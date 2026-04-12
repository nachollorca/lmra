from dataclasses import dataclass, field
from typing import Generator, Literal, TypeAlias

from lmdk import Message, UserMessage, complete
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Session

from .code import execute, validate
from .context import build


@dataclass
class State:
    session: Session = field(default_factory=Session)
    messages: list[Message] = field(default_factory=list)
    namespace: dict = field(default_factory=dict)


class Output(BaseModel):
    message: str
    code: str


LoopSignal: TypeAlias = Literal["COMPLETION", "VALIDATION", "EXECUTION"]
Event: TypeAlias = LoopSignal | Message


def run(
    state: State,
    schema: type[DeclarativeBase],
    model: str,
) -> Generator[Event, None, State]:
    """Execute the agentic loop.

    **yields** ``Event``: every intermediate assistant message and loop signal
    **returns** ``State``: full conversation, database snapshot and python namespace.

    An intermediate turn is one where the assistant message carries ``.code``;
    the loop ends as soon as the assistant responds without code.

    Args:
        state: Conversation, database state and python namespace (mutated in place).
        schema: SQLAlchemy declarative base that defines the db signature.
        model: Model identifier forwarded to ``complete()``.

    Yields:
        Each intermediate assistant ``Message`` and the current ``LoopSignal``

    Returns:
        The mutated ``State``.
    """
    system_instruction = build(session=state.session, base=schema)

    def _call() -> Generator[Event, None, Output]:
        """Single LM call."""
        yield "COMPLETION"
        response = complete(
            model=model,
            prompt=state.messages,
            system_instruction=system_instruction,
            output_schema=Output,
        )
        state.messages.append(response.message)
        yield response.message
        return response.output

    output = yield from _call()
    code = output.code

    while code:
        # --- validate ---------------------------------------------------
        yield "VALIDATION"
        is_valid, reason = validate(code=code, allowed_imports=None)
        if not is_valid:
            message = UserMessage(f"Code rejected: {reason}")
            state.messages.append(message)
            yield message

            output = yield from _call()
            code = output.code
            continue

        # --- execute ----------------------------------------------------
        yield "EXECUTION"
        result = execute(code=code, session=state.session, namespace=state.namespace)
        message = UserMessage(f"Execution result:\n{result}")
        state.messages.append(message)
        yield message

        output = yield from _call()
        code = output.code

    return state

from dataclasses import dataclass, field
from typing import Generator, Literal, TypeAlias

from lmdk import Message, UserMessage, complete
from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase, Session

from .code import execute, validate
from .context import build


@dataclass
class State:
    """Contains the different objects whose state is modified through the agentic loop.

    Attributes:
        db_session: the sqlalchemy database connection
        messages: the conversation history
        namespace: symbols of the code environment that the agent uses
    """

    db_session: Session = field(default_factory=Session)
    messages: list[Message] = field(default_factory=list)
    namespace: dict = field(default_factory=dict)


class Output(BaseModel):
    """Pydantic model to force the LM structured output."""

    message: str = Field(description="The response shown to the user.")
    code: str = Field(default="", description="The optional code to run.")


# Type aliases for convinience
LoopSignal: TypeAlias = Literal["COMPLETION", "VALIDATION", "EXECUTION"]
Event: TypeAlias = LoopSignal | Message


def run(
    state: State,
    db_schema: type[DeclarativeBase],
    model: str,
) -> Generator[Event, None, State]:
    """Execute the agentic loop.

    An intermediate turn is one where the assistant message requests to run ``.code``.
    The loop ends as soon as the assistant responds without code. Turn is returned to user.

    Args:
        state: Conversation, database state and python namespace (mutated in place).
        db_schema: SQLAlchemy declarative base that defines the db signature.
        model: Model identifier forwarded to ``complete()``.

    Yields:
        ``Event``: every intermediate assistant message and loop signal

    Returns:
        ``State``: possibly modified conversation, database snapshot and python namespace
    """
    system_instruction = build(db_session=state.db_session, db_schema=db_schema)

    def _call() -> Generator[Event, None, Output]:
        """Single LM call helper to avoid duplication in every completion."""
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
        yield "VALIDATION"
        is_valid, reason = validate(code=code, allowed_imports=None)
        if not is_valid:
            message = UserMessage(f"Code rejected: {reason}")
            state.messages.append(message)
            yield message
            output = yield from _call()
            code = output.code
            continue

        yield "EXECUTION"
        # If the namespace is empty, we should probably execute the first cell
        result = execute(
            code=code, db_session=state.db_session, namespace=state.namespace
        )
        message = UserMessage(f"Execution result:\n{result}")
        state.messages.append(message)
        yield message
        output = yield from _call()
        code = output.code

    return state

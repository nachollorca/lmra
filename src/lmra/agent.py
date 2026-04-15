"""Contains the agentic loop and related utils."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generator, TypeAlias

from lmdk import Message, UserMessage, complete
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from .code import execute, validate
from .context import _build_first_cell, build

MAX_LOOPS = 20


@dataclass
class State:
    """Contains the different objects whose state is modified through the agentic loop.

    Attributes:
        session: the sqlalchemy database connection
        messages: the conversation history
        namespace: symbols of the code environment that the agent uses
    """

    session: Session | None = None
    messages: list[Message] = field(default_factory=list)
    namespace: dict = field(default_factory=dict)


class Output(BaseModel):
    """Pydantic model to force the LM structured output."""

    message: str = Field(description="The response shown to the user.")
    code: str = Field(default="", description="The optional code to run.")


class Signal(StrEnum):
    """Signals emitted by the agentic loop to indicate current stage."""

    COMPLETION = "COMPLETION"
    VALIDATION = "VALIDATION"
    EXECUTION = "EXECUTION"
    EXCEEDED = "EXCEEDED"


Event: TypeAlias = Signal | Message


def _complete(
    state: State,
    model: str,
    system_instruction: str,
) -> Generator[Event, None, Output]:
    """Single LM call: append the response, yield signals and the message, return parsed output."""
    yield Signal.COMPLETION
    response = complete(
        model=model,
        prompt=state.messages,
        system_instruction=system_instruction,
        output_schema=Output,
    )
    state.messages.append(response.message)
    yield response.message
    return response.output


def _init_session(state: State, base: type[DeclarativeBase]) -> None:
    """Initialize the SQLAlchemy session when missing (first call)."""
    if state.session is None:
        engine = create_engine("sqlite://")
        base.metadata.create_all(engine)
        state.session = Session(engine)


def _init_namespace(state: State, base: type[DeclarativeBase]) -> None:
    """Bootstrap or refresh the code execution namespace.

    On the first call the namespace is empty, so a first cell is executed to
    populate imports and inject ``session``.  On follow-up calls the namespace
    already carries everything from the previous invocation; only ``session``
    is refreshed because the database may have changed between calls (user side).
    """
    if not state.namespace:
        first_cell = _build_first_cell(base=base)
        state.namespace["session"] = state.session
        execute(source=first_cell, namespace=state.namespace)
    else:
        state.namespace["session"] = state.session


def run(
    state: State,
    base: type[DeclarativeBase],
    model: str,
    allowed_imports: list[str] = [],
) -> Generator[Event, None, State]:
    """Execute the agentic loop.

    An intermediate turn is one where the assistant message requests to run ``.code``.
    The loop ends as soon as the assistant responds without code. Turn is returned to user.

    Args:
        state: Conversation, database state and python namespace (mutated in place).
        base: SQLAlchemy declarative base that defines the db schema.
        model: Model identifier forwarded to ``complete()``.
        allowed_imports: Any vanilla module or third-party package that the agent can use.

    Yields:
        ``Event``: every intermediate assistant message and loop signal.

    Returns:
        ``State``: possibly modified conversation, database snapshot and python namespace.
    """
    _init_session(state, base)
    _init_namespace(state, base)

    assert state.session is not None  # already initialized in _init_session
    system_instruction = build(session=state.session, base=base)

    output = yield from _complete(state, model, system_instruction)
    code = output.code

    loops = 0
    while code:
        if loops >= MAX_LOOPS:
            yield Signal.EXCEEDED
            break
        loops += 1

        yield Signal.VALIDATION
        if reason := validate(source=code, allowed_imports=allowed_imports):
            message = UserMessage(f"Code rejected: {reason}")
            state.messages.append(message)
            yield message
            output = yield from _complete(state, model, system_instruction)
            code = output.code
            continue

        yield Signal.EXECUTION
        result = execute(source=code, namespace=state.namespace)
        message = UserMessage(f"Execution result:\n{result}")
        state.messages.append(message)
        yield message
        output = yield from _complete(state, model, system_instruction)
        code = output.code

    return state

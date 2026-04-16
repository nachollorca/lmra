"""Contains the agentic loop and related utils."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generator, TypeAlias

from lmdk import Message, UserMessage, complete
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from .code import execute, validate
from .context import render
from .tools import Tool, make_disclose_fn

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


def _init_namespace(
    state: State,
    base: type[DeclarativeBase],
    tools: list[Tool],
) -> dict[str, str]:
    """Populate or refresh the agent code execution namespace.

    On the first call the namespace is empty, so all symbols are injected:
    ``session``, ORM model classes, tool functions, and ``disclose``.
    On follow-up calls only ``session`` is refreshed because the database
    may have changed between calls (user side).

    Returns:
        A ``{name: description}`` dict of every injected **infrastructure**
        symbol.  Tool symbols are excluded — their source of truth is the
        ``Tool`` object itself, rendered separately by ``_render_tools_summary``.
    """
    descriptions: dict[str, str] = {}

    state.namespace["session"] = state.session
    descriptions["session"] = "a `sqlalchemy.orm.Session` connected to the database."

    for cls in base.__subclasses__():
        state.namespace[cls.__name__] = cls
        descriptions[cls.__name__] = "ORM model class (see schema above)."

    for t in tools:
        state.namespace[t.name] = t.fn

    if tools:
        state.namespace["disclose"] = make_disclose_fn(tools)
        descriptions["disclose"] = (
            "`disclose(name: str) -> str` — prints the full signature"
            " and docstring of a tool. Call it before using a tool you haven't seen yet."
        )

    return descriptions


def run(
    state: State,
    base: type[DeclarativeBase],
    model: str,
    tools: list[Tool] = [],
    allowed_imports: list[str] = [],
) -> Generator[Event, None, State]:
    """Execute the agentic loop.

    An intermediate turn is one where the assistant message requests to run ``.code``.
    The loop ends as soon as the assistant responds without code. Turn is returned to user.

    Args:
        state: Conversation, database state and python namespace (mutated in place).
        base: SQLAlchemy declarative base that defines the db schema.
        model: Model identifier forwarded to ``complete()``.
        tools: User-provided tools the agent can call in generated code.
        allowed_imports: Any vanilla module or third-party package that the agent can use.

    Yields:
        ``Event``: every intermediate assistant message and loop signal.

    Returns:
        ``State``: possibly modified conversation, database snapshot and python namespace.
    """
    _init_session(state, base)
    descriptions = _init_namespace(state, base, tools)

    system_instruction = render(base=base, tools=tools, descriptions=descriptions)

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

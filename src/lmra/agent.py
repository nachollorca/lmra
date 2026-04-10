from dataclasses import dataclass, field
from typing import Generator

from lmdk import Message, UserMessage, complete
from sqlalchemy.orm import DeclarativeBase, Session

from .code import execute, validate
from .context import build


# I am not sure if we have enough reason to formalize a dataclass to hold these two
@dataclass
class State:
    # messages is clear, but we should also store the current snapshot of the database
    # i am not sure if it should be a path to sqlite
    # or a sqlalchemy session
    # or a dict with the serialized db made from database_manager.serialize
    # the main advantage of the serialization is that we could compute the diff between snapshots
    # effectively informing of additions / deletions / edits
    # but of course you need some time to serialize / compare / deserialize
    session: Session = field(default_factory=Session)
    messages: list[Message] = field(default_factory=list)


# I am not sure if this is the standard, maybe we could go with some typing.Literal for simplicity
class LoopSignal(Enum):
    LM_COMPLETION = auto()
    CODE_VALIDATION = (  # I am not sure if this is useful, it will always be quick, but can inform users
        auto()
    )
    CODE_EXECUTION = auto()


def run(
    state: State,
    base: type[  # this must match the database snapshot passed in state, should we check?
        DeclarativeBase
    ],
    model: str,
) -> Generator[  # Is there a vanilla python Iterator that we could use instead of typing.Generator?
    Message | LoopSignal, None, State
]:
    """Execute the agentic loop.

    The generator **yields**: every intermediate assistant message (suitable for
    streaming as Server-Sent Events) and loop signal (suitable to inform user of the state)
    and **returns** the mutated ``State`` containing the full conversation and the
    (possibly modified) database.

    An intermediate turn is one where the assistant message carries ``.code``;
    the loop ends as soon as the assistant responds without code.

    Args:
        state: Conversation and database state (mutated in place).
        base:  SQLAlchemy declarative base that defines the schema.
        model: Model identifier forwarded to ``complete()``.

    Yields:
        Each intermediate assistant ``Message`` and the current ``LoopSignal``

    Returns:
        The mutated ``State``.
    """
    yield LoopSignal.LM_COMPLETION
    system_instruction = build()
    response = complete(
        model=model, messages=state.messages, system_instruction=system_instruction
    )
    state.messages.append(response.message)

    # If the model answers directly (no code), return immediately.
    code = response.output.code
    if not code:
        return state

    # otherwise, yield the intermediate result and trigger agentic loop
    yield response.message

    while code:
        # --- validate ---------------------------------------------------
        yield LoopSignal.CODE_VALIDATION
        is_valid, reason = validate(code=code)
        if not is_valid:
            message = UserMessage(f"Code rejected: {reason}")
            state.messages.append(message)
            yield message

            yield LoopSignal.LM_COMPLETION
            response = complete(
                model=model,
                messages=state.messages,
                system_instruction=system_instruction,
            )
            state.messages.append(response.message)
            yield response.message
            continue

        # --- execute ----------------------------------------------------
        yield LoopSignal.CODE_EXECUTION
        result = execute(code=response.code, session=state.session)
        message = UserMessage(f"Execution result:\n{result}")
        state.messages.append(message)
        # I am not sure if it is a good idea to update the system_instruction every time we run code
        # Just in case the code actually did modify the database
        # But maybe it'd be weird to have a system instruction that contradicts some of the intermediate messages
        yield message

        yield LoopSignal.LM_COMPLETION
        response = complete(
            model=model, messages=state.messages, system_instruction=system_instruction
        )
        state.messages.append(response.message)
        code = response.output.code
        yield response.message

    # Loop exited -> last response has no code; it is the final answer.
    return state


# it feels like there is some duplication in the completion / message yielding / loop signal ...
# we might want to abstract some atomic helpers

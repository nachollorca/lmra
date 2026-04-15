"""Demo script that exercises lmra.agent.run and verifies DB side-effects."""

from base import Author, Base
from lmdk import UserMessage

from lmra.agent import Event, Signal, State, run

MODEL = "vertex:gemini-3-flash-preview"


def print_event(event: Event) -> None:
    """Pretty-print a Signal or Message coming from the agent loop."""
    if isinstance(event, Signal):
        print(f"\n>>> SIGNAL: {event.value}")
    else:
        # It's a Message (assistant or injected user message)
        print(event)


def main() -> None:
    state = State()

    # -- Turn 1: ask the agent to insert an author --------------------------
    state.messages.append(UserMessage("Add an author named 'Jorge Luis Borges' to the database."))

    print("=" * 60)
    print("TURN 1 — Insert an author")
    print("=" * 60)

    gen = run(state=state, base=Base, model=MODEL)
    try:
        while True:
            event = next(gen)
            print_event(event)
    except StopIteration as exc:
        state = exc.value

    # -- Verify the row was actually created --------------------------------
    authors = state.session.query(Author).filter_by(name="Jorge Luis Borges").all()
    assert len(authors) == 1, f"Expected 1 author, got {len(authors)}: {authors}"
    print(f"\n✅ Verification passed: {authors[0]}")

    # -- Turn 2: ask a query ------------------------------------------------
    state.messages.append(UserMessage("List all authors in the database."))

    print("\n" + "=" * 60)
    print("TURN 2 — Query authors")
    print("=" * 60)

    gen = run(state=state, base=Base, model=MODEL)
    try:
        while True:
            event = next(gen)
            print_event(event)
    except StopIteration as exc:
        state = exc.value

    print("\n✅ Demo finished successfully.")


if __name__ == "__main__":
    main()

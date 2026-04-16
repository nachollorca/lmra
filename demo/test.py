"""Demo script that exercises lmra.agent.run and verifies DB side-effects."""

from base import Author, Base
from lmdk import UserMessage

from lmra.agent import State, run

MODEL = "vertex:gemini-3-flash-preview"


def main() -> None:
    state = State()

    # -- Turn 1: ask the agent to insert an author --------------------------

    print("=" * 60)
    print("TURN 1 — Insert an author")
    print("=" * 60)
    state.messages.append(UserMessage("Add an author named 'Jorge Luis Borges' to the database."))
    gen = run(state=state, base=Base, model=MODEL)
    try:
        while True:
            event = next(gen)
            print(event, "\n")
    except StopIteration as exc:
        state = exc.value

    # -- Verify the row was actually created --------------------------------
    authors = state.session.query(Author).filter_by(name="Jorge Luis Borges").all()
    assert len(authors) == 1, f"Expected 1 author, got {len(authors)}: {authors}"
    print(f"\n✅ Verification passed: {authors[0]}")

    # -- Turn 2: ask a query ------------------------------------------------
    print("\n" + "=" * 60)
    print("TURN 2 — Query authors")
    print("=" * 60)
    state.messages.append(UserMessage("List all authors in the database."))
    gen = run(state=state, base=Base, model=MODEL)
    try:
        while True:
            event = next(gen)
            print(event, "\n")
    except StopIteration as exc:
        state = exc.value

    print("\n✅ Demo finished successfully.")


if __name__ == "__main__":
    main()

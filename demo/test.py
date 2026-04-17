"""Demo script that exercises lmra.agent.run with schema access and a tool."""

from fixtures import Author, Base, Book, get_author_catalog
from lmdk import UserMessage

from lmra.agent import State, run

MODEL = "vertex:gemini-3-flash-preview"

state = State()

# -- Turn 1: seed some data ---------------------------------------------

print("=" * 60)
print("TURN 1 — Insert authors and books")
print("=" * 60)
state.messages.append(
    UserMessage("Make authors Almudena Grandes and Rosa Montero and two books for each")
)
gen = run(state=state, base=Base, model=MODEL, tools=[get_author_catalog])
try:
    while True:
        event = next(gen)
        print(event, "\n")
except StopIteration as exc:
    state = exc.value

# -- Verify rows --------------------------------------------------------
authors = state.session.query(Author).all()
assert len(authors) == 2, f"Expected 2 authors, got {len(authors)}"
books = state.session.query(Book).all()
assert len(books) == 4, f"Expected 4 books, got {len(books)}"
print(f"\n✅ Verification passed: {len(authors)} authors, {len(books)} books")

# -- Turn 2: ask the model to use the tool ------------------------------

print("\n" + "=" * 60)
print("TURN 2 — Use format_catalog tool")
print("=" * 60)
state.messages.append(UserMessage("use the tool to get me the catalog from almudena"))
gen = run(state=state, base=Base, model=MODEL, tools=[get_author_catalog])
try:
    while True:
        event = next(gen)
        print(event, "\n")
except StopIteration as exc:
    state = exc.value

print("\n✅ Demo finished successfully.")

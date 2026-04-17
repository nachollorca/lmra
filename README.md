# lmra

Every new operation you want to allow a user to perform on your application's data model means new logic, a new screen. Feature development is the bottleneck: translating between what the user would like to do and the rigid paths your code allows.

`lmra` removes that layer. Hand an LM your ORM schema — the one you already have — and a sandboxed Python environment. It composes its own queries and transformations as code in a single turn. You do not need to define a thousand brittle GUIs for each possible action, nor a comprehensive but discrete set of tools for the LM to leverage. Users describe what they want from the application with natural language; the agent figures out how to make it happen.

---

## Whitepaper

### Tool calling hits a wall

The standard agentic pattern is function calling: define tools, let the LM pick one, read the result, repeat. This is clean and safe, but it doesn't scale.

Real applications have complex data models. To give the LM meaningful access you end up writing dozens of tools, each one crowding the context window. Every compound operation (filter, then aggregate, then compare) either needs its own dedicated tool or forces the agent to chain calls across multiple LM completions — slow and expensive. And you become the bottleneck: every new user need is a new tool to design, implement, test and document.

### Code as the action space

Research shows that letting LMs write and execute code instead of picking from a discrete set of tools produces stronger agents[1](https://arxiv.org/abs/2402.01030)[2](https://arxiv.org/pdf/2401.00812)[3](https://arxiv.org/pdf/2411.01747). Code gives the model composition (chain operations in one turn), control flow (loops, conditionals, error handling), and self-extension (define helper functions that persist in the namespace). A single code block can do what would otherwise take a long chain of tool calls.

But code execution alone doesn't solve the data access problem. The LM still needs some interface to read and modify application state. You're back to writing wrapper functions — unless the right abstraction already exists.

### Relational algebra is the interface you don't have to build

And it does. Relational algebra is a solved discipline: decades of refinement behind optimal ways of organizing and querying structured data. SQL databases implement it. ORMs like SQLAlchemy wrap it in the same Python the LM is already writing.

By placing an ORM session and the model classes in the agent's execution namespace, `lmra` gives the LM full, structured access to the data without a single hand-crafted tool. The developer defines the schema once — which they'd do anyway. The LM handles everything else.

### What this means for applications

Traditional software requires two layers of work on top of the data model:

1. **Business logic** (backend) — functions and endpoints for every operation users might need.
2. **UI workflows** (frontend) — screens, forms and click sequences to expose those operations.

Both layers grow with the complexity of the data model and the operations pipelines that we want to allow for the user.

With `lmra`, the developer defines the schema and optionally a handful of tools for things that genuinely require custom logic (sending emails, calling external APIs, very complex workflows). Everything else — every query, every data transformation, every "find all X where Y and then update Z" — the LM composes on the fly.

For users, this replaces navigating menus and filling forms with describing what they want. It removes the mismatch between what the user is thinking and the rigid paths a GUI offers.

### Beyond file systems

Today's coding agents (Opencode, Pi, Claude Code) prove that LMs can navigate file structures effectively with tools as simple as `bash`, `read`, `write` and `edit`. But file systems are structurally simple: trees of named nodes with blob contents.

Application data is a different beast. Dozens of entity types, foreign keys, many-to-many relationships, constraints, cascading dependencies. Relational data is orders of magnitude richer than a directory tree. The ORM gives the LM the right abstraction: it thinks in terms of entities, relationships and queries rather than raw files.

---

## Use

### Install
`uv add lmra`

### Usage
[here some minimal example of how to set up the mandatory inputs (the declarative base...) and get the streamed events from the `agent.run` function.
We could include some expanders as in `lmdk/README.md` for examples of other moving parts at the discretion of the user]
...

### How it works
In short: **chat → LM generates SQLAlchemy code → validate → execute → return results → repeat until done**.

1. **Schema as context** (`context.py`): The source code of your ORM classes is extracted via `inspect.getsource` and rendered into a Jinja system prompt alongside available symbols and tools.

2. **Agentic loop** (`agent.py`): The LM produces structured output — a message and optional Python code. If code is present, it's validated, executed, and the result is fed back as a user message. The loop continues until the LM responds without code or hits 20 iterations.

3. **Sandboxed execution** (`code.py`): An AST pass blocks dangerous builtins (`exec`, `eval`, `open`…), forbidden modules (`os`, `subprocess`…), dangerous dunder access, and enforces an import whitelist. Safe code runs in a persistent namespace with stdout captured.

4. **Optional tools** (`tools.py`): Developers can register custom functions with the `@tool` decorator. Only tool names and one-liners appear in the prompt — the LM calls `disclose(name)` to see full signatures on demand, keeping the context window lean.

---

## Development

### Structure
```
src/lmdk/
├── agent.py      # Entrypoint for the agentic loop
├── code.py       # Sandboxed python env on which to run the agent requested code
├── context.py    # Utils to engineer the context passed to the agent
├── datbase.py    # Utils that access or modify the database
├── prompt.jinja  # Default system instruction template
└── tools.py      # Logic to expose functions to the model
```

### Tooling
We use `just` for development tasks. Use:
- `just sync`: Updates lockfile and syncs environment.
- `just format`: Lints and formats with `ruff`.
- `just check-types`: Static analysis with `ty`.
- `just analyze-complexity`: Cyclomatic complexity checks with `complexipy`.
- `just test`: Runs pytest with 90% coverage threshold.

### Contribute
1. **Hooks**: Install pre-commit hooks via `just install-hooks`. PRs will fail CI if linting/formatting is not applied.
2. **Issues**: Open an issue first using the default template.
3. **PRs**: Link your PR to the relevant issue using the PR template.

---

## License
MIT

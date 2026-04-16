# Language Model Relational Agent

**`lmra`** is a **code-executing LLM agent for querying/modifying SQLAlchemy databases**.

**What it does:** Given a SQLAlchemy database schema, it lets a user chat with an LLM that can write and execute Python/SQLAlchemy code against the database to answer questions or perform mutations.

**How it works:**

1. **Context setup** (`context.py`): Inspects ORM classes (marked `__show__ = True`) via `inspect.getsource`, renders a Jinja system prompt (`prompt.jinja`) containing the schema and a bootstrap code cell (imports + `session`).

2. **Agentic loop** (`agent.py`): Uses structured output (`Output` = message + optional code). If the LLM returns code, it validates → executes → feeds the result back as a user message → calls the LLM again. Loops until the LLM responds without code (or hits 20 iterations).

3. **Sandboxed execution** (`code.py`): AST-validates code against forbidden builtins (`exec`, `eval`, `open`…), forbidden modules (`os`, `subprocess`…), forbidden dunder attributes, and an import whitelist. Safe code is `exec()`'d in a persistent namespace with stdout captured.

In short: **chat → LLM generates SQLAlchemy code → validate → execute → return results → repeat until done**.

"""Contains the utils to engineer the context passed to the agent."""

import inspect
from pathlib import Path

from lmdk import render_template
from sqlalchemy.orm import DeclarativeBase

from .tools import Tool

_TEMPLATE_PATH = Path(__file__).parent / "prompt.jinja"


def _render_schema_source(base: type[DeclarativeBase]) -> str:
    """Return the source code of ORM classes for the LM prompt.

    Extracts source code via ``inspect.getsource`` for every mapped class
    registered under *base*.  The sources are concatenated separated by
    blank lines.
    """
    sources = [inspect.getsource(cls) for cls in base.__subclasses__()]
    return "\n\n".join(sources)


def _render_symbols(descriptions: dict[str, str]) -> str:
    """Format the symbol descriptions dict as a Markdown bullet list.

    Args:
        descriptions: ``{name: description}`` as returned by ``_init_namespace``.

    Returns:
        A Markdown-formatted bullet list.
    """
    return "\n".join(f"- `{name}`: {desc}" for name, desc in descriptions.items())


def _render_tools_summary(tools: list[Tool]) -> str:
    """Render name + one-liner for each tool.

    This summary is shown in the system prompt.  The agent can call
    ``disclose(name)`` to see full details.

    Args:
        tools: User-provided tools registered for this run.

    Returns:
        A Markdown-formatted bullet list, or empty string if no tools.
    """
    if not tools:
        return ""
    return "\n".join(f"- `{t.name}`: {t.short_description}" for t in tools)


def render(
    base: type[DeclarativeBase],
    tools: list[Tool],
    descriptions: dict[str, str],
) -> str:
    """Build the system instruction for the LM with all context parts.

    Args:
        base: The declarative base describing the schema.
        tools: User-provided tools registered for this run.
        descriptions: ``{name: description}`` of every namespace symbol,
            as returned by ``_init_namespace`` in ``agent.py``.
    """
    return render_template(
        path=str(_TEMPLATE_PATH),
        SCHEMA=_render_schema_source(base=base),
        SYMBOLS=_render_symbols(descriptions),
        TOOLS=_render_tools_summary(tools),
    )

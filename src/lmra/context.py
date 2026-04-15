"""Contains the utils to engineer the context passed to the agent."""

import inspect
from pathlib import Path

from lmdk import render_template
from sqlalchemy.orm import DeclarativeBase

_TEMPLATE_PATH = Path(__file__).parent / "prompt.jinja"


def _shown_classes(base: type[DeclarativeBase]) -> list[type]:
    """Return mapped classes where ``__show__`` is True."""
    return [cls for cls in base.__subclasses__() if getattr(cls, "__show__", False)]


def _render_schema_source(base: type[DeclarativeBase]) -> str:
    """Return the source code of shown ORM classes for the LM prompt.

    Iterates mapped classes with ``__show__ == True`` and extracts their
    source code via ``inspect.getsource``.  The sources are concatenated
    separated by blank lines.
    """
    sources = [inspect.getsource(cls) for cls in _shown_classes(base)]
    return "\n\n".join(sources)


def _render_table_imports(base: type[DeclarativeBase]) -> str:
    """Return ``from <module> import <Class>, ...`` lines for shown tables.

    Groups classes by their defining module so a single import line is
    produced per module.
    """
    by_module: dict[str, list[str]] = {}
    for cls in _shown_classes(base):
        module = cls.__module__
        by_module.setdefault(module, []).append(cls.__name__)
    lines = [f"from {mod} import {', '.join(names)}" for mod, names in by_module.items()]
    return "\n".join(lines)


def render_bootstrap_code(base: type[DeclarativeBase]) -> str:
    """Build the first cell that is auto-executed in the agent namespace.

    Includes ORM table imports and the essential SQLAlchemy import for
    ``session`` (which is injected into the namespace externally).
    """
    lines = [
        "from sqlalchemy.orm import Session",
        _render_table_imports(base=base),
    ]
    return "\n".join(lines)


def render(base: type[DeclarativeBase], first_cell: str) -> str:
    """Build the system prompt.

    Args:
        base: The declarative base describing the schema.
        first_cell: Pre-computed first cell string (shown verbatim in the prompt).
    """
    prompt = render_template(
        path=str(_TEMPLATE_PATH),
        SCHEMA=_render_schema_source(base=base),
        FIRST_CELL=first_cell,
    )
    return prompt

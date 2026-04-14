from lmdk import render_template
from sqlalchemy.orm import DeclarativeBase, Session

from .database import overview, schema_text, table_imports


def _build_first_cell(base: type[DeclarativeBase]) -> str:
    """Builds the first cell that will always be executed."""
    imports = table_imports(base=base)
    # here we have to import session from sqlalchemy, the engine, etc.
    raise NotImplementedError


def build(session: Session, base: type[DeclarativeBase]) -> str:
    """Builds the system prompt."""
    prompt = render_template(
        path="prompt.jinja",
        SCHEMA=schema_text(base=base),
        OVERVIEW=overview(session=session),
        FIRST_CELL=_build_first_cell(base=base),
    )
    return prompt

from lmdk import render_template
from sqlalchemy.orm import DeclarativeBase, Session

from .database import get_overview, get_schema, get_table_imports


def _build_first_cell(db_schema: type[DeclarativeBase]) -> str:
    """Builds the first cell that will always be executed."""
    table_imports = get_table_imports(db_schema=db_schema)
    # here we have toimport session from sqlalchemy, the engine, etc.
    raise NotImplementedError


def build(db_session: Session, db_schema: type[DeclarativeBase]) -> str:
    """Builds the system prompt."""
    prompt = render_template(
        path="prompt.jinja",
        SCHEMA=get_schema(db_schema=db_schema),
        OVERVIEW=get_overview(db_session=db_session),
        FIRST_CELL=_build_first_cell(db_schema=db_schema),
    )
    return prompt

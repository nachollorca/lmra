from lmdk import render_template
from sqlalchemy.orm import DeclarativeBase, Session


def build(session: Session, base: type[DeclarativeBase]) -> str:
    """Builds the system prompt."""
    prompt = render_template(
        path="prompt.jinja", SCHEMA=..., SNAPSHOT=..., FIRST_CELL=...
    )
    raise NotImplementedError
    return prompt

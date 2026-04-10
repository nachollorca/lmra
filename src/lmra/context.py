from sqlalchemy.orm import DeclarativeBase, Session


def build(session: Session, base: type[DeclarativeBase]) -> str:
    """Builds the system prompt."""
    raise NotImplementedError

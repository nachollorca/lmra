from sqlalchemy.orm import DeclarativeBase, Session


def deserialize(data: dict[str, list[dict]], base: type[DeclarativeBase]) -> Session:
    """Unpack a JSON-serialised database state into an SQLAlchemy session.

    Creates an in-memory SQLite database, issues ``Base.metadata.create_all``,
    and populates every table from *data*.

    Args:
        data: Mapping of ``{table_name: [row_dict, ...]}``.
        base: The declarative base whose metadata describes the schema.

    Returns:
        A ready-to-use SQLAlchemy ``Session`` bound to the in-memory database.
    """
    raise NotImplementedError


def serialize(session: Session, base: type[DeclarativeBase]) -> dict[str, list[dict]]:
    """Freeze the current database state into a JSON-serialisable dict.

    Args:
        session: The active session to read from.
        base:    The declarative base whose metadata describes the schema.

    Returns:
        ``{table_name: [row_dict, ...]}`` for every table in the schema.
    """
    raise NotImplementedError

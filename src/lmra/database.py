from sqlalchemy.orm import DeclarativeBase, Session


def deserialize(
    data: dict[str, list[dict]], base: type[DeclarativeBase]
) -> Session:
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


def serialize(
    session: Session, base: type[DeclarativeBase]
) -> dict[str, list[dict]]:
    """Freeze the current database state into a JSON-serialisable dict.

    Args:
        session: The active session to read from.
        base: The declarative base whose metadata describes the schema.

    Returns:
        ``{table_name: [row_dict, ...]}`` for every table in the schema.
    """
    raise NotImplementedError


def overview(session: Session) -> str:
    """Inspects the database state and returns a string summarizing it for the LM.

    Return extra information for tables with attribute ``__overview__`` set to ``True``"""
    raise NotImplementedError


def schema_text(base: type[DeclarativeBase]) -> str:
    """Returns a string for the LM showing the Tables and Relationships conforming the database.

    It only shows tables where attribute ``__show__`` is set to True."""
    raise NotImplementedError


def table_imports(base: type[DeclarativeBase]) -> str:
    """Returns the ORM tables in ``from [module] import tables``.

    It only shows tables where attribute ``__show__`` is set to True."""
    raise NotImplementedError

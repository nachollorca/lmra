"""Contains the utilities that access or modify the database."""

from sqlalchemy import create_engine
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
    engine = create_engine("sqlite://")
    base.metadata.create_all(engine)
    session = Session(engine)

    # Build a lookup from table name to mapped class
    cls_by_table: dict[str, type] = {}
    for cls in base.__subclasses__():
        table_name = cls.__tablename__ if hasattr(cls, "__tablename__") else cls.__table__.name
        cls_by_table[table_name] = cls

    for table_name, rows in data.items():
        cls = cls_by_table.get(table_name)
        if cls is None:
            continue
        for row in rows:
            session.add(cls(**row))

    session.commit()
    return session


def serialize(session: Session, base: type[DeclarativeBase]) -> dict[str, list[dict]]:
    """Freeze the current database state into a JSON-serialisable dict.

    Args:
        session: The active session to read from.
        base: The declarative base whose metadata describes the schema.

    Returns:
        ``{table_name: [row_dict, ...]}`` for every table in the schema.
    """
    result: dict[str, list[dict]] = {}
    for cls in base.__subclasses__():
        table_name = cls.__tablename__ if hasattr(cls, "__tablename__") else cls.__table__.name
        columns = [c.key for c in cls.__table__.columns]
        rows = session.query(cls).all()
        result[table_name] = [{col: getattr(row, col) for col in columns} for row in rows]
    return result

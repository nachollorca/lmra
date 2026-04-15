"""Dummy declarative base with two related tables for demo/testing purposes."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base."""


class Author(Base):
    """An author who can write many books."""

    __tablename__ = "authors"
    __show__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))

    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    """A book belonging to a single author."""

    __tablename__ = "books"
    __show__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    author: Mapped["Author"] = relationship(back_populates="books")

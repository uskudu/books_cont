import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, ForeignKey, String, TIMESTAMP
from sqlalchemy.sql import func

from app.schemas.user import BookOwnedSchema
from app.schemas.user import UserActionsGetSchema
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


user_books_table = Table(
    "user_books",
    Base.metadata,
    Column(
        "user_id", ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    ),
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    author: Mapped[str] = mapped_column(nullable=False, index=True)
    genre: Mapped[str]
    year: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str]
    price: Mapped[int] = mapped_column(nullable=False, index=True)
    times_bought: Mapped[int] = mapped_column(default=0)
    times_returned: Mapped[int] = mapped_column(default=0)
    rating: Mapped[float] = mapped_column(default=0)

    buyers: Mapped[list["User"]] = relationship(
        secondary=user_books_table, back_populates="bought_books"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "year": self.year,
            "description": self.description,
            "price": self.price,
            "times_bought": self.times_bought,
            "times_returned": self.times_returned,
            "rating": self.rating,
        }


class Admin(Base):
    __tablename__ = "admins"
    admin_id: Mapped[str] = mapped_column(
        unique=True, primary_key=True, default=str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="admins")

    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "username": self.username,
            "role": self.role,
        }


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(
        unique=True, primary_key=True, default=str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="user")
    money: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(default=True)  # False if deleted

    bought_books: Mapped[list["Book"]] = relationship(
        secondary=user_books_table, back_populates="buyers"
    )

    user_actions: Mapped[list["UserActions"]] = relationship(back_populates="user")

    # def for_admin(self): pass
    def to_dict(self):
        owned_books = [
            BookOwnedSchema(
                title=book.title,
                author=book.author,
                genre=book.genre,
                year=book.year,
                description=book.description,
                price=book.price,
                times_bought=book.times_bought,
                times_returned=book.times_returned,
                rating=book.rating,
            )
            for book in self.bought_books
        ]
        actions_history = [
            UserActionsGetSchema(
                user_id=action.user_id,
                action_type=action.action_type,
                details=action.details,
                total=action.total,
                timestamp=action.timestamp,
            )
            for action in self.user_actions
        ]
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "money": self.money,
            "bought_books": owned_books,
            "actions_history": actions_history,
            "active": self.active,
        }


class UserActions(Base):
    __tablename__ = "user_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.user_id"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(nullable=False)
    details: Mapped[str] = mapped_column(nullable=False)
    total: Mapped[int] = mapped_column(nullable=True)
    timestamp: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="user_actions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "details": self.details,
            "total": self.total,
            "timestamp": self.timestamp,
        }

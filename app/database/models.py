from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import Index, String, DateTime, ForeignKey, Numeric, Boolean, Integer, func
from typing import Optional, List
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    """Базовый класс для всех моделей с id"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    wishlists: Mapped[List["WishlistModel"]] = relationship(back_populates="user")


class GameModel(BaseModel):
    __tablename__ = "games"

    title: Mapped[str] = mapped_column(String)
    external_id: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    wishlists: Mapped[List["WishlistModel"]] = relationship(back_populates="game")
    price_history: Mapped[List["PriceHistoryModel"]] = relationship(back_populates="game")


class WishlistModel(BaseModel):
    __tablename__ = "wishlists"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    target_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    user: Mapped["UserModel"] = relationship(back_populates="wishlists")
    game: Mapped["GameModel"] = relationship(back_populates="wishlists")

    __table_args__ = (
        Index('ix_wishlist_user_game', 'user_id', 'game_id', unique=True),
    )


class PriceHistoryModel(BaseModel):
    __tablename__ = "price_history"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    game: Mapped["GameModel"] = relationship(back_populates="price_history")

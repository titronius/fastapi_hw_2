import datetime
import uuid

from settings import PG_DSN
from sqlalchemy import UUID, Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, Table, UniqueConstraint, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from data_types import FieldStr

engine = create_async_engine(
    PG_DSN,
)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):

    @property
    def id_dict(self):
        return {"id": self.id}
    
role_rights = Table(
    "role_rights_relation",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), index=True),
    Column("right_id", ForeignKey("right.id"), index=True)
)


user_roles = Table(
    "user_roles_relation",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), index=True),
    Column("user_id", ForeignKey("advertisement_user.id"), index=True)
)


class Right(Base):
    __tablename__ = "right"
    _model = "right"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    write: Mapped[bool] = mapped_column(Boolean, default=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    only_own: Mapped[bool] = mapped_column(Boolean, default=True)
    model: Mapped[FieldStr] = mapped_column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("model", "only_own", "read", "write"),
        CheckConstraint("model in ('user', 'advertisement', 'token', 'right', 'role')")
    )

class Role(Base):
    __tablename__ = "role"
    _model = "role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    rights: Mapped[list[Right]] = relationship(secondary=role_rights)
    
class Advertisement(Base):
    __tablename__ = "advertisement"
    _model = "advertisement"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("advertisement_user.id"))
    user: Mapped["User"] = relationship("User", lazy="joined", back_populates="advertisements")
    
    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author": self.author,
            "created_at": self.created_at.isoformat()
        }
        
class User(Base):
    __tablename__ = "advertisement_user"
    _model = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(72), nullable=False)
    tokens: Mapped[list["Token"]] = relationship("Token", lazy="joined", cascade="delete", back_populates="user")
    advertisements: Mapped[list["Advertisement"]] = relationship("Advertisement", lazy="joined", back_populates="user")
    roles: Mapped[list[Role]] = relationship(Role, secondary=user_roles, lazy="joined")

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "roles": [role.id for role in self.roles],
            "advertisements": [advertisement.id for advertisement in self.advertisements]
        }

class Token(Base):
    __tablename__ = "token"
    _model = "token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(
        UUID, server_default=func.gen_random_uuid(), unique=True
    )
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("advertisement_user.id"))
    user: Mapped[User] = relationship(User, lazy="joined", cascade="delete", back_populates="tokens")


    @property
    def dict(self):
        return {
            "token": self.token
        }


ORM_OBJECT = Advertisement | User | Token | Role | Right
ORM_CLS = type[Advertisement] | type[User] | type[Token] | type[Role] | type[Right]
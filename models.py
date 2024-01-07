from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    email = Column(String)
    hashed_password = Column(String)


class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

from pydantic import BaseModel, Field
from typing import Optional


class TodoRequestSchema(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: Optional[bool] = False


class UsersDetailsSchema(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    email: str
    password: str
    role: str

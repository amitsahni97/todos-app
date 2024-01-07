from pydantic import BaseModel, Field, model_validator
from typing import Optional


class TodoRequestSchema(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: Optional[bool] = False


class UpdateUserDetails(BaseModel):
    user_name: Optional[str] = Field(None, min_length=4, max_length=25)
    email: Optional[str] = Field(None, min_length=5, max_length=50)
    password: Optional[str] = Field(None, min_length=4, max_length=25)

    @model_validator(mode='after')
    def verify_details(self):
        email = self.email
        password = self.password
        if not email and not password and not self.user_name:
            raise ValueError("No data provided to update")
        return self


class UsersDetailsSchema(BaseModel):
    user_name: str = Field(min_length=4, max_length=25, description="This is user name")
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=4, max_length=25)

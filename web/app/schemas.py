from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, AnyHttpUrl, BaseModel, EmailStr, validator


class ObjectCreateInfo(BaseModel):
    file_name: str
    object_name: str


class PostResponce(BaseModel):
    user: str
    user_objects: List[ObjectCreateInfo]


class ObjectGetInfo(BaseModel):
    object_name: str
    download_url: AnyHttpUrl
    registration_date: datetime


class GetResponce(BaseModel):
    objects: List[ObjectGetInfo]


class Message(BaseModel):
    message: str


class CreateUserRequest(BaseModel):
    user_name: str
    first_name: str
    second_name: str
    email: EmailStr | None = None
    password: str


class CreateUserResponse(BaseModel):
    user_name: str
    id: UUID4
    created_at: datetime


class MutableUserDataInDB(BaseModel):
    first_name: Optional[str]
    second_name: Optional[str]
    email: Optional[str]
    disabled: Optional[bool]
    user_role: Optional[str]

    @validator("first_name")
    def first_name_string(cls, v):
        assert v.isalpha(), "must be string"
        return v

    @validator("second_name")
    def second_name_string(cls, v):
        assert v.isalpha(), "must be string"
        return v

    class Config:
        orm_mode = True


class StaticUserDataInDB(MutableUserDataInDB):
    id: UUID4
    user_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserPass(StaticUserDataInDB):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

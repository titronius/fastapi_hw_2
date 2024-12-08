import datetime
from typing import Literal
import uuid

from pydantic import BaseModel

class IdResponse(BaseModel):
    id: int
    
class Status(BaseModel):
    status: Literal["success"]

class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: float
    author: str
    
class CreateAdvertisementResponse(IdResponse):
    pass
    
class GetAdvertisementResponse(BaseModel):
    title: str
    description: str
    price: float
    author: str
    created_at: datetime.datetime
    
class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str| None = None
    price: float| None = None
    author: str| None = None
    
class UpdateUserRequest(BaseModel):
    name: str | None = None
    password: str| None = None
    
class GetAdvertisementsRequest(UpdateAdvertisementRequest):
    pass

class UpdateAdvertisementResponse(IdResponse):
    pass

class DeleteAdvertisementResponse(Status):
    pass

class BaseUserRequest(BaseModel):
    name: str
    password: str

    
class CreateUserRequests(BaseUserRequest):
    pass

class GetUserResponse(BaseModel):
    id: int
    name: str
    roles: list
    advertisements: list

class UpdateUserResponse(IdResponse):
    pass

class DeleteUserResponse(Status):
    pass

class CreateUserResponse(IdResponse):
    pass

class LoginRequest(BaseUserRequest):
    pass

class LoginResponse(BaseModel):
    token: uuid.UUID
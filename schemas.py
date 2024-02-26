from pydantic import BaseModel


class UserGetSchema(BaseModel):
    id:int
    name : str
    email: str
    password : str


class UserPostSchema(BaseModel):
    name : str
    email: str
    password : str

class UserUpdateSchema(BaseModel):
    name : str
    password : str


class Token(BaseModel):
    access_token : str
    token_type : str
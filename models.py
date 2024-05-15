from fastapi import UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional  # Import Optional from typing module


class User(BaseModel):
    user_id: int = Field(None, description="The user id")
    phone: str = Field(None, description="The phone of the user")
    role: str = Field(None, description="The role of the user 'admin', 'store_user', 'user'")
    password: Optional[str] = Field(None, description="The password of the user")
    name: str = Field(None, description="The name of the user")
    is_owner: Optional[bool] = Field(False, description="The user is the owner of the store")
    store_name: Optional[str] = Field(None, description="The name of the store")
    access_token: Optional[str] = Field(None, description="The access token of the user")


class UserUpdate(BaseModel):
    user_id: int = Field(None, description="The user id")
    name: str = Field(None, description="The name of the user")
    store_id: int = Field(None, description="The store id")
    role: str = Field(None, description="The role of the user 'admin', 'store_user', 'user'")
    password: Optional[str] = Field(None, description="The password of the user")


class UserIn(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    username: str


class UserInDB(UserIn):
    hashed_password: str


class RegisterUser(BaseModel):
    phone: str = Field(None, description="The phone of the user")
    role: str = Field(None, description="The role of the user 'admin', 'store_user', 'user'")
    name: str = Field(None, description="The name of the user")
    store_id: Optional[int] = Field(default=None, description="The store id (optional)")


class Store(BaseModel):
    id: int = Field(None, description="The store id")
    name: str = Field(None, description="The name of the store")
    address: str = Field(None, description="The address of the store")
    phone: str = Field(None, description="The phone of the store")
    user_list: Optional[list] = Field(None, description="The user list of the store")


# class StoreUpdate(BaseModel):
#     id: int = Field(None, description="The store id")
#     name: str = Field(None, description="The name of the store")
#     address: str = Field(None, description="The address of the store")
#     phone: str = Field(None, description="The phone of the store")
# user_list: Optional[list] = Field(None, description="The user list of the store")


class StoreIn(BaseModel):
    id: int = Field(None, description="The store id")
    name: str = Field(None, description="The name of the store")
    address: str = Field(None, description="The address of the store")
    phone: str = Field(None, description="The phone of the store")
    # user_list: Optional[list] = Field(None, description="The user list of the store")


class RemoveOrAddUserInStore(BaseModel):
    store_id: int = Field(None, description="The store id")
    user_list: list = Field(None, description="The user id list")


class SetUserStore(BaseModel):
    store_id: int = Field(None, description="The store id")
    user_id: int = Field(None, description="The user id")
    is_set: bool = Field(True, description="Set or remove the user from the store")


class RawMaterialIn(BaseModel):
    name: str = Field(None, description="The name of the raw material")
    unit: str = Field(None, description="The unit of the raw material")
    image_data: UploadFile = File(description="Image file for the raw material")

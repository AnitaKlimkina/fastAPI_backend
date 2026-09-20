from pydantic import BaseModel, Field, ConfigDict


class BaseResponse(BaseModel):
    result: bool


class FollowersResponse(BaseModel):
    id: int = Field(..., validation_alias="id_user")
    name: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class FollowingResponse(BaseModel):
    id: int = Field(..., validation_alias="id_user")
    name: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserResponse(BaseModel):
    id: int = Field(..., validation_alias="id_user")
    name: str
    followers: list[FollowersResponse]
    following: list[FollowingResponse]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AboutUserResponse(BaseResponse):
    user: UserResponse


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


class MediaResponse(BaseResponse):
    media_id: int


class TweetResponse(BaseResponse):
    tweet_id: int


class TweetAuthorResponse(BaseModel):
    id: int = Field(..., validation_alias="id_user")
    name: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TweetLikeResponse(BaseModel):
    user_id: int = Field(..., validation_alias="id_user")
    name: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TweetItemResponse(BaseModel):
    id: int
    content: str
    attachments: list[str]
    author: TweetAuthorResponse
    likes: list[TweetLikeResponse]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AllTweetsResponse(BaseResponse):
    tweets: list[TweetItemResponse]


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids:list[int] = []


class LikeCreate(BaseResponse):
    id_user: int
    id_tweet: int
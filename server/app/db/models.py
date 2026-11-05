from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table, UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""


USERS_ID_FK = "users.id_user"
USERS_TABLE = "Users"
TWEETS_TABLE = "Tweets"
TWEETS_ID_FK = "tweets.id_tweet"
TWEETS_ATTR = "tweets"

followers = Table("followers", Base.metadata,
                  Column(
                      "follower_id",
                      Integer,
                      ForeignKey(USERS_ID_FK),
                      primary_key=True),
                  Column(
                      "followed_id",
                      Integer,
                      ForeignKey(USERS_ID_FK),
                      primary_key=True))


class Users(Base):
    __tablename__ = "users"
    id_user = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    tweets = relationship(TWEETS_TABLE, back_populates="authors",
                          cascade="all, delete-orphan")
    following = relationship(
        USERS_TABLE,
        secondary=followers,
        primaryjoin="Users.id_user==followers.c.follower_id",
        secondaryjoin="Users.id_user==followers.c.followed_id",
        back_populates="followers",
    )
    followers = relationship(
        USERS_TABLE,
        secondary=followers,
        primaryjoin="Users.id_user==followers.c.followed_id",
        secondaryjoin="Users.id_user==followers.c.follower_id",
        back_populates="following",
    )

    likes = relationship("Likes", back_populates="users")


class Tweets(Base):
    __tablename__ = TWEETS_ATTR
    id_tweet = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)  # noqa: WPS110
    id_author = Column(Integer, ForeignKey(USERS_ID_FK))

    media = relationship(
        "Media",
        back_populates=TWEETS_ATTR,
        cascade="all, delete-orphan")
    authors = relationship(USERS_TABLE, back_populates=TWEETS_ATTR)
    likes = relationship("Likes", back_populates=TWEETS_ATTR)


class Media(Base):
    __tablename__ = "media"
    id_media = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    id_tweet = Column(Integer, ForeignKey(TWEETS_ID_FK))

    tweets = relationship(TWEETS_TABLE, back_populates="media")


class Likes(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint(
        "id_user", "id_tweet", name="unique_user_tweet_like"),)
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey(USERS_ID_FK), nullable=False)
    id_tweet = Column(Integer, ForeignKey(TWEETS_ID_FK))

    users = relationship(USERS_TABLE, back_populates="likes")
    tweets = relationship(TWEETS_TABLE, back_populates="likes")

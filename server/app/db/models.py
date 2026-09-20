from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

followers = Table("followers", Base.metadata,
                  Column("follower_id", Integer, ForeignKey("users.id_user"), primary_key=True),
                  Column("followed_id", Integer, ForeignKey("users.id_user"), primary_key=True))


class Users(Base):
    __tablename__ = "users"
    id_user = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    tweets = relationship("Tweets", back_populates="authors",
                          cascade="all, delete-orphan")

    following = relationship(
        "Users",
        secondary=followers,
        primaryjoin="Users.id_user==followers.c.follower_id",
        secondaryjoin="Users.id_user==followers.c.followed_id",
        backref="followers",
    )

    likes = relationship("Likes", back_populates="users")
    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Tweets(Base):
    __tablename__ = "tweets"
    id_tweet = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    id_author = Column(Integer, ForeignKey("users.id_user"))

    media = relationship("Media", back_populates="tweets", cascade="all, delete-orphan")
    authors = relationship("Users", back_populates="tweets")
    likes = relationship("Likes", back_populates="tweets")

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Media(Base):
    __tablename__ = "media"
    id_media = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    id_tweet = Column(Integer, ForeignKey("tweets.id_tweet"))

    tweets = relationship("Tweets", back_populates="media")
    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_tweet = Column(Integer, ForeignKey("tweets.id_tweet"))

    users = relationship("Users", back_populates="likes")
    tweets = relationship("Tweets", back_populates="likes")


    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


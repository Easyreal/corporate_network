import os

from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, backref

engine = create_engine(os.getenv("POSTGRES_URL"), echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    another_info = Column(String, nullable=True, default=None)
    api_key = Column(String, nullable=False)

    subscriptions = relationship("Subscriptions", backref="users", lazy='joined')
    subscribers = relationship("Subscribers", backref="users", lazy='joined')


class Subscriptions(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subscription_id = Column(Integer, nullable=False)


class Subscribers(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subscriber_id = Column(Integer, nullable=False)


class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    tweet_id = Column(Integer, ForeignKey('tweets.id', ondelete="CASCADE"))

    tweet = relationship('Tweets', backref='likes', lazy='joined')
    user = relationship("Users", backref='likes', lazy="joined")
    __table_args__ = (UniqueConstraint("user_id", "tweet_id", name="unique_user_tweet"),)

class Tweets(Base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    tweet_data = Column(String, nullable=False)
    tweet_media_ids = Column(ARRAY(Integer), server_default="{}")
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    author = relationship("Users", backref=backref("tweets", lazy='joined', cascade="all,delete"))

class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    path = Column(String(255))

def init_db():
    # time.sleep(5)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()

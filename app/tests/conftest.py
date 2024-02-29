import os

import pytest
import sys
sys.path.append('/app')
from app.routes import application
from app.setting.orm_models import session, Users, Tweets
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope='function', autouse=True)
def prepare_tables():
    session.query(Users).delete()
    session.query(Tweets).delete()
    session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
    session.execute(text("ALTER SEQUENCE tweets_id_seq RESTART WITH 1"))
    session.commit()
    user = Users(id=1, name='Sasha', api_key='test')
    session.add(user)
    tweet = Tweets(tweet_data='hello, guys!', tweet_media_ids=None, author_id=user.id)
    session.add(tweet)
    session.commit()


@pytest.fixture(scope='session')
def client():
    app = application.test_client()
    yield app


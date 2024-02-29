import os
import sys
from typing import Optional
import time
from flask import Flask, jsonify, request
from loguru import logger
from setting.orm_models import Likes, Subscribers, Subscriptions, Tweets, Users, session, init_db
from werkzeug.utils import secure_filename
sys.path.append('/app/setting')
sys.path.append('/app/tests')
from setting.app_setting import (
    check_user,
    generate_unique_name,
    get_path,
    save_to_database,
    swaggerui_blueprint,
    allowed_file
)


application = Flask(__name__)
application.config['DEBUG'] = True
application.config['UPLOAD_FOLDER'] = 'upload_folder'
application.register_blueprint(swaggerui_blueprint)
DATABASE_URL = str(os.getenv('DATABASE_URL'))


@application.route('/api/tweets', methods=['POST'])
@check_user
def api_tweets_post(user: Users):
    """Создать твит"""
    tweet_data: str = request.json['tweet_data']
    tweet_media_ids: Optional[set[int]] = request.json["tweet_media_ids"]
    if tweet_media_ids:
        tweet = Tweets(tweet_data=tweet_data, author_id=user.id, tweet_media_ids=tweet_media_ids)
        result = {
            'result': True,
            'tweet_id': tweet.id,
            'tweet_media_ids': tweet_media_ids
        }
    else:
        tweet = Tweets(tweet_data=tweet_data, author_id=user.id)
        result = {
            'result': True,
            'tweet_id': tweet.id
        }
    session.add(tweet)
    session.commit()
    return jsonify(result), 201


@application.route('/api/tweets', methods=['GET'])
def api_tweets_get():
    "Получить все твиты"
    tweets = session.query(Tweets).all()
    info = {
        "result": True,
        "tweets": [
            {
                "id": tweet.id,
                "content": tweet.tweet_data,
                "attachments": [get_path(id) for id in (tweet.tweet_media_ids)],  # Доработать
                "author": {"id": tweet.author.id, "name": tweet.author.name},
                "likes": [
                    {
                        'user_id': like.user_id,
                        'name': like.user.name
                    } for like in tweet.likes
                ]
            } for tweet in tweets]
    }
    session.commit()
    return jsonify(info), 200


@application.route('/api/tweets/<int:id>', methods=['DELETE'])
@check_user
def api_tweets_id_del(id: int, user: Users):
    """Удалить свой твит"""
    to_del = session.query(Tweets).filter(Tweets.id == id, Tweets.author_id == user.id).delete()
    if to_del:
        result = {
            "result": True
        }
        session.commit()
        return jsonify(result), 202
    return 400


@application.route('/api/tweets/<int:id>/likes', methods=['POST'])
@check_user
def api_tweets_likes_post(id: int, user: Users):
    """Поставить лайк"""
    like = Likes(user_id=user.id, tweet_id=id)
    session.add(like)
    result = {
        "result": True
    }
    session.commit()
    return jsonify(result), 202


@application.route('/api/tweets/<int:id>/likes', methods=['DELETE'])
@check_user
def api_tweets_likes_del(id: int, user: Users):
    """Убрать лайк"""
    session.query(Likes).filter(Likes.user_id == user.id, Likes.tweet_id == id).delete()
    result = {
        "result": True
    }
    session.commit()
    return jsonify(result), 202




@application.route('/api/medias', methods=['POST'])
def upload_media():
    """Загрузка фоток"""
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(str(generate_unique_name()) + '.' + file.filename.rsplit('.', 1)[1])
        file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        media_id = save_to_database(filename, file_path)
        return jsonify({'result': True, 'media_id': media_id})

    return jsonify({'result': False, 'error': 'Недопустимый файл'})


@application.route('/api/users/me', methods=['GET'])
@check_user
def api_users_me(user: Users):
    """Получить свои данные"""
    if not user:
        return 'Your api_key is not valid', 404
    result = {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [{"id": user_id, "name": name} for user_id, name in user.subscriptions]},
        "following": [{"id": user_id, "name": name} for user_id, name in user.subscribers]
    }
    logger.debug(f'{result}')
    session.commit()
    return jsonify(result), 200



@application.route('/api/users/<int:id>', methods=['GET'])
def api_users_id(id):
    """Получить данные пользователя"""
    user = session.query(Users).filter(Users.id == id).one()
    result = {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [{"id": user_id, "name": name} for user_id, name in user.subscriptions]},
        "following": [{"id": user_id, "name": name} for user_id, name in user.subscribers]
    }
    session.commit()
    return jsonify(result), 200


@application.route('/api/users/<int:id>/follow', methods=['POST'])
@check_user
def api_users_id_follow_post(id: int, user: Users):
    """Подписаться на пользователя"""
    subscriptions = Subscriptions(user_id=user.id, subscription_id=id)
    subscribers = Subscribers(user_id=id, subscriber_id=user.id)
    session.add(subscribers, subscriptions)
    result = {
        "result": True
    }
    session.commit()
    return jsonify(result), 202


@application.route('/api/users/<int:id>/follow', methods=['DELETE'])
@check_user
def api_users_id_follow_del(id: int, user: Users):
    """Отписаться от другого пользователя"""
    session.query(Subscriptions).filter(
        Subscriptions.user_id == user.id,
        Subscriptions.subscription_id == id).delete()

    session.query(Subscribers).filter(
        Subscribers.user_id == id,
        Subscribers.subscriber_id == user.id).delete()

    result = {
        "result": True
    }
    session.commit()
    return jsonify(result), 202

with application.app_context():
    time.sleep(2)
    init_db()
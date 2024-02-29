import json
from flask import Response

def test_api_users_me(client):
    "Проверка входа"
    response: Response = client.get('/api/users/me', headers={'api_key': 'test'})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['result'] == "true"
    assert 'user' in result
    user = result.get('user')
    assert 'id' in user
    assert 'name' in user
    assert 'followers' in user

def test_api_users_id(client):
    #Тест просмотра профиля
    response: Response = client.get('/api/users/1', headers={'api_key': 'test'})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['result'] == "true"
    assert 'user' in result
    user = result.get('user')
    assert 'id' in user
    assert 'name' in user
    assert 'followers' in user


def test_api_tweets_post(client):
    #Пост твита
    data = {
        'tweet_data': 'This is my first tweet',
        'tweet_media_ids': None
    }
    response: Response = client.post('/api/tweets', json=data, headers={'api_key': 'test'})
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result.get('result') == True
    assert 'tweet_id' in result
    assert result.get('tweet_media_ids') == data['tweet_media_ids']


def test_api_tweets_get(client):
    #Просмотр твитов
    response: Response = client.get('/api/tweets', headers={'api_key': 'test'})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['result'] == True
    assert 'tweets' in result

def test_api_tweets_likes_post(client):
    #Тест поставить лайк
    response: Response = client.post('/api/tweets/1/likes', headers={'api_key': 'test'})
    assert response.status_code == 202
    result = json.loads(response.data)
    assert result['result'] == True

def test_api_tweets_likes_del(client):
    #Тест убрать лайк
    response: Response = client.delete('/api/tweets/1/likes', headers={'api_key': 'test'})
    assert response.status_code == 202
    result = json.loads(response.data)
    assert result['result'] == True



def test_api_tweets_id_del(client):
    #Удалить твит
    response: Response = client.delete('/api/tweets/1', headers={'api_key': 'test'})
    assert response.status_code == 202
    result = json.loads(response.data)
    assert result['result'] == True


def test_upload_media(client):
    #Загрузка фото
    data = {
        'file': open('/app/tests/test_image.jpg', 'rb')
    }
    response: Response = client.post('/api/medias', data=data, headers={'api_key': 'test'})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['result'] == True
    assert 'media_id' in result



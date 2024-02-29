import uuid

from flask import request
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.exc import NoResultFound

from orm_models import Files, Users, session


"""swagger setting"""
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/swagger.yml'  # Our API url (can of course be a local resource)
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
)


"""authorization"""
def check_user(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('api_key')
        try:
            user = session.query(Users).filter(Users.api_key == api_key).one()
        except NoResultFound:
            user = False
        return func(*args, **kwargs, user=user)
    wrapper.__name__ = func.__name__
    return wrapper


"""upload files"""
def get_path(file_id):
    file = session.query(Files).filter(Files.id == file_id).one()
    return file.path


def generate_unique_name():
    unique_name = uuid.uuid4().hex
    return unique_name


def save_to_database(filename, file_path):
    file_record = Files(filename=filename, path=file_path)
    session.add(file_record)
    session.commit()
    return file_record.id

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

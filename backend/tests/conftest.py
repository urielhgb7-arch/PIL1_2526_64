import os
import pytest
from app import create_app
from app.database import db as _db

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'

@pytest.fixture(scope='session')
def app():
    flask_app = create_app()
    flask_app.config['TESTING'] = True

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

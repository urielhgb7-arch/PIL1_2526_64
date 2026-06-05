import os
import pytest
from app import create_app
from app.database import db as _db

os.environ['FLASK_CONFIG'] = 'testing'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['TEST_DATABASE_URL'] = 'sqlite:///:memory:'

@pytest.fixture(scope='session')
def app():
    flask_app = create_app()

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

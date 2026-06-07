import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env.local if present to pick up DATABASE_URL / TEST_DATABASE_URL
base_dir = Path(__file__).resolve().parent.parent
env_file = base_dir / '.env.local'
if env_file.exists():
    load_dotenv(env_file)

os.environ['FLASK_CONFIG'] = 'testing'
jwt_secret = os.environ.get('JWT_SECRET_KEY', 'test-secret-key')
if len(jwt_secret) < 32:
    jwt_secret = jwt_secret.ljust(32, '0')
os.environ['JWT_SECRET_KEY'] = jwt_secret

# Ensure a testing database is configured (TEST_DATABASE_URL or DATABASE_URL)
db_url = os.environ.get('TEST_DATABASE_URL') or os.environ.get('DATABASE_URL')
if not db_url:
    raise RuntimeError('Please set TEST_DATABASE_URL or DATABASE_URL in backend/.env.local for tests (Postgres).')
os.environ['TEST_DATABASE_URL'] = db_url

from app import create_app
from app.database import db as _db

@pytest.fixture(scope='session')
def app():
    flask_app = create_app()

    with flask_app.app_context():
        _db.drop_all()
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield app

@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()

@pytest.fixture()
def socketio_client(app):
    """Fixture pour tester les événements Socket.IO"""
    from app.sockets.chat import socketio
    socketio_test_client = socketio.test_client(app)
    return socketio_test_client

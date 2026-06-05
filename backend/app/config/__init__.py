import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True

class DevelopmentConfig(Config):
    DEBUG = True
    # En dev : SQLite local (ignorer DATABASE_URL)
    # En prod : utiliser DATABASE_URL via ProductionConfig
    _db_path = Path(__file__).resolve().parents[2] / 'instance' / 'dev.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{_db_path.as_posix()}'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'test-secret-key')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

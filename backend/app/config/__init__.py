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
    _db_path = Path(__file__).resolve().parents[2] / 'instance' / 'dev.db'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or f'sqlite:///{_db_path.as_posix()}'
    )

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    )
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL manquant dans l'environnement de production")

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

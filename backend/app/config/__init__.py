import os
import secrets
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


def _require_env(key: str, default: str = None, prod_required: bool = False) -> str:
    """Récupère une variable d'environnement.
    En production, lève une erreur si elle est absente ou égale à la valeur par défaut."""
    value = os.environ.get(key, default)
    if prod_required and os.environ.get('FLASK_ENV') == 'production':
        if not value or value == default:
            raise RuntimeError(
                f"[SÉCURITÉ] La variable d'environnement '{key}' est obligatoire en production. "
                f"Définissez-la sur Render (ou votre hébergeur) avant de déployer."
            )
    return value


class Config:
    # Génère un secret fort aléatoire par défaut (valable uniquement pour le dev local)
    _dev_secret = secrets.token_hex(32)
    _dev_jwt_secret = secrets.token_hex(32)

    SECRET_KEY = _require_env('SECRET_KEY', _dev_secret, prod_required=True)
    JWT_SECRET_KEY = _require_env('JWT_SECRET_KEY', _dev_jwt_secret, prod_required=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True

    # Configuration SMTP (Gmail)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_FROM = os.environ.get('MAIL_FROM', 'noreply@mentorlink.com')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5500')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f'postgresql://{os.environ.get("DB_USER", "postgres")}:{os.environ.get("DB_PASSWORD", "postgres")}@{os.environ.get("DB_HOST", "localhost")}:{os.environ.get("DB_PORT", "5432")}/{os.environ.get("DB_NAME", "mentorlink")}'
    )

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    )

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _require_env(key: str, default: str = None, prod_required: bool = False) -> str:
    """Récupère une variable d'environnement.
    En production, lève une erreur si elle est absente ou égale à la valeur par défaut."""
    value = os.environ.get(key, default)
    if prod_required and os.environ.get("FLASK_ENV") == "production":
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

    SECRET_KEY = _require_env("SECRET_KEY", _dev_secret, prod_required=True)
    JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY", _dev_jwt_secret, prod_required=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # Configuration SMTP (Gmail)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "noreply@mentorlink.com")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5500")

    # Cloudinary (optionnel — si non défini, fallback stockage base64 en DB)
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"postgresql://{os.environ.get('DB_USER', 'postgres')}:{os.environ.get('DB_PASSWORD', 'postgres')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'mentorlink')}"
    )


class ProductionConfig(Config):
    DEBUG = False
    from sqlalchemy.pool import NullPool

    db_url = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://")
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "poolclass": NullPool,
        }
    else:
        _db_path = Path(__file__).resolve().parents[2] / "instance" / "prod.db"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_db_path.as_posix()}"
        SQLALCHEMY_ENGINE_OPTIONS = {}


class TestingConfig(Config):
    TESTING = True
    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

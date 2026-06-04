# backend/app/__init__.py
from dotenv import load_dotenv
import os

load_dotenv()  # ← DOIT être en premier, avant tout import de config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    # Lire depuis l'environnement (déjà chargé par load_dotenv())
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    JWTManager(app)

    # Enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.matching import matching_bp
    from app.routes.messages import messages_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(matching_bp, url_prefix="/api")
    app.register_blueprint(messages_bp, url_prefix="/api")

    return app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
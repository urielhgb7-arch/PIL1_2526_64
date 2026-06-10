# backend/app/__init__.py
import logging
import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.config import config
from app.config.logging_config import setup_logging
from app.database import db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")


def create_app(config_name=None):
    flask_app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG") or os.getenv("FLASK_ENV", "development")

    flask_app.config.from_object(config.get(config_name, config["development"]))

    # Setup logging
    setup_logging(flask_app)
    logger = logging.getLogger(__name__)
    logger.info(f"Configuration: {config_name}")

    CORS(flask_app, resources={r"/api/*": {"origins": "*"}})

    # Garantit les headers CORS sur TOUTES les réponses, y compris les 500
    @flask_app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        return response

    # Handler global pour les exceptions non gérées (évite les 500 sans CORS)
    # Les HTTPException (404, 401...) sont re-propagées pour être gérées normalement
    from werkzeug.exceptions import HTTPException

    @flask_app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        if isinstance(e, HTTPException):
            return e
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"message": "Erreur interne du serveur", "error": str(e)}), 500

    db.init_app(flask_app)
    migrate = Migrate(flask_app, db)
    JWTManager(flask_app)

    # Socket.IO
    from app.sockets.chat import socketio

    socketio.init_app(flask_app)

    # Modèles
    from app import models

    # Creation de la base de données si elle n'existe pas

    with flask_app.app_context():
        try:
            db.create_all()
        except Exception as db_err:
            logger.warning(f"db.create_all(): {db_err}")

    # Initialisation Cloudinary
    from app.services.cloudinary_service import init_cloudinary
    init_cloudinary(flask_app)

    # Swagger / OpenAPI
    try:
        from flasgger import Swagger
        swagger_config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec",
                    "route": "/apispec.json",
                    "rule_filter": lambda rule: rule.rule.startswith("/api/"),
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs/",
        }
        Swagger(flask_app, config={
            "title": "IFRI MentorLink API",
            "description": "API de la plateforme de mentorat académique. Routes documentées avec Swagger.",
            "version": "1.0.0",
            "termsOfService": "",
            "swagger": "2.0",
        }, template={
            "swagger": "2.0",
            "info": {
                "title": "IFRI MentorLink API",
                "description": "Plateforme de mentorat académique — API REST complète.",
                "version": "1.0.0",
                "contact": {
                    "name": "Équipe MentorLink",
                },
            },
            "basePath": "/api",
            "schemes": ["http", "https"],
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT Token. Exemple: 'Bearer <token>'"
                }
            },
        })
        logger.info("Swagger UI disponible sur /docs/")
    except ImportError:
        logger.warning("flasgger not installed — Swagger UI disabled")

    # Seed matières par défaut si la table est vide (uniquement si DB existe)
    try:
        from app.models import Matiere

        if db.session.query(Matiere).count() == 0:
            default_matieres = [
                Matiere(nom="Algorithmique", filiere="GL", annee="L1"),
                Matiere(nom="Structures de données", filiere="GL", annee="L2"),
                Matiere(nom="Base de données SQL", filiere="GL", annee="L1"),
                Matiere(nom="Programmation Orientée Objet", filiere="GL", annee="L2"),
                Matiere(nom="Génie logiciel", filiere="GL", annee="L3"),
                Matiere(nom="Architecture des ordinateurs", filiere="GL", annee="L1"),
                Matiere(nom="Systèmes d'exploitation", filiere="GL", annee="L2"),
                Matiere(nom="Web Development", filiere="GL", annee="L2"),
                Matiere(nom="Réseaux informatiques", filiere="RSI", annee="L1"),
                Matiere(nom="Sécurité des réseaux", filiere="RSI", annee="L2"),
                Matiere(nom="Télécommunications", filiere="RSI", annee="L2"),
                Matiere(nom="Administration système", filiere="RSI", annee="L3"),
                Matiere(nom="Cyberdéfense", filiere="Sécurité", annee="L3"),
                Matiere(nom="Cryptographie", filiere="Sécurité", annee="L2"),
                Matiere(
                    nom="Sécurité des applications", filiere="Sécurité", annee="L3"
                ),
                Matiere(nom="Audit de sécurité", filiere="Sécurité", annee="L3"),
                Matiere(nom="Intelligence artificielle", filiere="GL", annee="L3"),
                Matiere(nom="Machine Learning", filiere="GL", annee="M1"),
                Matiere(nom="Big Data", filiere="RSI", annee="M1"),
                Matiere(nom="Cloud Computing", filiere="GL", annee="M1"),
                Matiere(nom="Développement mobile", filiere="GL", annee="L3"),
                Matiere(nom="Gestion de projet informatique", filiere="GL", annee="M2"),
                Matiere(nom="Langage SQL avancé", filiere="RSI", annee="L3"),
                Matiere(
                    nom="Administration de bases de données", filiere="RSI", annee="M1"
                ),
                Matiere(nom="Sécurité web", filiere="Sécurité", annee="L3"),
                Matiere(nom="Ethical Hacking", filiere="Sécurité", annee="M1"),
            ]
            for m in default_matieres:
                db.session.add(m)
            db.session.commit()
            logger.info(f"{len(default_matieres)} matieres inserees par defaut.")
    except Exception as seed_error:
        logger.warning(f"Seed matieres ignore: {seed_error}")

    # Blueprints
    from app.routes.auth import auth_bp

    flask_app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from app.routes.profile import profile_bp

    flask_app.register_blueprint(profile_bp, url_prefix="/api")

    from app.routes.matching import matching_bp

    flask_app.register_blueprint(matching_bp, url_prefix="/api")

    from app.routes.messages import messages_bp

    flask_app.register_blueprint(messages_bp, url_prefix="/api")

    from app.routes.notifications import notifications_bp

    flask_app.register_blueprint(notifications_bp, url_prefix="/api")

    from app.sockets.polling import polling_bp

    flask_app.register_blueprint(polling_bp, url_prefix="/api")

    from app.routes.offers import offers_bp

    flask_app.register_blueprint(offers_bp, url_prefix="/api")

    _disposed = False

    @flask_app.before_request
    def _dispose_engine_once():
        nonlocal _disposed
        if _disposed:
            return
        _disposed = True
        # Ne pas disposer pour SQLite (in-memory serait perdu)
        if "sqlite" in db.engine.url.drivername:
            logger.info("SQLite detected, skipping engine dispose")
            return
        try:
            db.engine.dispose()
            logger.info("Engine disposed (post-fork cleanup)")
        except Exception as e:
            logger.warning(f"Engine dispose warning: {e}")

    @flask_app.route("/api/health", methods=["GET"])
    def health_check():
        db_ok = False
        db_msg = "unknown"
        try:
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            db_ok = True
            db_msg = "connected"
        except Exception as e:
            db_msg = str(e)[:300]
        return jsonify(
            {"status": "healthy" if db_ok else "degraded", "database": db_msg}
        ), 200 if db_ok else 503

    @flask_app.route("/", defaults={"path": ""})
    @flask_app.route("/<path:path>")
    def serve_frontend(path):
        full_path = os.path.join(FRONTEND_DIR, path)
        if path and os.path.exists(full_path) and not os.path.isdir(full_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return flask_app


# Pour gunicorn (app:app ou wsgi:app)
app = create_app()

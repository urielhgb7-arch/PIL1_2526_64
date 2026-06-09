# backend/app/__init__.py
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.database import db
from app.config import config
from app.config.logging_config import setup_logging
def create_app(config_name=None):
    flask_app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    flask_app.config.from_object(config.get(config_name, config['development']))

    # Setup logging
    setup_logging(flask_app)
    logger = logging.getLogger(__name__)
    logger.info(f"Configuration: {config_name}")

    CORS(flask_app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(flask_app)
    migrate = Migrate(flask_app, db)
    JWTManager(flask_app)

    # Socket.IO
    from app.sockets.chat import socketio
    socketio.init_app(flask_app)

    # Modèles
    from app import models

    #Creation de la base de données si elle n'existe pas

    with flask_app.app_context():
        try:
            from sqlalchemy_utils import database_exists, create_database
            if not database_exists(db.engine.url):
                create_database(db.engine.url)
                logger.info("Base de données créée automatiquement !")
            db.create_all()
            # Appliquer les migrations Flask-Migrate en attente
            try:
                from flask_migrate import upgrade
                upgrade()
            except Exception as mig_err:
                logger.warning(f"Migrations Flask-Migrate ignorées: {mig_err}")
            logger.info("Database tables initialized successfully")
        except Exception as db_error:
            logger.error(f"Database initialization error: {db_error}", exc_info=True)

        # Seed matières par défaut si la table est vide
        try:
            from app.models import Matiere
            if db.session.query(Matiere).count() == 0:
                default_matieres = [
                    Matiere(nom='Algorithmique', filiere='GL', annee='L1'),
                    Matiere(nom='Structures de données', filiere='GL', annee='L2'),
                    Matiere(nom='Base de données SQL', filiere='GL', annee='L1'),
                    Matiere(nom='Programmation Orientée Objet', filiere='GL', annee='L2'),
                    Matiere(nom='Génie logiciel', filiere='GL', annee='L3'),
                    Matiere(nom='Architecture des ordinateurs', filiere='GL', annee='L1'),
                    Matiere(nom='Systèmes d\'exploitation', filiere='GL', annee='L2'),
                    Matiere(nom='Web Development', filiere='GL', annee='L2'),
                    Matiere(nom='Réseaux informatiques', filiere='RSI', annee='L1'),
                    Matiere(nom='Sécurité des réseaux', filiere='RSI', annee='L2'),
                    Matiere(nom='Télécommunications', filiere='RSI', annee='L2'),
                    Matiere(nom='Administration système', filiere='RSI', annee='L3'),
                    Matiere(nom='Cyberdéfense', filiere='Sécurité', annee='L3'),
                    Matiere(nom='Cryptographie', filiere='Sécurité', annee='L2'),
                    Matiere(nom='Sécurité des applications', filiere='Sécurité', annee='L3'),
                    Matiere(nom='Audit de sécurité', filiere='Sécurité', annee='L3'),
                    Matiere(nom='Intelligence artificielle', filiere='GL', annee='L3'),
                    Matiere(nom='Machine Learning', filiere='GL', annee='M1'),
                    Matiere(nom='Big Data', filiere='RSI', annee='M1'),
                    Matiere(nom='Cloud Computing', filiere='GL', annee='M1'),
                    Matiere(nom='Développement mobile', filiere='GL', annee='L3'),
                    Matiere(nom='Gestion de projet informatique', filiere='GL', annee='M2'),
                    Matiere(nom='Langage SQL avancé', filiere='RSI', annee='L3'),
                    Matiere(nom='Administration de bases de données', filiere='RSI', annee='M1'),
                    Matiere(nom='Sécurité web', filiere='Sécurité', annee='L3'),
                    Matiere(nom='Ethical Hacking', filiere='Sécurité', annee='M1'),
                ]
                for m in default_matieres:
                    db.session.add(m)
                db.session.commit()
                logger.info(f" {len(default_matieres)} matières insérées par défaut.")
        except Exception as seed_error:
            logger.warning(f"Seed matières ignoré: {seed_error}")

    # Blueprints
    from app.routes.auth import auth_bp
    flask_app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes.profile import profile_bp
    flask_app.register_blueprint(profile_bp, url_prefix='/api')

    from app.routes.matching import matching_bp
    flask_app.register_blueprint(matching_bp, url_prefix='/api')

    from app.routes.messages import messages_bp
    flask_app.register_blueprint(messages_bp, url_prefix='/api')

    from app.routes.notifications import notifications_bp
    flask_app.register_blueprint(notifications_bp, url_prefix='/api')

    from app.sockets.polling import polling_bp
    flask_app.register_blueprint(polling_bp, url_prefix='/api')
    
    from app.routes.offers import offers_bp
    flask_app.register_blueprint(offers_bp, url_prefix='/api')

    from app.routes.feedback import feedback_bp
    flask_app.register_blueprint(feedback_bp, url_prefix='/api')

    @flask_app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "database": "connected"}), 200

    return flask_app

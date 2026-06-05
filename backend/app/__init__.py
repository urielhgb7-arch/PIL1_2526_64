# backend/app/__init__.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.database import db
from app.config import config


def create_app(config_name=None):
    flask_app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    flask_app.config.from_object(config.get(config_name, config['development']))

    CORS(flask_app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(flask_app)
    JWTManager(flask_app)

    # Modèles
    from app import models

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

    @flask_app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "database": "connected"}), 200

    return flask_app

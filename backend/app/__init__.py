# backend/app/__init__.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.database import db 

def create_app():
    # 1. Création de l'application Flask locale
    flask_app = Flask(__name__) 
    
    # 2. Configurations
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/mentorlink')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-ifri-key')

    # 3. Initialisations
    db.init_app(flask_app)
    jwt = JWTManager(flask_app)
    CORS(flask_app, resources={r"/api/*": {"origins": "*"}})

    # 4. Importation des modèles (On utilise un "from" pour éviter d'écraser la variable)
    from app import models

    # 5. Enregistrement des routes (sur flask_app !)
    from app.routes.auth import auth_bp
    flask_app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes.matching import matching_bp
    flask_app.register_blueprint(matching_bp, url_prefix='/api')
    
    from app.routes.messages import messages_bp
    flask_app.register_blueprint(messages_bp, url_prefix='/api')
    
    from app.sockets.polling import polling_bp
    flask_app.register_blueprint(polling_bp, url_prefix='/api')
    
    @flask_app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "database": "connected"}), 200

    return flask_app
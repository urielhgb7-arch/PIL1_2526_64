import os
from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"status": "ok", "message": "Bienvenue sur l'API MentorLink !"})

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app
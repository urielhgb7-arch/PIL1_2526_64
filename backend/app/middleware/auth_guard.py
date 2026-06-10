# backend/app/middleware/auth_guard.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.database import db
from app.models.user import User

def token_required(f):
    """
    Décorateur pour protéger les routes — vérifie le JWT et injecte l'utilisateur courant.
    Usage : @token_required au-dessus de la fonction de route.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = int(get_jwt_identity())
            current_user = db.session.get(User, current_user_id)
            if not current_user:
                return jsonify({"message": "Utilisateur introuvable"}), 404
        except Exception as e:
            return jsonify({"message": "Token invalide ou expiré", "error": str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def admin_required(f):
    """
    Décorateur pour les routes réservées aux admins.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = int(get_jwt_identity())
            current_user = db.session.get(User, current_user_id)
            if not current_user:
                return jsonify({"message": "Utilisateur introuvable"}), 404
            if current_user.role != 'admin':
                return jsonify({"message": "Accès réservé aux administrateurs"}), 403
        except Exception as e:
            return jsonify({"message": "Token invalide ou expiré", "error": str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

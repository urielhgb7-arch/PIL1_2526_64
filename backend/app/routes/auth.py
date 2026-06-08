
# backend/app/routes/auth.py
import logging
import os
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.database import db
from app.models import User, Profile, PasswordResetToken
from flask_jwt_extended import create_access_token
from app.validators import validate_json, is_valid_email, is_valid_format_preference, is_valid_niveau
from app.middleware.auth_guard import token_required

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

# ── Constantes de validation ─────────────────────────────────────────────────
PASSWORD_MIN_LENGTH = 8  # Minimum 8 caractères (était 6, trop faible)

# ── Rate limiting simple en mémoire pour /forgot-password ────────────────────
# Structure : { ip_address: [timestamp, timestamp, ...] }
_forgot_password_attempts: dict = defaultdict(list)
FORGOT_PASSWORD_MAX_ATTEMPTS = 5    # max 5 tentatives
FORGOT_PASSWORD_WINDOW_SECONDS = 3600  # par heure


def _check_forgot_password_rate_limit(ip: str) -> bool:
    """Retourne True si la limite est dépassée, False sinon."""
    now = datetime.now(timezone.utc).timestamp()
    window_start = now - FORGOT_PASSWORD_WINDOW_SECONDS

    # Nettoyer les anciennes tentatives
    _forgot_password_attempts[ip] = [
        t for t in _forgot_password_attempts[ip] if t > window_start
    ]

    if len(_forgot_password_attempts[ip]) >= FORGOT_PASSWORD_MAX_ATTEMPTS:
        return True  # limite dépassée

    _forgot_password_attempts[ip].append(now)
    return False  # autorisé


def _validate_password_strength(password: str) -> str | None:
    """Valide la robustesse du mot de passe.
    Retourne un message d'erreur, ou None si le mot de passe est valide."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Le mot de passe doit faire au moins {PASSWORD_MIN_LENGTH} caractères"
    if not any(c.isdigit() for c in password):
        return "Le mot de passe doit contenir au moins un chiffre"
    if not any(c.isalpha() for c in password):
        return "Le mot de passe doit contenir au moins une lettre"
    return None


@auth_bp.route('/register', methods=['POST'])
@validate_json(required_fields=['email', 'password', 'nom', 'prenom'], email_field='email')
def register():
    """Enregistre un nouvel utilisateur (étudiant)"""
    data = request.validated_json

    try:
        # Validation robustesse du mot de passe
        pwd_error = _validate_password_strength(data['password'])
        if pwd_error:
            return jsonify({"message": pwd_error}), 400

        # Vérification unicité email
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"Tentative inscription avec email existant: {data['email'][:10]}***")
            return jsonify({"message": "Cet email existe déjà"}), 400

        # Validation niveau
        if data.get('niveau') and not is_valid_niveau(data['niveau']):
            return jsonify({"message": "Niveau invalide. Valeurs acceptées: L1-L3, M1-M2"}), 400

        # Validation format
        format_preference = data.get('format_preference', 'hybride')
        if format_preference and not is_valid_format_preference(format_preference):
            return jsonify({"message": "Format d'apprentissage invalide"}), 400
        

        # backend/app/routes/auth.py — dans register()
        if data.get('telephone'):
            existing_tel = Profile.query.filter_by(telephone=data['telephone']).first()
            if existing_tel:
                return jsonify({"message": "Ce numéro de téléphone est déjà utilisé"}), 400

        # Création user
        new_user = User(email=data['email'], role='student')
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.flush()  # ← obtient l'id SANS commiter
        logger.info(f"✅ Utilisateur créé: {data['email'][:10]}***")

        # Création du profil dans la même transaction
        new_profile = Profile(
            user_id=new_user.id,
            nom=data['nom'],
            prenom=data['prenom'],
            filiere=data.get('filiere') or '',
            niveau=data.get('niveau') or '',
            format_preference=format_preference,
            bio=data.get('bio', ''),
            telephone=data.get('telephone', '')
        )
        db.session.add(new_profile)
        db.session.commit()  # ← un seul commit pour les deux
        logger.info(f"✅ Profil créé pour user_id={new_user.id}")

        # Retour du token
        access_token = create_access_token(identity=str(new_user.id))
        return jsonify({
            "message": "Compte créé avec succès !",
            "token": access_token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "role": new_user.role
            }
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Erreur intégrité DB: {str(e)[:100]}")
        return jsonify({"message": "Erreur lors de la création du compte"}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur inscription: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authentifie un utilisateur et retourne un JWT"""
    try:
        data = request.get_json(force=True, silent=True)
        if not data or not data.get('email') or not data.get('password'):
            logger.warning("Tentative login sans email/password")
            return jsonify({"message": "Email et mot de passe requis"}), 400

        if not is_valid_email(data.get('email')):
            logger.warning(f"Login avec email invalide: {data.get('email')[:10] if data.get('email') else 'None'}***")
            return jsonify({"message": "Email invalide"}), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            logger.warning(f"Login échoué pour: {data['email'][:10]}***")
            return jsonify({"message": "Identifiants invalides"}), 401

        profile_id = user.profile.id if user.profile else None
        access_token = create_access_token(identity=str(user.id))
        logger.info(f"✅ Login réussi: {data['email'][:10]}***")

        return jsonify({
            "token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "profile_id": profile_id
            }
        }), 200

    except Exception as e:
        logger.error(f"Erreur login: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json(required_fields=['email'], email_field='email')
def forgot_password():
    """Demande de réinitialisation de mot de passe.
    - Rate limité à 5 tentatives/heure par IP pour éviter le spam.
    - Le token N'EST JAMAIS retourné dans la réponse (même en dev).
      Consultez les logs du serveur en développement.
    """
    # Rate limiting par IP
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
    if _check_forgot_password_rate_limit(client_ip):
        logger.warning(f"Rate limit /forgot-password dépassé pour IP={client_ip}")
        return jsonify({"message": "Trop de tentatives. Réessayez dans une heure."}), 429

    data = request.validated_json
    email = data['email']
    user = User.query.filter_by(email=email).first()

    # Réponse identique qu'il y ait un compte ou non (évite l'énumération d'emails)
    response = {"message": "Si votre email existe, un lien de réinitialisation a été émis."}

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()

        # En dev : afficher le token dans les logs (jamais dans la réponse HTTP)
        if os.getenv('FLASK_ENV') != 'production':
            logger.info(
                f"[DEV UNIQUEMENT] Token reset pour user_id={user.id} : {token} "
                f"(expire dans 1h — ne jamais afficher en production)"
            )
        else:
            logger.info(f"Réinitialisation MDP demandée pour user_id={user.id}")
            # TODO : envoyer le token par email via un service SMTP (ex: SendGrid, Mailgun)

    return jsonify(response), 200


@auth_bp.route('/reset-password', methods=['POST'])
@validate_json(required_fields=['token', 'new_password'])
def reset_password():
    data = request.validated_json
    token = data['token']
    new_password = data['new_password']

    pwd_error = _validate_password_strength(new_password)
    if pwd_error:
        return jsonify({"message": pwd_error}), 400

    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
    now = datetime.now(timezone.utc)

    if not reset_token:
        return jsonify({"message": "Token invalide ou expiré"}), 400

    expires_at = reset_token.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        return jsonify({"message": "Token invalide ou expiré"}), 400

    user = db.session.get(User, reset_token.user_id)
    if not user:
        return jsonify({"message": "Token invalide ou expiré"}), 400

    user.set_password(new_password)
    reset_token.used = True
    db.session.commit()

    logger.info(f"Mot de passe réinitialisé pour user_id={user.id} email={user.email}")
    return jsonify({"message": "Mot de passe réinitialisé avec succès"}), 200


@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.get_json(force=True, silent=True) or {}

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"message": "Ancien et nouveau mot de passe requis"}), 400

    if not current_user.check_password(old_password):
        return jsonify({"message": "Ancien mot de passe incorrect"}), 401

    pwd_error = _validate_password_strength(new_password)
    if pwd_error:
        return jsonify({"message": pwd_error}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Mot de passe modifié avec succès"}), 200

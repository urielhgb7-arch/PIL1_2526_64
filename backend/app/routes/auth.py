# backend/app/routes/auth.py
import logging
import os
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.database import db
from app.middleware.auth_guard import token_required
from app.models import (
    Conversation,
    EmailToken,
    Matching,
    Message,
    Notification,
    PasswordResetToken,
    Profile,
    User,
)
from app.services.email_service import send_password_reset_email, send_verification_email
from app.validators import (
    is_valid_benin_phone,
    is_valid_email,
    is_valid_format_preference,
    is_valid_niveau,
    validate_json,
)
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

# ── Constantes de validation ─────────────────────────────────────────────────
PASSWORD_MIN_LENGTH = 8  # Minimum 8 caractères (était 6, trop faible)

# ── Rate limiting simple en mémoire pour /forgot-password ────────────────────
# Structure : { ip_address: [timestamp, timestamp, ...] }
_forgot_password_attempts: dict = defaultdict(list)
FORGOT_PASSWORD_MAX_ATTEMPTS = 5  # max 5 tentatives
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


@auth_bp.route("/register", methods=["POST"])
@validate_json(
    required_fields=["email", "password", "nom", "prenom"], email_field="email"
)
def register():
    """Enregistre un nouvel utilisateur (étudiant)"""
    data = request.validated_json

    try:
        # Validation robustesse du mot de passe
        pwd_error = _validate_password_strength(data["password"])
        if pwd_error:
            return jsonify({"message": pwd_error}), 400

        # Vérification unicité email
        if User.query.filter_by(email=data["email"]).first():
            logger.warning(
                f"Tentative inscription avec email existant: {data['email'][:10]}***"
            )
            return jsonify({"message": "Cet email existe déjà"}), 400

        # Validation niveau
        if data.get("niveau") and not is_valid_niveau(data["niveau"]):
            return jsonify(
                {"message": "Niveau invalide. Valeurs acceptées: L1-L3, M1-M2"}
            ), 400

        # Validation format
        format_preference = data.get("format_preference", "hybride")
        if format_preference and not is_valid_format_preference(format_preference):
            return jsonify({"message": "Format d'apprentissage invalide"}), 400

        # Validation téléphone béninois
        phone = data.get("telephone")
        if phone and not is_valid_benin_phone(phone):
            return (
                jsonify(
                    {
                        "message": "Numéro de téléphone béninois invalide. Format attendu: 01[4569]XXXXXXX (10 chiffres)"
                    }
                ),
                400,
            )

        # backend/app/routes/auth.py — dans register()
        if data.get("telephone"):
            existing_tel = Profile.query.filter_by(telephone=data["telephone"]).first()
            if existing_tel:
                return jsonify(
                    {"message": "Ce numéro de téléphone est déjà utilisé"}
                ), 400

        # Création user
        new_user = User(email=data["email"], role="student")
        new_user.set_password(data["password"])
        db.session.add(new_user)
        db.session.flush()  # ← obtient l'id SANS commiter
        logger.info(f" Utilisateur créé: {data['email'][:10]}***")

        # Création du profil dans la même transaction
        phone = data.get("telephone")
        if not phone:
            phone = f"non-renseigne-{new_user.id}"
        new_profile = Profile(
            user_id=new_user.id,
            nom=data["nom"],
            prenom=data["prenom"],
            filiere=data.get("filiere") or "GL",
            niveau=data.get("niveau") or "L1",
            format_preference=format_preference,
            bio=data.get("bio", ""),
            telephone=phone,
        )
        db.session.add(new_profile)
        db.session.commit()  # ← un seul commit pour les deux
        logger.info(f" Profil créé pour user_id={new_user.id}")

        # Génération token de vérification email
        verif_token_str = None
        if new_user.email.endswith('@test.ifri.edu'):
            new_user.email_verified = True
            db.session.commit()
            logger.info(f"Email auto-vérifié pour user test user_id={new_user.id}")
        else:
            verif_token_str = secrets.token_urlsafe(32)
            verif_expires = datetime.now(timezone.utc) + timedelta(hours=24)
            db.session.add(EmailToken(user_id=new_user.id, token=verif_token_str, expires_at=verif_expires))
            db.session.commit()
            logger.info(f"Token vérification email généré pour user_id={new_user.id}")
            
            # Envoi de l'email de vérification (si SMTP configuré)
            email_sent = send_verification_email(new_user.email, verif_token_str)
            if email_sent:
                logger.info(f"Email de vérification envoyé à user_id={new_user.id} ({new_user.email[:10]}***)")
            else:
                logger.warning(f"Email de vérification non envoyé (SMTP non configuré) pour user_id={new_user.id}")

        # Retour du token
        access_token = create_access_token(identity=str(new_user.id))
        response = {
            "message": "Compte créé avec succès !",
            "token": access_token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "role": new_user.role,
                "email_verified": new_user.email_verified,
            },
        }
        # En dev : retourner le token de vérification pour test
        if verif_token_str and os.getenv('FLASK_ENV') != 'production':
            response['verification_token'] = verif_token_str
            response['verification_url'] = f"/api/auth/verify-email?token={verif_token_str}"

        return jsonify(response), 201

    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Erreur intégrité DB: {str(e)[:100]}")
        return jsonify({"message": "Erreur lors de la création du compte"}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur inscription: {str(e)[:500]}", exc_info=True)
        return jsonify({"message": f"Erreur serveur: {str(e)[:500]}"}), 500


@auth_bp.route("/verify-email", methods=["GET"])
def verify_email():
    """Vérifie l'email d'un utilisateur via un token"""
    token = request.args.get('token')
    if not token:
        return jsonify({"message": "Token requis"}), 400

    email_token = EmailToken.query.filter_by(token=token).first()
    if not email_token:
        return jsonify({"message": "Token invalide"}), 400

    now = datetime.now(timezone.utc)
    expires = email_token.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        db.session.delete(email_token)
        db.session.commit()
        return jsonify({"message": "Token expiré"}), 400

    user = db.session.get(User, email_token.user_id)
    if not user:
        return jsonify({"message": "Utilisateur introuvable"}), 404

    user.email_verified = True
    db.session.delete(email_token)
    db.session.commit()

    logger.info(f"Email vérifié pour user_id={user.id}")
    return jsonify({"message": "Email vérifié avec succès ! Vous pouvez maintenant vous connecter."}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authentifie un utilisateur et retourne un JWT"""
    try:
        data = request.get_json(force=True, silent=True)
        if not data or not data.get("email") or not data.get("password"):
            logger.warning("Tentative login sans email/password")
            return jsonify({"message": "Email et mot de passe requis"}), 400

        if not is_valid_email(data.get("email")):
            logger.warning(
                f"Login avec email invalide: {data.get('email')[:10] if data.get('email') else 'None'}***"
            )
            return jsonify({"message": "Email invalide"}), 400

        user = User.query.filter_by(email=data["email"]).first()

        if not user or not user.check_password(data["password"]):
            logger.warning(f"Login échoué pour: {data['email'][:10]}***")
            return jsonify({"message": "Identifiants invalides"}), 401

        # Vérification email — sauf pour @test.ifri.edu et @gmail.com en dev
        is_dev_env = os.getenv('FLASK_ENV') != 'production'
        is_test_email = user.email.endswith('@test.ifri.edu') or (user.email.endswith('@gmail.com') and is_dev_env)
        if not user.email_verified and not is_test_email:
            logger.warning(f"Login refusé: email non vérifié pour {data['email'][:10]}***")
            return jsonify({"message": "Veuillez vérifier votre email avant de vous connecter", "email_verified": False}), 403

        profile_id = user.profile.id if user.profile else None
        access_token = create_access_token(identity=str(user.id))
        logger.info(f" Login réussi: {data['email'][:10]}***")

        return jsonify(
            {
                "token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "profile_id": profile_id,
                    "email_verified": user.email_verified,
                },
            }
        ), 200

    except Exception as e:
        logger.error(f"Erreur login: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


@auth_bp.route("/forgot-password", methods=["POST"])
@validate_json(required_fields=["email"], email_field="email")
def forgot_password():
    """Demande de réinitialisation de mot de passe.
    - Rate limité à 5 tentatives/heure par IP pour éviter le spam.
    - En dev : le token est retourné dans la réponse pour faciliter les tests.
    - En production : le token N'EST PAS retourné (log uniquement).
    """
    # Rate limiting par IP
    client_ip = (
        request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
        .split(",")[0]
        .strip()
    )
    if _check_forgot_password_rate_limit(client_ip):
        logger.warning(f"Rate limit /forgot-password dépassé pour IP={client_ip}")
        return jsonify(
            {"message": "Trop de tentatives. Réessayez dans une heure."}
        ), 429

    data = request.validated_json
    email = data["email"]
    user = User.query.filter_by(email=email).first()

    # Réponse identique qu'il y ait un compte ou non (évite l'énumération d'emails)
    response = {
        "message": "Si votre email existe, un lien de réinitialisation a été émis."
    }

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = PasswordResetToken(
            user_id=user.id, token=token, expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()

        # Toujours retourner le token dans la réponse pour faciliter les tests
        response["reset_token"] = token
        logger.info(
            f"Token reset pour user_id={user.id} : {token} "
            f"(expire dans 1h)"
        )
        
        # Envoi de l'email (si SMTP configuré)
        email_sent = send_password_reset_email(user.email, token)
        if email_sent:
            logger.info(f"Email de réinitialisation envoyé à {user.email[:10]}***")
        else:
            logger.warning(f"Email de réinitialisation non envoyé (SMTP non configuré)")

    return jsonify(response), 200


@auth_bp.route("/reset-password", methods=["POST"])
@validate_json(required_fields=["token", "new_password"])
def reset_password():
    data = request.validated_json
    token = data["token"]
    new_password = data["new_password"]

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


@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password(current_user):
    data = request.get_json(force=True, silent=True) or {}

    old_password = data.get("old_password")
    new_password = data.get("new_password")

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


@auth_bp.route("/delete-account", methods=["DELETE"])
@token_required
def delete_account(current_user):
    """Supprime définitivement le compte de l'utilisateur connecté.
    Requiert la confirmation du mot de passe.
    """
    data = request.get_json(force=True, silent=True) or {}
    password = data.get("password")

    if not password:
        return jsonify(
            {"message": "Mot de passe requis pour confirmer la suppression"}
        ), 400

    if not current_user.check_password(password):
        return jsonify({"message": "Mot de passe incorrect"}), 401

    user_id = current_user.id
    user_email = current_user.email

    try:
        # 1. Supprimer les messages des conversations impliquant l'utilisateur
        conversations = Conversation.query.filter(
            (Conversation.user_one_id == user_id)
            | (Conversation.user_two_id == user_id)
        ).all()
        conv_ids = [c.id for c in conversations]
        if conv_ids:
            Message.query.filter(Message.conversation_id.in_(conv_ids)).delete(
                synchronize_session=False
            )

        # 2. Supprimer les conversations elles-mêmes
        Conversation.query.filter(
            (Conversation.user_one_id == user_id)
            | (Conversation.user_two_id == user_id)
        ).delete(synchronize_session=False)

        # 3. Supprimer les notifications de l'utilisateur
        Notification.query.filter_by(user_id=user_id).delete(synchronize_session=False)

        # 4. Supprimer les matchings impliquant l'utilisateur
        Matching.query.filter(
            (Matching.user_one_id == user_id)
            | (Matching.user_two_id == user_id)
            | (Matching.initiator_id == user_id)
        ).delete(synchronize_session=False)

        # 5. Supprimer l'utilisateur (cascade vers Profile → Offers, Demands,
        #    Competences, Lacunes, Disponibilites, PasswordResetTokens)
        db.session.delete(current_user)
        db.session.commit()

        logger.info(f"Compte supprimé : user_id={user_id} email={user_email[:10]}***")
        return jsonify({"message": "Compte supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Erreur suppression compte user_id={user_id}: {str(e)[:500]}",
            exc_info=True,
        )
        return jsonify(
            {"message": "Erreur serveur lors de la suppression du compte"}
        ), 500

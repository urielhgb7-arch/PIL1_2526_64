
# backend/app/routes/auth.py
import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.database import db
from app.models import User, Profile
from flask_jwt_extended import create_access_token
from app.validators import validate_json, is_valid_email, is_valid_format_preference, is_valid_niveau

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_json(required_fields=['email', 'password', 'nom', 'prenom', 'filiere', 'niveau'], email_field='email')
def register():
    """Enregistre un nouvel utilisateur (étudiant)"""
    data = request.validated_json
    
    try:
        # Vérification unicité email
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"Tentative inscription avec email existant: {data['email'][:10]}***")
            return jsonify({"message": "Cet email existe déjà"}), 400

        # Validation niveau
        if not is_valid_niveau(data['niveau']):
            logger.warning(f"Niveau invalide: {data['niveau']}")
            return jsonify({"message": f"Niveau invalide. Valeurs acceptées: L1-L3, M1-M2"}), 400

        # Création de l'utilisateur — rôle 'student' FIXÉ côté serveur
        new_user = User(email=data['email'], role='student')
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"✅ Utilisateur créé: {data['email'][:10]}***")

        # Création du profil
        format_preference = data.get('format_preference', 'hybride')
        if format_preference and not is_valid_format_preference(format_preference):
            logger.warning(f"Format invalide: {format_preference}")
            return jsonify({"message": "Format d'apprentissage invalide"}), 400

        new_profile = Profile(
            user_id=new_user.id,
            nom=data['nom'],
            prenom=data['prenom'],
            filiere=data['filiere'],
            niveau=data['niveau'],
            format_preference=format_preference,
            bio=data.get('bio', ''),
            telephone=data.get('telephone', '')
        )
        db.session.add(new_profile)
        db.session.commit()
        logger.info(f"✅ Profil créé pour user_id={new_user.id}")

        return jsonify({"message": "Compte créé avec succès ! Connectez-vous."}), 201
        
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


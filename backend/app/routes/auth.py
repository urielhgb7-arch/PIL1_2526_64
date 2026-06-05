
# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User, Profile
from flask_jwt_extended import create_access_token
from app.validators import validate_json, is_valid_email, is_valid_format_preference

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_json(required_fields=['email', 'password', 'nom', 'prenom', 'filiere', 'niveau'], email_field='email')
def register():
    data = request.validated_json

    # Vérification unicité email
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Cet email existe déjà"}), 400

    # Création de l'utilisateur — rôle 'student' FIXÉ côté serveur (jamais par le frontend)
    new_user = User(email=data['email'], role='student')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    # Création automatique du profil lié (toutes colonnes NOT NULL couvertes)
    format_preference = data.get('format_preference', 'hybride')
    if format_preference and not is_valid_format_preference(format_preference):
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

    return jsonify({"message": "Compte créé avec succès ! Connectez-vous."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    
    data = request.get_json(force=True, silent=True)
    # force=True : force la lecture même sans Content-Type
    # silent=True : retourne None au lieu de planter si le JSON est invalide
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email et mot de passe requis"}), 400

    if not is_valid_email(data.get('email')):
        return jsonify({"message": "Email invalide"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Identifiants invalides"}), 401

    profile_id = user.profile.id if user.profile else None

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "profile_id": profile_id
        }
    }), 200

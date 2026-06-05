
# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User, Profile
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validation des champs obligatoires (cohérent avec schema.sql NOT NULL)
    required_fields = ['email', 'password', 'nom', 'prenom', 'filiere', 'niveau']
    if not data or not all(data.get(field) for field in required_fields):
        return jsonify({
            "message": "Champs obligatoires manquants",
            "required": required_fields
        }), 400

    # Vérification unicité email
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Cet email existe déjà"}), 400

    # Création de l'utilisateur — rôle 'student' FIXÉ côté serveur (jamais par le frontend)
    new_user = User(email=data['email'], role='student')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    # Création automatique du profil lié (toutes colonnes NOT NULL couvertes)
    new_profile = Profile(
        user_id=new_user.id,
        nom=data['nom'],
        prenom=data['prenom'],
        filiere=data['filiere'],
        niveau=data['niveau'],
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

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Identifiants invalides"}), 401

    profile_id = user.profile.id if user.profile else None

    # JWT avec rôle 'student' unifié (double casquette Mentor/Mentoré)
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': 'student',
            'email': user.email
        }
    )

    return jsonify({
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "profile_id": profile_id
        }
    }), 200

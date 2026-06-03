from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User, Profile
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({"message": "Données incomplètes"}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Cet email existe déjà"}), 400

    new_user = User(email=data['email'], role=data['role'])
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()

    # Amorce du J3 : création automatique du profil lié
    new_profile = Profile(
        user_id=new_user.id,
        nom=data.get('nom', ''),
        prenom=data.get('prenom', ''),
        filiere=data.get('filiere', 'Non spécifiée'),
        niveau=data.get('niveau', 'L1')
    )
    db.session.add(new_profile)
    db.session.commit()

    return jsonify({"message": "Compte créé avec succès ! Connectez-vous."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email et mot de passe requis"}), 400
        
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
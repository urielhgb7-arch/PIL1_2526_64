from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Profile, Offer, Demand

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/matching', methods=['GET'])
@jwt_required()
def get_matches():
    # 1. Qui est connecté ?
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "Utilisateur introuvable"}), 404

    # 2. Trouver son profil
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    # 3. Seulement pour les mentorés
    if user.role != 'mentore':
        return jsonify({"message": "Réservé aux mentorés"}), 403

    # 4. Quelles matières cherche ce mentoré ?
    mes_demandes = Demand.query.filter_by(profile_id=profile.id).all()
    matieres_cherchees = [d.matiere for d in mes_demandes]

    if not matieres_cherchees:
        return jsonify({"message": "Aucune demande enregistrée"}), 400

    # 5. Trouver les mentors qui proposent ces matières
    offres = Offer.query.filter(
        Offer.matiere.in_(matieres_cherchees)
    ).all()

    # 6. Construire la réponse
    resultats = []
    for offre in offres:
        mentor_profile = Profile.query.get(offre.profile_id)
        mentor_user = User.query.get(mentor_profile.user_id)
        resultats.append({
            "mentor_id": mentor_user.id,
            "nom": mentor_profile.nom,
            "prenom": mentor_profile.prenom,
            "filiere": mentor_profile.filiere,
            "matiere": offre.matiere,
            "disponible": mentor_profile.disponible
        })

    return jsonify(resultats), 200
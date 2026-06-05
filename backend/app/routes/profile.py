# backend/app/routes/profile.py
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User, Profile, Disponible, ProfilCompetence, ProfilLacune, Matiere
from app.middleware.auth_guard import token_required

profile_bp = Blueprint('profile', __name__)


# ─── GET /api/profile/me ────────────────────────────────────────────────────
@profile_bp.route('/profile/me', methods=['GET'])
@token_required
def get_my_profile(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    # Compétences
    competences = ProfilCompetence.query.filter_by(profile_id=profile.id).all()
    competences_data = []
    for c in competences:
        matiere = db.session.get(Matiere, c.matiere_id)
        competences_data.append({
            "matiere_id": c.matiere_id,
            "matiere_nom": matiere.nom if matiere else "",
            "niveau": c.niveau
        })

    # Lacunes
    lacunes = ProfilLacune.query.filter_by(profile_id=profile.id).all()
    lacunes_data = []
    for l in lacunes:
        matiere = db.session.get(Matiere, l.matiere_id)
        lacunes_data.append({
            "matiere_id": l.matiere_id,
            "matiere_nom": matiere.nom if matiere else "",
            "priorite": l.priorite
        })

    # Disponibilités
    dispos = Disponible.query.filter_by(profile_id=profile.id).all()
    dispos_data = [{"jour": d.jour, "creneau": d.creneau} for d in dispos]

    return jsonify({
        "id": profile.id,
        "user_id": current_user.id,
        "email": current_user.email,
        "nom": profile.nom,
        "prenom": profile.prenom,
        "filiere": profile.filiere,
        "niveau": profile.niveau,
        "bio": profile.bio,
        "telephone": profile.telephone,
        "disponible": profile.disponible,
        "avatar_url": profile.avatar_url,
        "competences": competences_data,
        "lacunes": lacunes_data,
        "disponibilites": dispos_data
    }), 200


# ─── PUT /api/profile/me ────────────────────────────────────────────────────
@profile_bp.route('/profile/me', methods=['PUT'])
@token_required
def update_my_profile(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()

    # Mise à jour des champs simples
    if data.get('nom'):
        profile.nom = data['nom']
    if data.get('prenom'):
        profile.prenom = data['prenom']
    if data.get('filiere'):
        profile.filiere = data['filiere']
    if data.get('niveau'):
        profile.niveau = data['niveau']
    if 'bio' in data:
        profile.bio = data['bio']
    if 'telephone' in data:
        profile.telephone = data['telephone']
    if 'disponible' in data:
        profile.disponible = data['disponible']

    db.session.commit()
    return jsonify({"message": "Profil mis à jour avec succès"}), 200


# ─── POST /api/profile/disponibilites ───────────────────────────────────────
@profile_bp.route('/profile/disponibilites', methods=['POST'])
@token_required
def add_disponibilite(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    jour = data.get('jour')
    creneau = data.get('creneau')

    if not jour or not creneau:
        return jsonify({"message": "jour et creneau requis"}), 400

    dispo = Disponible(profile_id=profile.id, jour=jour, creneau=creneau)
    db.session.add(dispo)
    db.session.commit()

    return jsonify({"message": "Disponibilité ajoutée"}), 201


# ─── DELETE /api/profile/disponibilites ─────────────────────────────────────
@profile_bp.route('/profile/disponibilites', methods=['DELETE'])
@token_required
def remove_disponibilite(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    jour = data.get('jour')
    creneau = data.get('creneau')

    dispo = Disponible.query.filter_by(
        profile_id=profile.id, jour=jour, creneau=creneau
    ).first()

    if not dispo:
        return jsonify({"message": "Disponibilité introuvable"}), 404

    db.session.delete(dispo)
    db.session.commit()
    return jsonify({"message": "Disponibilité supprimée"}), 200


# ─── POST /api/profile/competences ──────────────────────────────────────────
@profile_bp.route('/profile/competences', methods=['POST'])
@token_required
def add_competence(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    data = request.get_json()

    matiere_id = data.get('matiere_id')
    niveau = data.get('niveau', 'Intermédiaire')

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    existing = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if existing:
        return jsonify({"message": "Compétence déjà ajoutée"}), 400

    comp = ProfilCompetence(profile_id=profile.id, matiere_id=matiere_id, niveau=niveau)
    db.session.add(comp)
    db.session.commit()
    return jsonify({"message": "Compétence ajoutée"}), 201


# ─── DELETE /api/profile/competences ────────────────────────────────────────
@profile_bp.route('/profile/competences', methods=['DELETE'])
@token_required
def remove_competence(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    data = request.get_json()
    matiere_id = data.get('matiere_id')

    comp = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if not comp:
        return jsonify({"message": "Compétence introuvable"}), 404

    db.session.delete(comp)
    db.session.commit()
    return jsonify({"message": "Compétence supprimée"}), 200

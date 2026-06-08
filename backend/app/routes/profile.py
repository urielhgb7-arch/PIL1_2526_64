# backend/app/routes/profile.py
import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError, ProgrammingError
from app.database import db
from app.models import User, Profile, Disponible, ProfilCompetence, ProfilLacune, Matiere
from app.middleware.auth_guard import token_required
from app.validators import matiere_exists, is_valid_format_preference, is_valid_day, is_valid_competence_level, is_valid_priority_level

logger = logging.getLogger(__name__)
profile_bp = Blueprint('profile', __name__)
CRENEAUX_VALIDES = [
       '08-09', '09-10', '10-11', '11-12',
            '12-13', '13-14',                   
            '14-15', '15-16', '16-17', '17-18', 
            '18-19', '19-20', '20-21' ,'21-22'   
]


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
            "niveau": c.niveau,
            "is_available_to_help": c.is_available_to_help
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
    dispos_data = [{
        "jour": d.jour,
        "creneau": d.creneau,
        "is_reserved": d.is_reserved
    } for d in dispos]

    return jsonify({
        "id": profile.id,
        "user_id": current_user.id,
        "email": current_user.email,
        "nom": profile.nom,
        "prenom": profile.prenom,
        "filiere": profile.filiere,
        "niveau": profile.niveau,
        "format_preference": profile.format_preference,
        "bio": profile.bio,
        "telephone": profile.telephone,
        "disponible": profile.disponible,
        "avatar_url": profile.avatar_url,
        "competences": competences_data,
        "lacunes": lacunes_data,
        "disponibilites": dispos_data
    }), 200


# ─── POST /api/profile/lacunes ─────────────────────────────────────────────
@profile_bp.route('/profile/lacunes', methods=['POST'])
@token_required
def add_lacune(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    matiere_id = data.get('matiere_id')


    # 🆕 CHECK CROISÉ : la matière est-elle déjà une compétence ?
    competence_existante = ProfilCompetence.query.filter_by(
        profile_id=profile.id,
        matiere_id=matiere_id
    ).first()
    if competence_existante:
        return jsonify({
            "message": "Cette matière est déjà dans tes compétences. Supprime-la d'abord avant de l'ajouter en lacune."
        }), 400
    
    priorite = data.get('priorite', 'Moyenne')

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    if not is_valid_priority_level(priorite):
        return jsonify({"message": "Priorité invalide"}), 400

    existing = ProfilLacune.query.filter_by(profile_id=profile.id, matiere_id=matiere_id).first()
    if existing:
        return jsonify({"message": "Lacune déjà ajoutée"}), 400

    lacune = ProfilLacune(profile_id=profile.id, matiere_id=matiere_id, priorite=priorite)
    db.session.add(lacune)
    db.session.commit()

    return jsonify({"message": "Lacune ajoutée"}), 201


# ─── DELETE /api/profile/lacunes ────────────────────────────────────────────
@profile_bp.route('/profile/lacunes', methods=['DELETE'])
@token_required
def remove_lacune(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    matiere_id = data.get('matiere_id')

    lacune = ProfilLacune.query.filter_by(profile_id=profile.id, matiere_id=matiere_id).first()
    if not lacune:
        return jsonify({"message": "Lacune introuvable"}), 404

    db.session.delete(lacune)
    db.session.commit()
    return jsonify({"message": "Lacune supprimée"}), 200


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
    if 'format_preference' in data:
        format_preference = data['format_preference']
        if not is_valid_format_preference(format_preference):
            return jsonify({"message": "Format d'apprentissage invalide"}), 400
        profile.format_preference = format_preference

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

    jours_valides = {'Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'}
    if jour not in jours_valides:
        return jsonify({"message": "jour invalide"}), 400
    if creneau not in CRENEAUX_VALIDES:
        return jsonify({"message": "Créneau invalide"}), 400

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

    # 🆕 CHECK CROISÉ : la matière est-elle déjà une lacune ?
    lacune_existante = ProfilLacune.query.filter_by(
        profile_id=profile.id,
        matiere_id=matiere_id
    ).first()
    if lacune_existante:
        return jsonify({
            "message": "Cette matière est déjà dans tes lacunes. Supprime-la d'abord avant de l'ajouter en compétence."
        }), 400
    
    niveau = data.get('niveau', 'Intermédiaire')
    is_available_to_help = data.get('is_available_to_help', True)

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    # vérifier que la matière existe
    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    existing = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if existing:
        return jsonify({"message": "Compétence déjà ajoutée"}), 400

    if isinstance(is_available_to_help, str):
        if is_available_to_help.lower() in ('true', 'false'):
            is_available_to_help = is_available_to_help.lower() == 'true'
        else:
            return jsonify({"message": "is_available_to_help doit être true ou false"}), 400
    else:
        is_available_to_help = bool(is_available_to_help)

    comp = ProfilCompetence(
        profile_id=profile.id,
        matiere_id=matiere_id,
        niveau=niveau,
        is_available_to_help=is_available_to_help
    )
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


# ─── PUT /api/profile/competences/<matiere_id>/activate ──────────────────
@profile_bp.route('/profile/competences/<int:matiere_id>/activate', methods=['PUT'])
@token_required
def activate_competence(current_user, matiere_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    comp = ProfilCompetence.query.filter_by(
        profile_id=profile.id,
        matiere_id=matiere_id
    ).first()
    if not comp:
        return jsonify({"message": "Compétence introuvable"}), 404

    comp.is_available_to_help = True
    db.session.commit()
    return jsonify({"message": "Compétence activée pour l'aide", "is_available_to_help": comp.is_available_to_help}), 200


# ─── PUT /api/profile/competences/<matiere_id>/deactivate ───────────────
@profile_bp.route('/profile/competences/<int:matiere_id>/deactivate', methods=['PUT'])
@token_required
def deactivate_competence(current_user, matiere_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    comp = ProfilCompetence.query.filter_by(
        profile_id=profile.id,
        matiere_id=matiere_id
    ).first()
    if not comp:
        return jsonify({"message": "Compétence introuvable"}), 404

    comp.is_available_to_help = False
    db.session.commit()
    return jsonify({"message": "Compétence désactivée pour l'aide", "is_available_to_help": comp.is_available_to_help}), 200


# ─── GET /api/matieres ─────────────────────────────────────────────────────
@profile_bp.route('/matieres', methods=['GET'])
def get_matieres():
    try:
        matieres = Matiere.query.order_by(Matiere.nom.asc()).all()
    except ProgrammingError as e:
        logger.warning('Matieres table missing or not initialized: %s', e)
        db.session.rollback()
        return jsonify([]), 200

    result = [
        {
            "id": m.id,
            "nom": m.nom,
            "annee": m.annee,
            "filiere": m.filiere
        }
        for m in matieres
    ]
    return jsonify(result), 200

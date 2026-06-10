# backend/app/routes/profile.py
import logging

from app.database import db
from app.middleware.auth_guard import token_required
from app.models import (
    Demand,
    Disponible,
    Matching,
    Matiere,
    ProfilCompetence,
    Profile,
    ProfilLacune,
    User,
)
from app.validators import (
    is_valid_competence_level,
    is_valid_day,
    normalize_format_preference,
    is_valid_priority_level,
    matiere_exists,
)
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, ProgrammingError

logger = logging.getLogger(__name__)
profile_bp = Blueprint("profile", __name__)
CRENEAUX_VALIDES = [
    "08-09",
    "09-10",
    "10-11",
    "11-12",
    "12-13",
    "13-14",
    "14-15",
    "15-16",
    "16-17",
    "17-18",
    "18-19",
    "19-20",
    "20-21",
    "21-22",
]


# ─── GET /api/profile/me ────────────────────────────────────────────────────
@profile_bp.route("/profile/me", methods=["GET"])
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
        competences_data.append(
            {
                "matiere_id": c.matiere_id,
                "matiere_nom": matiere.nom if matiere else "",
                "niveau": c.niveau,
                "is_available_to_help": c.is_available_to_help,
            }
        )

    # Lacunes
    lacunes = ProfilLacune.query.filter_by(profile_id=profile.id).all()
    lacunes_data = []
    for l in lacunes:
        matiere = db.session.get(Matiere, l.matiere_id)
        lacunes_data.append(
            {
                "matiere_id": l.matiere_id,
                "matiere_nom": matiere.nom if matiere else "",
                "priorite": l.priorite,
            }
        )

    # Disponibilités
    dispos = Disponible.query.filter_by(profile_id=profile.id).all()
    dispos_data = [
        {"jour": d.jour, "creneau": d.creneau, "is_reserved": d.is_reserved}
        for d in dispos
    ]

    return jsonify(
        {
            "id": profile.id,
            "user_id": current_user.id,
            "email": current_user.email,
            "email_verified": current_user.email_verified,
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
            "disponibilites": dispos_data,
        }
    ), 200


# ─── POST /api/profile/lacunes ─────────────────────────────────────────────
@profile_bp.route("/profile/lacunes", methods=["POST"])
@token_required
def add_lacune(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    matiere_id = data.get("matiere_id")

    # 🆕 CHECK CROISÉ : la matière est-elle déjà une compétence ?
    competence_existante = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if competence_existante:
        return jsonify(
            {
                "message": "Cette matière est déjà dans tes compétences. Supprime-la d'abord avant de l'ajouter en lacune."
            }
        ), 400

    priorite = data.get("priorite", "Moyenne")

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    if not is_valid_priority_level(priorite):
        return jsonify({"message": "Priorité invalide"}), 400

    existing = ProfilLacune.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if existing:
        return jsonify({"message": "Lacune déjà ajoutée"}), 400

    lacune = ProfilLacune(
        profile_id=profile.id, matiere_id=matiere_id, priorite=priorite
    )
    db.session.add(lacune)
    db.session.commit()

    return jsonify({"message": "Lacune ajoutée"}), 201


# ─── DELETE /api/profile/lacunes ────────────────────────────────────────────
@profile_bp.route("/profile/lacunes", methods=["DELETE"])
@token_required
def remove_lacune(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    matiere_id = data.get("matiere_id")

    lacune = ProfilLacune.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if not lacune:
        return jsonify({"message": "Lacune introuvable"}), 404

    db.session.delete(lacune)

    # Supprimer les demandes non résolues liées à cette lacune
    demands = Demand.query.filter_by(profile_id=profile.id, matiere_id=matiere_id).all()
    for demand in demands:
        accepted = Matching.query.filter_by(
            demand_id=demand.id, status="accepted"
        ).first()
        if not accepted:
            db.session.delete(demand)

    db.session.commit()
    return jsonify(
        {"message": "Lacune et demandes non résolues associées supprimées"}
    ), 200


# ─── PUT /api/profile/me ────────────────────────────────────────────────────
@profile_bp.route("/profile/me", methods=["PUT"])
@token_required
def update_my_profile(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()

    # Mise à jour des champs simples
    if data.get("nom"):
        profile.nom = data["nom"]
    if data.get("prenom"):
        profile.prenom = data["prenom"]
    if data.get("filiere"):
        profile.filiere = data["filiere"]
    if data.get("niveau"):
        profile.niveau = data["niveau"]
    if "bio" in data:
        profile.bio = data["bio"]
    if "avatar_url" in data:
        profile.avatar_url = data["avatar_url"]
    if "telephone" in data and data["telephone"]:
        existing = Profile.query.filter(
            Profile.telephone == data["telephone"], Profile.id != profile.id
        ).first()
        if existing:
            return jsonify({"message": "Ce numéro est déjà utilisé"}), 400
        profile.telephone = data["telephone"]
    if "disponible" in data:
        profile.disponible = data["disponible"]
    if "format_preference" in data:
        format_preference = normalize_format_preference(data["format_preference"])
        if not format_preference:
            return jsonify({"message": "Format d'apprentissage invalide"}), 400
        profile.format_preference = format_preference

    db.session.commit()
    return jsonify({"message": "Profil mis à jour avec succès"}), 200


# ─── PUT /api/profile/avatar/upload ──────────────────────────────────────────
@profile_bp.route("/profile/avatar/upload", methods=["POST"])
@token_required
def upload_avatar_file(current_user):
    """Upload un fichier image vers Cloudinary (ou fallback base64).

    Accepte multipart/form-data avec un champ 'file' (image).
    Retourne l'URL de l'avatar (Cloudinary ou base64 si fallback).
    ---
    tags: [Profil]
    consumes: [multipart/form-data]
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Fichier image (max 2 Mo)
    responses:
      200:
        description: URL de l'avatar
      400:
        description: Fichier manquant ou invalide
    """
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    if "file" not in request.files:
        return jsonify({"message": "Fichier requis (champ 'file')"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"message": "Fichier vide"}), 400

    file_data = file.read()
    if len(file_data) > 2 * 1024 * 1024:
        return jsonify({"message": "Image trop grande. Maximum 2 Mo."}), 400

    from app.services.cloudinary_service import upload_avatar as cloud_upload
    public_id = f"user_{current_user.id}"
    url = cloud_upload(file_data, public_id=public_id)

    if url:
        profile.avatar_url = url
    else:
        import base64
        b64 = base64.b64encode(file_data).decode("utf-8")
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif"}.get(ext, "image/jpeg")
        profile.avatar_url = f"data:{mime};base64,{b64}"

    db.session.commit()

    competences = ProfilCompetence.query.filter_by(profile_id=profile.id).all()
    lacunes = ProfilLacune.query.filter_by(profile_id=profile.id).all()
    return jsonify({
        "message": "Avatar enregistré avec succès",
        "avatar_url": profile.avatar_url,
        "storage": "cloudinary" if url else "base64",
    }), 200


# ─── PUT /api/profile/avatar ────────────────────────────────────────────────
@profile_bp.route("/profile/avatar", methods=["PUT"])
@token_required
def update_avatar(current_user):
    """Met à jour UNIQUEMENT l'avatar. Retourne le profil complet pour vérification."""
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json(silent=True)
    if not data or "avatar_url" not in data:
        return jsonify({"message": "avatar_url requis"}), 400

    avatar_url = data["avatar_url"]
    if not avatar_url or not isinstance(avatar_url, str):
        return jsonify({"message": "avatar_url invalide"}), 400

    # Vérifie que c'est une data URL valide (commence par data:image/)
    if not avatar_url.startswith("data:image/"):
        return jsonify({"message": "Format d'image invalide. Utilisez une data URL (data:image/...)"}), 400

    profile.avatar_url = avatar_url
    db.session.commit()

    # Retourne le profil complet pour que le frontend puisse vérifier
    competences = ProfilCompetence.query.filter_by(profile_id=profile.id).all()
    lacunes = ProfilLacune.query.filter_by(profile_id=profile.id).all()
    return jsonify({
        "message": "Avatar enregistré avec succès",
        "profile": {
            "id": profile.id,
            "user_id": current_user.id,
            "email": current_user.email,
            "nom": profile.nom,
            "prenom": profile.prenom,
            "filiere": profile.filiere,
            "niveau": profile.niveau,
            "avatar_url": profile.avatar_url,
        }
    }), 200


# ─── POST /api/profile/disponibilites ───────────────────────────────────────
@profile_bp.route("/profile/disponibilites", methods=["POST"])
@token_required
def add_disponibilite(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    jour = data.get("jour")
    creneau = data.get("creneau")

    if not jour or not creneau:
        return jsonify({"message": "jour et creneau requis"}), 400

    jours_valides = {
        "Lundi",
        "Mardi",
        "Mercredi",
        "Jeudi",
        "Vendredi",
        "Samedi",
        "Dimanche",
    }
    if jour not in jours_valides:
        return jsonify({"message": "jour invalide"}), 400
    if creneau not in CRENEAUX_VALIDES:
        return jsonify({"message": "Créneau invalide"}), 400

    dispo = Disponible(profile_id=profile.id, jour=jour, creneau=creneau)
    db.session.add(dispo)
    db.session.commit()

    return jsonify({"message": "Disponibilité ajoutée"}), 201


# ─── DELETE /api/profile/disponibilites ─────────────────────────────────────
@profile_bp.route("/profile/disponibilites", methods=["DELETE"])
@token_required
def remove_disponibilite(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    data = request.get_json()
    jour = data.get("jour")
    creneau = data.get("creneau")

    dispo = Disponible.query.filter_by(
        profile_id=profile.id, jour=jour, creneau=creneau
    ).first()

    if not dispo:
        return jsonify({"message": "Disponibilité introuvable"}), 404

    db.session.delete(dispo)
    db.session.commit()
    return jsonify({"message": "Disponibilité supprimée"}), 200


# ─── POST /api/profile/competences ──────────────────────────────────────────
@profile_bp.route("/profile/competences", methods=["POST"])
@token_required
def add_competence(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404
    data = request.get_json()
    matiere_id = data.get("matiere_id")

    # 🆕 CHECK CROISÉ : la matière est-elle déjà une lacune ?
    lacune_existante = ProfilLacune.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if lacune_existante:
        return jsonify(
            {
                "message": "Cette matière est déjà dans tes lacunes. Supprime-la d'abord avant de l'ajouter en compétence."
            }
        ), 400

    niveau = data.get("niveau", "Intermédiaire")
    is_available_to_help = data.get("is_available_to_help", True)

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
        if is_available_to_help.lower() in ("true", "false"):
            is_available_to_help = is_available_to_help.lower() == "true"
        else:
            return jsonify(
                {"message": "is_available_to_help doit être true ou false"}
            ), 400
    else:
        is_available_to_help = bool(is_available_to_help)

    comp = ProfilCompetence(
        profile_id=profile.id,
        matiere_id=matiere_id,
        niveau=niveau,
        is_available_to_help=is_available_to_help,
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify({"message": "Compétence ajoutée"}), 201


# ─── DELETE /api/profile/competences ────────────────────────────────────────
@profile_bp.route("/profile/competences", methods=["DELETE"])
@token_required
def remove_competence(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404
    data = request.get_json()
    matiere_id = data.get("matiere_id")

    comp = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if not comp:
        return jsonify({"message": "Compétence introuvable"}), 404

    db.session.delete(comp)
    db.session.commit()
    return jsonify({"message": "Compétence supprimée"}), 200


# ─── PUT /api/profile/competences/<matiere_id>/activate ──────────────────
@profile_bp.route("/profile/competences/<int:matiere_id>/activate", methods=["PUT"])
@token_required
def activate_competence(current_user, matiere_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    comp = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if not comp:
        return jsonify({"message": "Compétence introuvable"}), 404

    comp.is_available_to_help = True
    db.session.commit()
    return jsonify(
        {
            "message": "Compétence activée pour l'aide",
            "is_available_to_help": comp.is_available_to_help,
        }
    ), 200


# ─── PUT /api/profile/competences/<matiere_id>/deactivate ───────────────
@profile_bp.route("/profile/competences/<int:matiere_id>/deactivate", methods=["PUT"])
@token_required
def deactivate_competence(current_user, matiere_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    comp = ProfilCompetence.query.filter_by(
        profile_id=profile.id, matiere_id=matiere_id
    ).first()
    if not comp:
        return jsonify({"message": "Compétence introuvable"}), 404

    comp.is_available_to_help = False
    db.session.commit()
    return jsonify(
        {
            "message": "Compétence désactivée pour l'aide",
            "is_available_to_help": comp.is_available_to_help,
        }
    ), 200


# ─── GET /api/matieres ─────────────────────────────────────────────────────
@profile_bp.route("/matieres", methods=["GET"])
def get_matieres():
    try:
        matieres = Matiere.query.order_by(Matiere.nom.asc()).all()
    except ProgrammingError as e:
        logger.warning("Matieres table missing or not initialized: %s", e)
        db.session.rollback()
        return jsonify([]), 200

    result = [
        {"id": m.id, "nom": m.nom, "annee": m.annee, "filiere": m.filiere}
        for m in matieres
    ]
    return jsonify(result), 200

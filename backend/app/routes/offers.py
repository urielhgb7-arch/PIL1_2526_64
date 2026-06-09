# backend/app/routes/offers.py
import re
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Profile
from app.models.services import Matching, Offer, Demand, ProfilLacune, ProfilCompetence
from app.middleware.auth_guard import token_required
from app.validators import is_valid_format_preference, matiere_exists, is_valid_day, is_valid_creneau, VALID_DAYS

logger = logging.getLogger(__name__)
offers_bp = Blueprint('offers', __name__)

FORMAT_PREFERENCE_MAP = {
    'En ligne': 'en_ligne',
    'en ligne': 'en_ligne',
    'Présentiel': 'presentiel',
    'présentiel': 'presentiel',
    'Hybride': 'hybride',
    'hybride': 'hybride'
}
VALID_URGENCIES = {'Low', 'Medium', 'High', 'Urgent'}
DAY_INDEX_TO_NAME = {
    0: 'Lundi',
    1: 'Mardi',
    2: 'Mercredi',
    3: 'Jeudi',
    4: 'Vendredi',
    5: 'Samedi',
    6: 'Dimanche'
}


def _parse_iso_slot(slot_iso):
    if not slot_iso or not isinstance(slot_iso, str):
        return None, None

    # Try "Jour-hH-hH" format (e.g. "Lundi-8h-9h")
    match = re.match(r'^(\w+)-(\d+)h-(\d+)h$', slot_iso.strip())
    if match:
        jour = match.group(1)
        debut = int(match.group(2))
        fin = int(match.group(3))
        if jour not in VALID_DAYS or debut < 0 or fin > 24 or fin - debut != 1:
            return None, None
        creneau = f'{debut:02d}-{fin:02d}'
        return jour, creneau

    # Try ISO datetime format
    try:
        if slot_iso.endswith('Z'):
            slot_iso = slot_iso[:-1] + '+00:00'
        dt = datetime.fromisoformat(slot_iso)
    except ValueError:
        return None, None

    jour = DAY_INDEX_TO_NAME.get(dt.weekday())
    heure = dt.hour
    creneau = f'{heure:02d}-{heure + 1:02d}'
    return jour, creneau


def _normalize_format_preference(value):
    if not value:
        return 'hybride'
    if value in FORMAT_PREFERENCE_MAP:
        return FORMAT_PREFERENCE_MAP[value]
    if is_valid_format_preference(value):
        return value
    return None


def _get_profile_or_404(user_id: int):
    """Récupère le profil associé à un user_id, ou lève une 404."""
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return None, jsonify({"message": "Profil introuvable"}), 404
    return profile, None, None


# ── POST /api/offers ─────────────────────────────────────────────────────────
@offers_bp.route('/offers', methods=['POST'])
@token_required
def create_offer(current_user):
    data = request.get_json(force=True, silent=True) or {}
    
    matiere_id = data.get('matiere_id')
    description = data.get('description', '')
    jour = data.get('jour')
    creneau = data.get('creneau')
    format_preference = data.get('format_preference', 'hybride')
    disponibilites = data.get('disponibilites') or data.get('disponibilite')

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    # Parse disponibilites if provided
    all_slots = []
    if disponibilites:
        if not isinstance(disponibilites, list) or len(disponibilites) == 0:
            return jsonify({"message": "disponibilites doit être une liste non vide"}), 400
        for slot in disponibilites:
            slot_jour, slot_creneau = _parse_iso_slot(slot)
            if not slot_jour or not slot_creneau:
                return jsonify({"message": "disponibilite invalide"}), 400
            if not is_valid_day(slot_jour):
                return jsonify({"message": "jour invalide"}), 400
            if not is_valid_creneau(slot_creneau):
                return jsonify({"message": "creneau invalide"}), 400
            all_slots.append({"jour": slot_jour, "creneau": slot_creneau})
    else:
        if jour and not is_valid_day(jour):
            return jsonify({"message": "jour invalide"}), 400
        if creneau and not is_valid_creneau(creneau):
            return jsonify({"message": "creneau invalide"}), 400
        if jour and creneau:
            all_slots.append({"jour": jour, "creneau": creneau})

    if not is_valid_format_preference(format_preference):
        return jsonify({"message": "format invalide"}), 400

    profile, error_response, error_status = _get_profile_or_404(current_user.id)
    if error_response:
        return error_response, error_status

    first_slot = all_slots[0] if all_slots else {}

    offer = Offer(
        profile_id=profile.id,
        matiere_id=matiere_id,
        description=description,
        jour=first_slot.get('jour'),
        creneau=first_slot.get('creneau'),
        format_preference=format_preference,
        disponibilites=all_slots
    )
    db.session.add(offer)
    db.session.commit()
    logger.info(f"Offre créée: profile_id={profile.id} matiere_id={matiere_id}")
    return jsonify({"message": "Offre créée avec succès", "id": offer.id}), 201

# ── GET /api/offers ──────────────────────────────────────────────────────────
@offers_bp.route('/offers', methods=['GET'])
def get_offers():
    matiere_id = request.args.get('matiere_id', type=int)
    jour = request.args.get('jour')
    creneau = request.args.get('creneau')
    format_pref = request.args.get('format_preference')

    query = Offer.query
    if matiere_id:
        query = query.filter_by(matiere_id=matiere_id)
    if jour:
        query = query.filter_by(jour=jour)
    if creneau:
        query = query.filter_by(creneau=creneau)
    if format_pref:
        query = query.filter_by(format_preference=format_pref)

    offers = query.all()
    result = []
    for o in offers:
        profile = Profile.query.get(o.profile_id)
        publicateur = None
        if profile:
            publicateur = {"user_id": profile.user_id, "nom": profile.nom, "prenom": profile.prenom}
        result.append({
            "id": o.id,
            "profile_id": o.profile_id,
            "matiere_id": o.matiere_id,
            "matiere_nom": o.matiere.nom if o.matiere else None,
            "description": o.description,
            "jour": o.jour,
            "creneau": o.creneau,
            "format_preference": o.format_preference,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "publicateur": publicateur
        })
    return jsonify(result), 200


# ── GET /api/offers/mine ─────────────────────────────────────────────────────
@offers_bp.route('/offers/mine', methods=['GET'])
@token_required
def get_my_offers(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404
    offers = Offer.query.filter_by(profile_id=profile.id).all()
    result = []
    for o in offers:
        result.append({
            "id": o.id,
            "matiere_id": o.matiere_id,
            "matiere_nom": o.matiere.nom if o.matiere else None,
            "description": o.description,
            "jour": o.jour,
            "creneau": o.creneau,
            "format_preference": o.format_preference,
            "created_at": o.created_at.isoformat() if o.created_at else None
        })
    return jsonify(result), 200


# ── GET /api/demands/mine ────────────────────────────────────────────────────
@offers_bp.route('/demands/mine', methods=['GET'])
@token_required
def get_my_demands(current_user):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404
    demands = Demand.query.filter_by(profile_id=profile.id).all()
    result = []
    for d in demands:
        result.append({
            "id": d.id,
            "matiere_id": d.matiere_id,
            "matiere_nom": d.matiere.nom if d.matiere else None,
            "jour": d.jour,
            "creneau": d.creneau,
            "description": d.description,
            "created_at": d.created_at.isoformat() if d.created_at else None
        })
    return jsonify(result), 200


# ── DELETE /api/offers/<id> ──────────────────────────────────────────────────
@offers_bp.route('/offers/<int:offer_id>', methods=['DELETE'])
@token_required
def delete_offer(current_user, offer_id):
    offer = db.session.get(Offer, offer_id)
    if not offer:
        return jsonify({"message": "Offre introuvable"}), 404

    profile, error_response, error_status = _get_profile_or_404(current_user.id)
    if error_response:
        return error_response, error_status

    if offer.profile_id != profile.id:
        return jsonify({"message": "Non autorisé"}), 403

    db.session.delete(offer)
    db.session.commit()
    logger.info(f"Offre supprimée: id={offer_id}")
    return jsonify({"message": "Offre supprimée"}), 200


# ── POST /api/demands ────────────────────────────────────────────────────────
@offers_bp.route('/demands', methods=['POST'])
@token_required
def create_demand(current_user):
    data = request.get_json(force=True, silent=True) or {}
    matiere_id = data.get('matiere_id')
    jour = data.get('jour')
    creneau = data.get('creneau')
    description = data.get('description', '')
    disponibilite = data.get('disponibilite') or data.get('disponibilites')
    urgence = data.get('urgence')
    format_pref = data.get('format')

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    if not disponibilite and (not jour or not creneau):
        return jsonify({"message": "jour et creneau requis"}), 400

    if disponibilite:
        if not isinstance(disponibilite, list) or len(disponibilite) == 0:
            return jsonify({"message": "disponibilite doit être une liste non vide"}), 400

    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    if format_pref:
        format_pref = _normalize_format_preference(format_pref)
        if not format_pref:
            return jsonify({"message": "format invalide"}), 400

    if urgence and urgence not in VALID_URGENCIES:
        return jsonify({"message": "urgence invalide"}), 400

    profile, error_response, error_status = _get_profile_or_404(current_user.id)
    if error_response:
        return error_response, error_status

    all_slots = []
    if disponibilite:
        if not isinstance(disponibilite, list) or len(disponibilite) == 0:
            return jsonify({"message": "disponibilite doit être une liste non vide"}), 400
        for slot_iso in disponibilite:
            slot_jour, slot_creneau = _parse_iso_slot(slot_iso)
            if not slot_jour or not slot_creneau:
                return jsonify({"message": "disponibilite invalide"}), 400
            if not is_valid_day(slot_jour):
                return jsonify({"message": "jour invalide"}), 400
            if not is_valid_creneau(slot_creneau):
                return jsonify({"message": "creneau invalide"}), 400
            all_slots.append({"jour": slot_jour, "creneau": slot_creneau})
    else:
        if jour and not is_valid_day(jour):
            return jsonify({"message": "jour invalide"}), 400
        if creneau and not is_valid_creneau(creneau):
            return jsonify({"message": "creneau invalide"}), 400
        if jour and creneau:
            all_slots.append({"jour": jour, "creneau": creneau})

    first_slot = all_slots[0] if all_slots else {}

    demand = Demand(
        profile_id=profile.id,
        matiere_id=matiere_id,
        jour=first_slot.get('jour'),
        creneau=first_slot.get('creneau'),
        description=description,
        disponibilites=all_slots
    )
    db.session.add(demand)
    db.session.commit()
    logger.info(f"Demande créée: profile_id={profile.id} matiere_id={matiere_id} id={demand.id}")
    return jsonify({"message": "Demande créée avec succès", "id": demand.id}), 201


# ── GET /api/demands ─────────────────────────────────────────────────────────
@offers_bp.route('/demands', methods=['GET'])
def get_demands():
    demands = Demand.query.all()
    result = []
    for d in demands:
        profile = Profile.query.get(d.profile_id)
        publicateur = None
        if profile:
            publicateur = {"user_id": profile.user_id, "nom": profile.nom, "prenom": profile.prenom}
        result.append({
            "id": d.id,
            "profile_id": d.profile_id,
            "matiere_id": d.matiere_id,
            "matiere_nom": d.matiere.nom if d.matiere else None,
            "jour": d.jour,
            "creneau": d.creneau,
            "description": d.description,
            "created_at": d.created_at.isoformat(),
            "publicateur": publicateur
        })
    return jsonify(result), 200


# ── DELETE /api/demands/<id> ─────────────────────────────────────────────────
@offers_bp.route('/demands/<int:demand_id>', methods=['DELETE'])
@token_required
def delete_demand(current_user, demand_id):
    demand = db.session.get(Demand, demand_id)
    if not demand:
        return jsonify({"message": "Demande introuvable"}), 404

    profile, error_response, error_status = _get_profile_or_404(current_user.id)
    if error_response:
        return error_response, error_status

    if demand.profile_id != profile.id:
        return jsonify({"message": "Non autorisé"}), 403

    db.session.delete(demand)
    db.session.commit()
    logger.info(f"Demande supprimée: id={demand_id}")
    return jsonify({"message": "Demande supprimée"}), 200

# backend/app/routes/offers.py
@offers_bp.route('/offers/<int:offer_id>/respond', methods=['POST'])
@token_required
def respond_to_offer(current_user, offer_id):
    """Un étudiant avec une lacune répond à une offre de mentorat"""
    offer = db.session.get(Offer, offer_id)
    if not offer:
        return jsonify({"message": "Offre introuvable"}), 404

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    # Vérifier que l'étudiant a bien une lacune sur cette matière
    lacune = ProfilLacune.query.filter_by(
        profile_id=profile.id,
        matiere_id=offer.matiere_id
    ).first()
    if not lacune:
        return jsonify({"message": "Vous n'avez pas de lacune sur cette matière"}), 400

    # Créer une demande pour ce matching (réutiliser le flow existant)
    demand = Demand(
        profile_id=profile.id,
        matiere_id=offer.matiere_id,
        jour=offer.jour or '',
        creneau=offer.creneau or '',
        description=f"Réponse à l'offre #{offer_id}"
    )
    db.session.add(demand)
    db.session.flush()

    # Créer le matching directement
    offrant_user_id = Profile.query.get(offer.profile_id).user_id
    new_match = Matching(
        user_one_id=current_user.id,
        user_two_id=offrant_user_id,
        initiator_id=current_user.id,
        demand_id=demand.id,
        offer_id=offer.id,
        matiere_id=offer.matiere_id,
        score=0.0,
        status='pending'
    )
    db.session.add(new_match)
    db.session.commit()

    return jsonify({
        "message": "Réponse envoyée au mentor",
        "matching_id": new_match.id
    }), 201


# ── POST /api/demands/<demand_id>/offer-help ──────────────────────────────────
@offers_bp.route('/demands/<int:demand_id>/offer-help', methods=['POST'])
@token_required
def offer_help_on_demand(current_user, demand_id):
    """Un étudiant avec une compétence propose son aide sur une demande"""
    demand = db.session.get(Demand, demand_id)
    if not demand:
        return jsonify({"message": "Demande introuvable"}), 404

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Profil introuvable"}), 404

    competence = ProfilCompetence.query.filter_by(
        profile_id=profile.id,
        matiere_id=demand.matiere_id
    ).first()
    if not competence:
        return jsonify({"message": "Vous n'avez pas de compétence sur cette matière"}), 400

    demandeur_profile = Profile.query.get(demand.profile_id)
    if not demandeur_profile:
        return jsonify({"message": "Profil du demandeur introuvable"}), 404

    existing = Matching.query.filter_by(
        user_one_id=current_user.id,
        user_two_id=demandeur_profile.user_id,
        demand_id=demand_id
    ).first()
    if existing:
        return jsonify({"message": "Aide déjà proposée", "matching_id": existing.id, "status": existing.status}), 200

    new_match = Matching(
        user_one_id=current_user.id,
        user_two_id=demandeur_profile.user_id,
        initiator_id=current_user.id,
        demand_id=demand_id,
        matiere_id=demand.matiere_id,
        score=0.0,
        status='pending'
    )
    db.session.add(new_match)
    db.session.commit()

    return jsonify({"message": "Aide proposée avec succès", "matching_id": new_match.id}), 201
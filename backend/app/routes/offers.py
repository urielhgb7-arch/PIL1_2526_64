# backend/app/routes/offers.py
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Profile
from app.models.services import Offer, Demand
from app.middleware.auth_guard import token_required
from app.validators import matiere_exists, is_valid_day, is_valid_creneau

logger = logging.getLogger(__name__)
offers_bp = Blueprint('offers', __name__)


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

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    profile, error_response, error_status = _get_profile_or_404(current_user.id)
    if error_response:
        return error_response, error_status

    offer = Offer(
        profile_id=profile.id,
        matiere_id=matiere_id,
        description=description
    )
    db.session.add(offer)
    db.session.commit()
    logger.info(f"Offre créée: profile_id={profile.id} matiere_id={matiere_id}")
    return jsonify({"message": "Offre créée avec succès", "id": offer.id}), 201


# ── GET /api/offers ──────────────────────────────────────────────────────────
@offers_bp.route('/offers', methods=['GET'])
def get_offers():
    offers = Offer.query.all()
    return jsonify([{
        "id": o.id,
        "profile_id": o.profile_id,
        "matiere_id": o.matiere_id,
        "matiere_nom": o.matiere.nom if o.matiere else None,
        "description": o.description,
        "created_at": o.created_at.isoformat()
    } for o in offers]), 200


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

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400
    if not jour or not creneau:
        return jsonify({"message": "jour et creneau requis"}), 400
    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404
    if not is_valid_day(jour):
        return jsonify({"message": "jour invalide"}), 400
    if not is_valid_creneau(creneau):
        return jsonify({"message": "creneau invalide"}), 400

    profile, error_response, error_status = _get_profile_or_404(current_user.id)
    if error_response:
        return error_response, error_status

    demand = Demand(
        profile_id=profile.id,
        matiere_id=matiere_id,
        jour=jour,
        creneau=creneau,
        description=description
    )
    db.session.add(demand)
    db.session.commit()
    logger.info(f"Demande créée: profile_id={profile.id} matiere_id={matiere_id}")
    return jsonify({"message": "Demande créée avec succès", "id": demand.id}), 201


# ── GET /api/demands ─────────────────────────────────────────────────────────
@offers_bp.route('/demands', methods=['GET'])
def get_demands():
    demands = Demand.query.all()
    return jsonify([{
        "id": d.id,
        "profile_id": d.profile_id,
        "matiere_id": d.matiere_id,
        "matiere_nom": d.matiere.nom if d.matiere else None,
        "jour": d.jour,
        "creneau": d.creneau,
        "description": d.description,
        "created_at": d.created_at.isoformat()
    } for d in demands]), 200


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
# backend/app/routes/matching.py
# ============================================================
# ROUTES MATCHING — IFRI MENTORLINK
# Endpoints : suggestions, accept, reject
# Conforme à : IFRI_Mentorlink_Vision_du_Système_de_Matching.pdf
# ============================================================

import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Profile, Conversation, Notification
from app.models.profile import Disponible
from app.models.services import Matching, ProfilCompetence, Demand, Matiere
from app.services.matching import calculate_matches
from app.validators import matiere_exists

logger = logging.getLogger(__name__)

matching_bp = Blueprint('matching', __name__)


# ── GET /api/matches/suggestions ────────────────────────────────────────────
# Section 5 & 10 du PDF : déclenchement du matching + affichage des résultats
@matching_bp.route('/matches/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    current_user_id = int(get_jwt_identity())

    # Filtre optionnel sur une matière précise (?matiere_id=1)
    demand_id = request.args.get('demand_id', type=int)
    matiere_id = request.args.get('matiere_id', type=int)

    if demand_id:
        demand = db.session.get(Demand, demand_id)
        profile = Profile.query.filter_by(user_id=current_user_id).first()
        if not demand or not profile or demand.profile_id != profile.id:
            return jsonify({"message": "Demande introuvable ou non autorisée"}), 404
        resultats = calculate_matches(current_user_id, demand_id=demand_id)
    else:
        resultats = calculate_matches(current_user_id, matiere_id=matiere_id)

    if not resultats:
        return jsonify({
            "message": "Aucun candidat trouvé. Complétez vos lacunes et disponibilités.",
            "matches": [],
            "total": 0
        }), 200

    # Pagination manuelle (le calcul se fait en mémoire)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    total = len(resultats)
    start = (page - 1) * per_page
    end = start + per_page
    page_results = resultats[start:end]

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": -(-total // per_page),  # ceil division
        "matches": page_results
    }), 200


# ── POST /api/matches/<student_id>/request ───────────────────────────────────
# Section 12 du PDF : swipe droite → création du matching en statut 'pending'
@matching_bp.route('/matches/<int:student_id>/request', methods=['POST'])
@jwt_required()
def request_match(student_id):
    current_user_id = int(get_jwt_identity())

    if current_user_id == student_id:
        return jsonify({"message": "Vous ne pouvez pas vous matcher avec vous-même"}), 400

    data = request.get_json(force=True, silent=True) or {}
    demand_id = data.get('demand_id')
    score     = data.get('score', 0.0)

    if not demand_id:
        return jsonify({"message": "demand_id requis"}), 400

    demand = db.session.get(Demand, demand_id)
    if not demand:
        return jsonify({"message": "Demande introuvable"}), 404
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile or demand.profile_id != profile.id:
        return jsonify({"message": "Non autorisé sur cette demande"}), 403

    # Vérifier que le candidat existe
    candidate = db.session.get(User, student_id)
    if not candidate:
        return jsonify({"message": "Candidat introuvable"}), 404

    # Vérifier qu'un matching n'existe pas déjà entre ces deux sur cette demande
    existing = Matching.query.filter_by(
        user_one_id=current_user_id,
        user_two_id=student_id,
        demand_id=demand_id
    ).first()
    if existing:
        return jsonify({
            "message": "Demande déjà envoyée",
            "matching_id": existing.id,
            "status": existing.status
        }), 200

    # Vérifier que le candidat dispose bien du créneau demandé et qu'il n'est pas réservé
    candidate_profile = Profile.query.filter_by(user_id=student_id).first()
    if not candidate_profile:
        return jsonify({"message": "Profil du candidat introuvable"}), 404

    candidate_slot = Disponible.query.filter_by(
        profile_id=candidate_profile.id,
        jour=demand.jour,
        creneau=demand.creneau,
        is_reserved=False
    ).first()
    if not candidate_slot:
        return jsonify({"message": "Le candidat n'est pas disponible sur ce créneau"}), 400

    # Créer le matching en statut 'pending'
    new_match = Matching(
        user_one_id=current_user_id,
        user_two_id=student_id,
        initiator_id=current_user_id,
        demand_id=demand_id,
        matiere_id=demand.matiere_id,
        score=score,
        status='pending'
    )
    db.session.add(new_match)
    db.session.flush()  # obtenir new_match.id avant commit
    # Notifier le candidat (Section 13 du PDF)
    demandeur = db.session.get(User, current_user_id)
    demandeur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    notif = Notification(
        user_id=student_id,
        titre="Nouvelle demande d'accompagnement",
        contenu=f"{demandeur_profile.prenom} {demandeur_profile.nom} souhaite votre aide. Compatibilité : {score}%",
        type='match_system'
    )
    db.session.add(notif)
    db.session.commit()

    # Email au candidat
    try:
        from app.services.email_service import send_match_notification_email
        from flask import current_app as app
        candidat_user = db.session.get(User, student_id)
        if candidat_user and candidat_user.email:
            send_match_notification_email(
                recipient_email=candidat_user.email,
                subject="Nouvelle demande d'accompagnement",
                sender_name=f"{demandeur_profile.prenom} {demandeur_profile.nom}",
                score=score,
                match_type="request",
                accept_url=f"{app.config.get('FRONTEND_URL', 'http://localhost:5500')}/pages/dashboard.html",
            )
    except Exception as e:
        logger.warning(f"Email request notif skipped: {e}")

    return jsonify({
        "message": "Demande envoyée avec succès",
        "matching_id": new_match.id,
        "status": "pending"
    }), 201


# ── POST /api/matches/<matching_id>/accept ───────────────────────────────────
# Section 14 du PDF : acceptation → statut 'accepted' + conversation créée
@matching_bp.route('/matches/<int:matching_id>/accept', methods=['POST'])
@jwt_required()
def accept_match(matching_id):
    current_user_id = int(get_jwt_identity())

    match = db.session.get(Matching, matching_id)
    if not match:
        return jsonify({"message": "Matching introuvable"}), 404

    # Seul le destinataire (user_two) peut accepter
    if match.user_two_id != current_user_id:
        return jsonify({"message": "Non autorisé"}), 403

    if match.status != 'pending':
        return jsonify({"message": f"Ce matching est déjà '{match.status}'"}), 400

    # Mettre à jour le statut
    match.status = 'accepted'

    # Créer la conversation automatiquement (Section 14 du PDF)
    existing_conv = Conversation.query.filter_by(
        user_one_id=match.user_one_id,
        user_two_id=match.user_two_id
    ).first() or Conversation.query.filter_by(
        user_one_id=match.user_two_id,
        user_two_id=match.user_one_id
    ).first()

    if not existing_conv:
        conv = Conversation(
            user_one_id=match.user_one_id,
            user_two_id=match.user_two_id
        )
        db.session.add(conv)
        db.session.flush()  # Pour obtenir conv.id avant le commit
        conversation_id = conv.id
    else:
        conversation_id = existing_conv.id

    # --- Réserver le créneau de l'aidant pour cette demande ---
    demand = db.session.get(Demand, match.demand_id)
    if not demand:
        return jsonify({"message": "Demande associée introuvable"}), 404

    helper_profile = Profile.query.filter_by(user_id=match.user_two_id).first()
    if helper_profile:
        helper_slot = Disponible.query.filter_by(
            profile_id=helper_profile.id,
            jour=demand.jour,
            creneau=demand.creneau,
            is_reserved=False
        ).first()
        if not helper_slot:
            return jsonify({"message": "Ce créneau n'est plus disponible"}), 400
        helper_slot.is_reserved = True

    # Notifier le demandeur que sa demande a été acceptée
    accepteur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    notif = Notification(
        user_id=match.user_one_id,
        titre="Demande acceptée !",
        contenu=f"{accepteur_profile.prenom} {accepteur_profile.nom} a accepté votre demande d'aide.",
        type='match_system'
    )
    db.session.add(notif)
    db.session.commit()

    # Email au demandeur
    try:
        from app.services.email_service import send_match_notification_email
        from flask import current_app as app
        demandeur_user = db.session.get(User, match.user_one_id)
        if demandeur_user and demandeur_user.email:
            send_match_notification_email(
                recipient_email=demandeur_user.email,
                subject="Demande acceptée !",
                sender_name=f"{accepteur_profile.prenom} {accepteur_profile.nom}",
                score=match.score,
                match_type="accept",
                accept_url=f"{app.config.get('FRONTEND_URL', 'http://localhost:5500')}/pages/dashboard.html",
            )
    except Exception as e:
        logger.warning(f"Email accept notif skipped: {e}")

    return jsonify({
        "message": "Match accepté ! Vous pouvez maintenant discuter.",
        "status": "accepted",
        "conversation_id": conversation_id
    }), 200


# ── POST /api/matches/<matching_id>/reject ───────────────────────────────────
# Section 15 du PDF : refus → statut 'rejected' + notification au demandeur
@matching_bp.route('/matches/<int:matching_id>/reject', methods=['POST'])
@jwt_required()
def reject_match(matching_id):
    current_user_id = int(get_jwt_identity())

    match = db.session.get(Matching, matching_id)
    if not match:
        return jsonify({"message": "Matching introuvable"}), 404

    # Seul le destinataire peut refuser
    if match.user_two_id != current_user_id:
        return jsonify({"message": "Non autorisé"}), 403

    if match.status != 'pending':
        return jsonify({"message": f"Ce matching est déjà '{match.status}'"}), 400

    match.status = 'rejected'

    # Notifier le demandeur du refus (Section 15 du PDF)
    refuseur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    notif = Notification(
        user_id=match.user_one_id,
        titre="Demande refusée",
        contenu=f"{refuseur_profile.prenom} {refuseur_profile.nom} n'est pas disponible pour le moment.",
        type='match_system'
    )
    db.session.add(notif)
    db.session.commit()

    # Email au demandeur
    try:
        from app.services.email_service import send_match_notification_email
        from flask import current_app as app
        demandeur_user = db.session.get(User, match.user_one_id)
        if demandeur_user and demandeur_user.email:
            send_match_notification_email(
                recipient_email=demandeur_user.email,
                subject="Demande refusée",
                sender_name=f"{refuseur_profile.prenom} {refuseur_profile.nom}",
                score=match.score,
                match_type="reject",
                accept_url=None,
            )
    except Exception as e:
        logger.warning(f"Email reject notif skipped: {e}")

    return jsonify({
        "message": "Match refusé.",
        "status": "rejected"
    }), 200


# ── GET /api/matches/received ────────────────────────────────────────────────
# Voir les demandes reçues en attente (pour le candidat)
@matching_bp.route('/matches/received', methods=['GET'])
@jwt_required()
def get_received_matches():
    current_user_id = int(get_jwt_identity())

    matches = Matching.query.filter_by(
        user_two_id=current_user_id
    ).order_by(Matching.created_at.desc()).all()

    result = []
    for m in matches:
        initiator_profile = Profile.query.filter_by(user_id=m.user_one_id).first()
        matiere_obj = db.session.get(Matiere, m.matiere_id)
        result.append({
            "matching_id": m.id,
            "demand_id": m.demand_id,
            "offer_id": m.offer_id,
            "initiator": {
                "user_id": m.user_one_id,
                "nom":     initiator_profile.nom if initiator_profile else "",
                "prenom":  initiator_profile.prenom if initiator_profile else "",
            },
            "matiere_id": m.matiere_id,
            "matiere_nom": matiere_obj.nom if matiere_obj else "",
            "jour": m.demand.jour if m.demand else None,
            "creneau": m.demand.creneau if m.demand else None,
            "score":      m.score,
            "status":     m.status,
            "created_at": m.created_at.isoformat()
        })

    return jsonify(result), 200


# ── GET /api/matches/sent ────────────────────────────────────────────────────
# Voir les demandes envoyées (pour le demandeur)
@matching_bp.route('/matches/sent', methods=['GET'])
@jwt_required()
def get_sent_matches():
    current_user_id = int(get_jwt_identity())

    matches = Matching.query.filter_by(
        user_one_id=current_user_id
    ).order_by(Matching.created_at.desc()).all()

    result = []
    for m in matches:
        candidat_profile = Profile.query.filter_by(user_id=m.user_two_id).first()
        result.append({
            "matching_id": m.id,
            "candidat": {
                "user_id": m.user_two_id,
                "nom":     candidat_profile.nom if candidat_profile else "",
                "prenom":  candidat_profile.prenom if candidat_profile else "",
            },
            "matiere_id": m.matiere_id,
            "jour": m.demand.jour if m.demand else None,
            "creneau": m.demand.creneau if m.demand else None,
            "score":      m.score,
            "status":     m.status,
            "created_at": m.created_at.isoformat()
        })

    return jsonify(result), 200
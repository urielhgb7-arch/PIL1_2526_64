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
    matiere_id = data.get('matiere_id')
    score     = data.get('score', 0.0)

    candidate = db.session.get(User, student_id)
    if not candidate:
        return jsonify({"message": "Candidat introuvable"}), 404

    profile = Profile.query.filter_by(user_id=current_user_id).first()

    # Vérifications liées à la demande (optionnel)
    if demand_id:
        demand = db.session.get(Demand, demand_id)
        if not demand:
            return jsonify({"message": "Demande introuvable"}), 404
        if not profile or demand.profile_id != profile.id:
            return jsonify({"message": "Non autorisé sur cette demande"}), 403

        matiere_id = demand.matiere_id

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
    else:
        # Matching général (sans demande spécifique) : éviter les doublons
        existing = Matching.query.filter_by(
            user_one_id=current_user_id,
            user_two_id=student_id,
            initiator_id=current_user_id,
            status='pending'
        ).first()
        if existing:
            return jsonify({
                "message": "Demande déjà envoyée",
                "matching_id": existing.id,
                "status": existing.status
            }), 200

    new_match = Matching(
        user_one_id=current_user_id,
        user_two_id=student_id,
        initiator_id=current_user_id,
        demand_id=demand_id,
        matiere_id=matiere_id,
        score=score,
        status='pending'
    )
    db.session.add(new_match)
    db.session.flush()

    demandeur_profile = profile or Profile.query.filter_by(user_id=current_user_id).first()
    matiere_nom = Matiere.query.get(matiere_id).nom if matiere_id else None
    sujet = f" en {matiere_nom}" if matiere_nom else ""
    notif = Notification(
        user_id=student_id,
        titre="Nouvelle demande de mentorat",
        contenu=f"{demandeur_profile.prenom} {demandeur_profile.nom} souhaite que vous le mentoriez{sujet}.",
        type='matching'
    )
    db.session.add(notif)
    db.session.commit()
    logger.info(f"Match request commit OK: user_one={current_user_id}, user_two={student_id}, matching_id={new_match.id}, demand_id={demand_id}")

    try:
        from app.services.email_service import send_match_notification_email
        from flask import current_app as app
        if candidate and candidate.email:
            send_match_notification_email(
                recipient_email=candidate.email,
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


# ── POST /api/matches/<student_id>/skip ───────────────────────────────────────
# Swipe gauche → enregistre un rejet pour ne plus revoir ce profil
@matching_bp.route('/matches/<int:student_id>/skip', methods=['POST'])
@jwt_required()
def skip_match(student_id):
    current_user_id = int(get_jwt_identity())

    if current_user_id == student_id:
        return jsonify({"message": "Vous ne pouvez pas vous ignorer vous-même"}), 400

    data = request.get_json(force=True, silent=True) or {}
    demand_id = data.get('demand_id')

    if not demand_id:
        return jsonify({"message": "demand_id est requis"}), 400

    profile = Profile.query.filter_by(user_id=current_user_id).first()
    demand = db.session.get(Demand, demand_id)
    if not demand or not profile or demand.profile_id != profile.id:
        return jsonify({"message": "Demande introuvable ou non autorisée"}), 404

    existing = Matching.query.filter_by(
        user_one_id=current_user_id,
        user_two_id=student_id,
        demand_id=demand_id
    ).first()

    if existing:
        if existing.status == 'pending':
            existing.status = 'rejected'
            db.session.commit()
            return jsonify({"message": "Demande annulée", "status": "rejected"}), 200
        elif existing.status == 'rejected':
            return jsonify({"message": "Déjà ignoré", "status": "rejected"}), 200
        else:
            return jsonify({"message": f"Impossible d'ignorer (statut: {existing.status})"}), 400

    new_match = Matching(
        user_one_id=current_user_id,
        user_two_id=student_id,
        initiator_id=current_user_id,
        demand_id=demand_id,
        matiere_id=demand.matiere_id,
        score=0,
        status='rejected'
    )
    db.session.add(new_match)
    db.session.commit()

    return jsonify({"message": "Profil ignoré", "status": "rejected"}), 201


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

    # --- Créer la conversation (fallback si échec) ---
    conversation_id = None
    try:
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
            db.session.flush()
            conversation_id = conv.id
        else:
            conversation_id = existing_conv.id
    except Exception as e:
        logger.warning(f"Conversation creation skipped (match {matching_id}): {e}")

    # --- Réserver le créneau de l'aidant (fallback si absent) ---
    try:
        demand = db.session.get(Demand, match.demand_id)
        if demand:
            helper_profile = Profile.query.filter_by(user_id=match.user_two_id).first()
            if helper_profile:
                helper_slot = Disponible.query.filter_by(
                    profile_id=helper_profile.id,
                    jour=demand.jour,
                    creneau=demand.creneau,
                    is_reserved=False
                ).first()
                if helper_slot:
                    helper_slot.is_reserved = True
    except Exception as e:
        logger.warning(f"Slot reservation skipped (match {matching_id}): {e}")

    # Notifier le demandeur que sa demande a été acceptée
    accepteur_profile = Profile.query.filter_by(user_id=current_user_id).first()
    notif = Notification(
        user_id=match.user_one_id,
        titre="Demande de mentorat acceptée !",
        contenu=f"{accepteur_profile.prenom} {accepteur_profile.nom} a accepté votre demande de mentorat.",
        type='matching'
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

    msg = "Match accepté ! Vous pouvez maintenant discuter." if conversation_id else "Match accepté !"
    return jsonify({
        "message": msg,
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
        titre="Demande de mentorat refusée",
        contenu=f"{refuseur_profile.prenom} {refuseur_profile.nom} n'est pas disponible pour le moment.",
        type='matching'
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
                "filiere": initiator_profile.filiere if initiator_profile else "",
                "niveau":  initiator_profile.niveau if initiator_profile else "",
                "bio":     initiator_profile.bio if initiator_profile else "",
                "avatar_url": initiator_profile.avatar_url if initiator_profile else "",
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
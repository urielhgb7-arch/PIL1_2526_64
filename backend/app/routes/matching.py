# backend/app/routes/matching.py
# ============================================================
# ROUTES MATCHING — IFRI MENTORLINK
# Endpoints : suggestions, accept, reject
# Conforme à : IFRI_Mentorlink_Vision_du_Système_de_Matching.pdf
# ============================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Profile, Conversation, Notification
from app.models.services import Matching, ProfilCompetence
from app.services.matching import calculate_matches
from app.validators import matiere_exists

matching_bp = Blueprint('matching', __name__)


# ── GET /api/matches/suggestions ────────────────────────────────────────────
# Section 5 & 10 du PDF : déclenchement du matching + affichage des résultats
@matching_bp.route('/matches/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    current_user_id = int(get_jwt_identity())

    # Filtre optionnel sur une matière précise (?matiere_id=1)
    matiere_id = request.args.get('matiere_id', type=int)

    resultats = calculate_matches(current_user_id, matiere_id=matiere_id)

    if not resultats:
        return jsonify({
            "message": "Aucun candidat trouvé. Complétez vos lacunes et disponibilités.",
            "matches": []
        }), 200

    return jsonify({
        "total": len(resultats),
        "matches": resultats
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
    matiere_id = data.get('matiere_id')
    score      = data.get('score', 0.0)

    if not matiere_id:
        return jsonify({"message": "matiere_id requis"}), 400

    # vérifier que la matière existe
    if not matiere_exists(matiere_id):
        return jsonify({"message": "Matière introuvable"}), 404

    # Vérifier que le candidat existe
    candidate = db.session.get(User, student_id)
    if not candidate:
        return jsonify({"message": "Candidat introuvable"}), 404

    # Vérifier qu'un matching n'existe pas déjà entre ces deux sur cette matière
    existing = Matching.query.filter_by(
        user_one_id=current_user_id,
        user_two_id=student_id,
        matiere_id=matiere_id
    ).first()
    if existing:
        return jsonify({
            "message": "Demande déjà envoyée",
            "matching_id": existing.id,
            "status": existing.status
        }), 200

    # Créer le matching en statut 'pending'
    new_match = Matching(
        user_one_id=current_user_id,
        user_two_id=student_id,
        initiator_id=current_user_id,
        matiere_id=matiere_id,
        score=score,
        status='pending'
    )
    db.session.add(new_match)
    db.session.flush()  # obtenir new_match.id avant commit
    # Créer une conversation immédiatement pour permettre au candidat
    # et au mentor d'échanger dès que la demande est envoyée.
    existing_conv = Conversation.query.filter_by(
        user_one_id=current_user_id,
        user_two_id=student_id
    ).first() or Conversation.query.filter_by(
        user_one_id=student_id,
        user_two_id=current_user_id
    ).first()

    if not existing_conv:
        conv = Conversation(user_one_id=current_user_id, user_two_id=student_id)
        db.session.add(conv)
        db.session.flush()
        conversation_id = conv.id
    else:
        conversation_id = existing_conv.id

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

    return jsonify({
        "message": "Demande envoyée avec succès",
        "matching_id": new_match.id,
        "status": "pending",
        "conversation_id": conversation_id
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

    # --- Geler la disponibilité de l'aidant pour cette matière ---
    # On marque la compétence correspondante comme non-disponible
    helper_profile = Profile.query.filter_by(user_id=match.user_two_id).first()
    if helper_profile:
        comp = ProfilCompetence.query.filter_by(profile_id=helper_profile.id, matiere_id=match.matiere_id).first()
        if comp:
            comp.is_available_to_help = False

        # Optionnel : marquer le profil global comme non-disponible
        helper_profile.disponible = False

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
        user_two_id=current_user_id,
        status='pending'
    ).order_by(Matching.created_at.desc()).all()

    result = []
    for m in matches:
        demandeur_profile = Profile.query.filter_by(user_id=m.user_one_id).first()
        result.append({
            "matching_id": m.id,
            "demandeur": {
                "user_id": m.user_one_id,
                "nom":     demandeur_profile.nom if demandeur_profile else "",
                "prenom":  demandeur_profile.prenom if demandeur_profile else "",
            },
            "matiere_id": m.matiere_id,
            "score":      m.score,
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
            "score":      m.score,
            "status":     m.status,
            "created_at": m.created_at.isoformat()
        })

    return jsonify(result), 200
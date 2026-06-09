import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Profile, Feedback, Matching

logger = logging.getLogger(__name__)
feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    current_user_id = int(get_jwt_identity())
    data = request.get_json(force=True, silent=True) or {}

    matching_id = data.get('matching_id')
    note = data.get('note')
    commentaire = data.get('commentaire', '')

    if not matching_id or not note:
        return jsonify({"message": "matching_id et note requis"}), 400

    if not isinstance(note, int) or note < 1 or note > 5:
        return jsonify({"message": "note doit être un entier entre 1 et 5"}), 400

    matching = db.session.get(Matching, matching_id)
    if not matching:
        return jsonify({"message": "Matching introuvable"}), 404

    if matching.status != 'accepted':
        return jsonify({"message": "Seuls les matchs acceptés peuvent être évalués"}), 400

    if matching.user_one_id != current_user_id and matching.user_two_id != current_user_id:
        return jsonify({"message": "Non autorisé"}), 403

    to_user_id = matching.user_two_id if matching.user_one_id == current_user_id else matching.user_one_id

    existing = Feedback.query.filter_by(from_user_id=current_user_id, matching_id=matching_id).first()
    if existing:
        return jsonify({"message": "Vous avez déjà évalué ce match"}), 400

    feedback = Feedback(
        from_user_id=current_user_id,
        to_user_id=to_user_id,
        matching_id=matching_id,
        note=note,
        commentaire=commentaire
    )
    db.session.add(feedback)
    db.session.commit()

    logger.info(f"Feedback créé: matching_id={matching_id}, note={note}")
    return jsonify({"message": "Feedback enregistré", "id": feedback.id}), 201


@feedback_bp.route('/feedback/<int:user_id>', methods=['GET'])
def get_user_feedback(user_id):
    feedbacks = Feedback.query.filter_by(to_user_id=user_id).order_by(Feedback.created_at.desc()).all()
    if not feedbacks:
        return jsonify({"note_moyenne": None, "total": 0, "feedbacks": []}), 200

    from_user_ids = [f.from_user_id for f in feedbacks]
    from_profiles = {p.user_id: p for p in Profile.query.filter(Profile.user_id.in_(from_user_ids)).all()}

    avg = sum(f.note for f in feedbacks) / len(feedbacks)

    return jsonify({
        "note_moyenne": round(avg, 2),
        "total": len(feedbacks),
        "feedbacks": [{
            "id": f.id,
            "from_user": {
                "user_id": f.from_user_id,
                "nom": from_profiles.get(f.from_user_id).nom if from_profiles.get(f.from_user_id) else "",
                "prenom": from_profiles.get(f.from_user_id).prenom if from_profiles.get(f.from_user_id) else ""
            },
            "note": f.note,
            "commentaire": f.commentaire,
            "created_at": f.created_at.isoformat()
        } for f in feedbacks]
    }), 200

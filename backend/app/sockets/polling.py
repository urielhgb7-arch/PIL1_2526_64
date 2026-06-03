from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.messages import Message, Conversation

polling_bp = Blueprint('polling', __name__)

@polling_bp.route('/polling/messages', methods=['GET'])
@jwt_required()
def check_nouveaux_messages():
    current_user_id = int(get_jwt_identity())

    # Trouver toutes les conversations de l'utilisateur
    convs = Conversation.query.filter(
        (Conversation.user_one_id == current_user_id) |
        (Conversation.user_two_id == current_user_id)
    ).all()

    conv_ids = [c.id for c in convs]

    # Compter les messages reçus (pas envoyés par moi)
    nouveaux = Message.query.filter(
        Message.conversation_id.in_(conv_ids),
        Message.sender_id != current_user_id
    ).order_by(Message.date_envoi.desc()).limit(10).all()

    result = [{
        "message_id": m.id,
        "conversation_id": m.conversation_id,
        "sender_id": m.sender_id,
        "contenu": m.contenu,
        "date_envoi": m.date_envoi.isoformat()
    } for m in nouveaux]

    return jsonify({
        "nouveaux_messages": len(result),
        "messages": result
    }), 200
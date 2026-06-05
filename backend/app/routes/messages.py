from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Profile
from app.models.messages import Conversation, Message

messages_bp = Blueprint('messages', __name__)

# --- CONVERSATIONS ---

@messages_bp.route('/conversations', methods=['POST'])
@jwt_required()
def creer_conversation():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    autre_user_id = data.get('user_id')
    if not autre_user_id:
        return jsonify({"message": "user_id requis"}), 400

    # Vérifier si la conversation existe déjà
    conv = Conversation.query.filter_by(
        user_one_id=current_user_id,
        user_two_id=autre_user_id
    ).first() or Conversation.query.filter_by(
        user_one_id=autre_user_id,
        user_two_id=current_user_id
    ).first()

    if conv:
        return jsonify({"conversation_id": conv.id}), 200

    # Créer une nouvelle conversation
    nouvelle_conv = Conversation(
        user_one_id=current_user_id,
        user_two_id=autre_user_id
    )
    db.session.add(nouvelle_conv)
    db.session.commit()

    return jsonify({"conversation_id": nouvelle_conv.id}), 201


@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def mes_conversations():
    current_user_id = int(get_jwt_identity())

    convs = Conversation.query.filter(
        (Conversation.user_one_id == current_user_id) |
        (Conversation.user_two_id == current_user_id)
    ).all()

    result = []
    for conv in convs:
        # L'autre personne dans la conversation
        autre_id = conv.user_two_id if conv.user_one_id == current_user_id else conv.user_one_id
        autre = db.session.get(User, autre_id)
        autre_profile = Profile.query.filter_by(user_id=autre_id).first()
        result.append({
            "conversation_id": conv.id,
            "avec": {
                "user_id": autre_id,
                "nom": autre_profile.nom if autre_profile else "",
                "prenom": autre_profile.prenom if autre_profile else ""
            }
        })

    return jsonify(result), 200


# --- MESSAGES ---

@messages_bp.route('/conversations/<int:conv_id>/messages', methods=['POST'])
@jwt_required()
def envoyer_message(conv_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    contenu = data.get('contenu')
    if not contenu:
        return jsonify({"message": "contenu requis"}), 400

    conv = db.session.get(Conversation, conv_id)
    if not conv:
        return jsonify({"message": "Conversation introuvable"}), 404

    msg = Message(
        conversation_id=conv_id,
        sender_id=current_user_id,
        contenu=contenu
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"message": "Message envoyé", "message_id": msg.id}), 201


@messages_bp.route('/conversations/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def lire_messages(conv_id):
    current_user_id = int(get_jwt_identity())

    conv = db.session.get(Conversation, conv_id)
    if not conv:
        return jsonify({"message": "Conversation introuvable"}), 404

    messages = Message.query.filter_by(
        conversation_id=conv_id
    ).order_by(Message.date_envoi.asc()).all()

    result = [{
        "id": m.id,
        "sender_id": m.sender_id,
        "contenu": m.contenu,
        "date_envoi": m.date_envoi.isoformat()
    } for m in messages]

    return jsonify(result), 200
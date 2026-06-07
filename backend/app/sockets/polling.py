"""
Endpoint de polling pour les nouveaux messages.

Utilisation : GET /api/polling/messages?last_message_id=<int>

Le client envoie le dernier message_id qu'il a déjà reçu.
Le backend ne retourne que les messages postérieurs à cet ID,
ce qui garantit qu'on ne renvoie pas les mêmes messages à chaque appel.
Si last_message_id est absent ou vaut 0, on retourne les 20 derniers messages.
"""
import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.messages import Message, Conversation

logger = logging.getLogger(__name__)
polling_bp = Blueprint('polling', __name__)


@polling_bp.route('/polling/messages', methods=['GET'])
@jwt_required()
def check_nouveaux_messages():
    current_user_id = int(get_jwt_identity())

    # L'identifiant du dernier message déjà connu par le client
    # (0 ou absent = première requête, on retourne les 20 derniers)
    last_message_id = request.args.get('last_message_id', 0, type=int)

    # Toutes les conversations de l'utilisateur
    convs = Conversation.query.filter(
        (Conversation.user_one_id == current_user_id) |
        (Conversation.user_two_id == current_user_id)
    ).all()

    conv_ids = [c.id for c in convs]

    if not conv_ids:
        return jsonify({"nouveaux_messages": 0, "messages": [], "last_message_id": last_message_id}), 200

    # Requête de base : messages reçus (pas envoyés par moi) dans mes conversations
    query = Message.query.filter(
        Message.conversation_id.in_(conv_ids),
        Message.sender_id != current_user_id
    )

    if last_message_id > 0:
        # Mode incrémental : uniquement les messages plus récents que le dernier connu
        query = query.filter(Message.id > last_message_id)
    else:
        # Première requête : les 20 derniers (pour initialiser le client)
        query = query.order_by(Message.date_envoi.desc()).limit(20)

    nouveaux = query.order_by(Message.date_envoi.asc()).all()

    result = [{
        "message_id":      m.id,
        "conversation_id": m.conversation_id,
        "sender_id":       m.sender_id,
        "contenu":         m.contenu,
        "date_envoi":      m.date_envoi.isoformat()
    } for m in nouveaux]

    # Retourne le nouvel ID de curseur pour le prochain appel
    new_last_id = result[-1]["message_id"] if result else last_message_id

    logger.debug(
        f"Polling user={current_user_id} last_id={last_message_id} "
        f"→ {len(result)} nouveau(x) message(s)"
    )

    return jsonify({
        "nouveaux_messages": len(result),
        "messages":          result,
        "last_message_id":   new_last_id   # ← le client doit stocker cette valeur
    }), 200
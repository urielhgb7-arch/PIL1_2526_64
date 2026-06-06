from flask import Blueprint, request, jsonify
import logging
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import User, Profile
from app.models.messages import Conversation, Message

logger = logging.getLogger(__name__)
messages_bp = Blueprint('messages', __name__)

# --- CONVERSATIONS ---

@messages_bp.route('/conversations', methods=['POST'])
@jwt_required()
def creer_conversation():
    """Crée une conversation entre deux utilisateurs"""
    current_user_id = int(get_jwt_identity())
    
    try:
        data = request.get_json(force=True, silent=True) or {}
        autre_user_id = data.get('user_id')
        
        if not autre_user_id:
            logger.warning(f"Création conversation sans user_id par user={current_user_id}")
            return jsonify({"message": "user_id requis"}), 400

        if current_user_id == autre_user_id:
            logger.warning(f"Tentative conversation avec soi-même par user={current_user_id}")
            return jsonify({"message": "Vous ne pouvez pas discuter avec vous-même"}), 400

        # Vérifier que l'autre utilisateur existe
        autre_user = db.session.get(User, autre_user_id)
        if not autre_user:
            logger.warning(f"Conversation avec user inexistant {autre_user_id}")
            return jsonify({"message": "Utilisateur introuvable"}), 404

        # Vérifier si la conversation existe déjà
        conv = Conversation.query.filter_by(
            user_one_id=current_user_id,
            user_two_id=autre_user_id
        ).first() or Conversation.query.filter_by(
            user_one_id=autre_user_id,
            user_two_id=current_user_id
        ).first()

        if conv:
            logger.info(f"✅ Conversation existante trouvée: {conv.id}")
            return jsonify({"conversation_id": conv.id}), 200

        # Créer une nouvelle conversation
        nouvelle_conv = Conversation(
            user_one_id=current_user_id,
            user_two_id=autre_user_id
        )
        db.session.add(nouvelle_conv)
        db.session.commit()
        logger.info(f"✅ Conversation créée: {nouvelle_conv.id} entre {current_user_id} et {autre_user_id}")

        return jsonify({"conversation_id": nouvelle_conv.id}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur création conversation: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def mes_conversations():
    """Liste toutes les conversations de l'utilisateur"""
    current_user_id = int(get_jwt_identity())
    
    try:
        convs = Conversation.query.filter(
            (Conversation.user_one_id == current_user_id) |
            (Conversation.user_two_id == current_user_id)
        ).all()

        result = []
        for conv in convs:
            autre_id = conv.user_two_id if conv.user_one_id == current_user_id else conv.user_one_id
            autre = db.session.get(User, autre_id)
            autre_profile = Profile.query.filter_by(user_id=autre_id).first()
            
            result.append({
                "conversation_id": conv.id,
                "avec": {
                    "user_id": autre_id,
                    "nom": autre_profile.nom if autre_profile else "Inconnu",
                    "prenom": autre_profile.prenom if autre_profile else ""
                }
            })

        logger.info(f"✅ {len(result)} conversations listées pour user={current_user_id}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erreur listing conversations: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


# --- MESSAGES ---

@messages_bp.route('/conversations/<int:conv_id>/messages', methods=['POST'])
@jwt_required()
def envoyer_message(conv_id: int):
    """Envoie un message dans une conversation"""
    current_user_id = int(get_jwt_identity())
    
    try:
        data = request.get_json(force=True, silent=True) or {}
        contenu = data.get('contenu', '').strip()
        
        if not contenu:
            logger.warning(f"Tentative envoi message vide par user={current_user_id}")
            return jsonify({"message": "Contenu du message requis"}), 400

        conv = db.session.get(Conversation, conv_id)
        if not conv:
            logger.warning(f"Message envoyé vers conversation inexistante: {conv_id}")
            return jsonify({"message": "Conversation introuvable"}), 404

        # Vérifier que l'utilisateur fait partie de la conversation
        if conv.user_one_id != current_user_id and conv.user_two_id != current_user_id:
            logger.warning(f"Accès non autorisé à conversation {conv_id} par user={current_user_id}")
            return jsonify({"message": "Accès refusé"}), 403

        msg = Message(
            conversation_id=conv_id,
            sender_id=current_user_id,
            contenu=contenu
        )
        db.session.add(msg)
        db.session.commit()
        logger.info(f"✅ Message envoyé: {msg.id} dans conv={conv_id}")

        return jsonify({"message": "Message envoyé", "message_id": msg.id}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur envoi message: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


@messages_bp.route('/conversations/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def lire_messages(conv_id: int):
    """Récupère tous les messages d'une conversation"""
    current_user_id = int(get_jwt_identity())
    
    try:
        conv = db.session.get(Conversation, conv_id)
        if not conv:
            logger.warning(f"Lecture conversation inexistante: {conv_id}")
            return jsonify({"message": "Conversation introuvable"}), 404

        # Vérifier que l'utilisateur fait partie de la conversation
        if conv.user_one_id != current_user_id and conv.user_two_id != current_user_id:
            logger.warning(f"Accès non autorisé à conversation {conv_id} par user={current_user_id}")
            return jsonify({"message": "Accès refusé"}), 403

        messages = Message.query.filter_by(
            conversation_id=conv_id
        ).order_by(Message.date_envoi.asc()).all()

        result = [{
            "id": m.id,
            "sender_id": m.sender_id,
            "contenu": m.contenu,
            "date_envoi": m.date_envoi.isoformat()
        } for m in messages]

        logger.info(f"✅ {len(result)} messages listés pour conv={conv_id}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erreur lecture messages: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500

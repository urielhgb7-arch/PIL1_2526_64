import logging
from flask_socketio import SocketIO, join_room, leave_room, emit, disconnect
from flask_jwt_extended import decode_token
from jwt.exceptions import InvalidTokenError
from app.models.messages import Message, Conversation, Notification
from app.database import db

logger = logging.getLogger(__name__)

socketio = SocketIO(cors_allowed_origins="*")


def _get_user_id_from_token(token: str) -> int | None:
    """
    Décode le JWT passé dans l'événement socket et retourne l'user_id.
    Retourne None si le token est invalide ou absent.
    """
    try:
        decoded = decode_token(token)
        return int(decoded["sub"])
    except Exception as e:
        logger.warning(f"Token socket invalide : {e}")
        return None


@socketio.on('connect')
def on_connect():
    emit('connected', {'message': 'Connexion établie'})


@socketio.on('register')
def on_register(data):
    """
    L'événement 'register' doit inclure un JWT valide.
    data = { token: str, user_id: int }
    """
    token = data.get('token')
    user_id = _get_user_id_from_token(token)

    if not user_id:
        emit('error', {'message': 'Token invalide. Connexion refusée.'})
        disconnect()
        return

    # Sécurité : on utilise l'ID issu du token, pas celui fourni par le client
    join_room(f"user_{user_id}")
    logger.info(f"Socket : user {user_id} enregistré dans sa room")
    emit('registered', {'user_id': user_id})


@socketio.on('join')
def on_join(data):
    """
    Rejoindre une conversation.
    data = { token: str, conversation_id: int }

    Vérifie que l'utilisateur fait partie de la conversation avant
    de l'ajouter à la room.
    """
    token = data.get('token')
    user_id = _get_user_id_from_token(token)

    if not user_id:
        emit('error', {'message': 'Token invalide.'})
        disconnect()
        return

    conversation_id = data.get('conversation_id')
    conv = db.session.get(Conversation, conversation_id)

    if not conv:
        emit('error', {'message': 'Conversation introuvable.'})
        return

    if conv.user_one_id != user_id and conv.user_two_id != user_id:
        logger.warning(
            f"Socket join refusé : user {user_id} n'appartient pas à conv {conversation_id}"
        )
        emit('error', {'message': 'Accès refusé à cette conversation.'})
        disconnect()
        return

    join_room(f"conv_{conversation_id}")
    logger.info(f"Socket : user {user_id} a rejoint conv_{conversation_id}")
    emit('joined', {'conversation_id': conversation_id})


@socketio.on('send_message')
def on_message(data):
    """
    Envoyer un message dans une conversation.
    data = { token: str, conversation_id: int, contenu: str }

    - Authentifie via le JWT (pas de sender_id côté client)
    - Vérifie que le sender appartient à la conversation
    - Persiste en base puis diffuse dans la room
    """
    token = data.get('token')
    user_id = _get_user_id_from_token(token)

    if not user_id:
        emit('error', {'message': 'Token invalide.'})
        disconnect()
        return

    conversation_id = data.get('conversation_id')
    contenu = (data.get('contenu') or '').strip()

    if not contenu:
        emit('error', {'message': 'Contenu vide.'})
        return

    conv = db.session.get(Conversation, conversation_id)
    if not conv:
        emit('error', {'message': 'Conversation introuvable.'})
        return

    if conv.user_one_id != user_id and conv.user_two_id != user_id:
        logger.warning(
            f"Socket send_message refusé : user {user_id} n'appartient pas à conv {conversation_id}"
        )
        emit('error', {'message': 'Accès refusé.'})
        disconnect()
        return

    # Persistence
    msg = Message(
        conversation_id=conversation_id,
        sender_id=user_id,      # ID issu du token, jamais du payload client
        contenu=contenu
    )
    db.session.add(msg)
    db.session.commit()
    logger.info(f"Socket : message {msg.id} persisté dans conv {conversation_id}")

    # Notification pour le destinataire
    try:
        from app.models.users import User
        sender = db.session.get(User, user_id)
        sender_name = f"{sender.prenom} {sender.nom}" if sender else "Quelqu'un"
        other_user_id = conv.user_one_id if conv.user_two_id == user_id else conv.user_two_id
        notif = Notification(
            user_id=other_user_id,
            titre="Nouveau message",
            contenu=f"{sender_name} vous a envoyé un message",
            type='message'
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        logger.warning(f"Échec création notification message : {e}")

    # Diffusion à tous les membres de la room
    emit('new_message', {
        'message_id':  msg.id,
        'sender_id':   user_id,
        'contenu':     contenu,
        'date_envoi':  msg.date_envoi.isoformat()
    }, room=f"conv_{conversation_id}")


@socketio.on('leave')
def on_leave(data):
    """
    data = { token: str, conversation_id: int }
    Authentifie avant de quitter la room pour éviter les désinscriptions
    arbitraires d'autres utilisateurs.
    """
    token = data.get('token')
    user_id = _get_user_id_from_token(token)

    if not user_id:
        emit('error', {'message': 'Token invalide.'})
        disconnect()
        return

    conversation_id = data.get('conversation_id')
    leave_room(f"conv_{conversation_id}")
    logger.info(f"Socket : user {user_id} a quitté conv_{conversation_id}")


@socketio.on('notify_match')
def on_match_notification(data):
    """
    data = { token: str, recipient_id: int, student_nom: str, matiere: str }
    Notifie un utilisateur qu'il a reçu une demande de matching.
    """
    token = data.get('token')
    user_id = _get_user_id_from_token(token)

    if not user_id:
        emit('error', {'message': 'Token invalide.'})
        disconnect()
        return

    recipient_id = data.get('recipient_id')
    student_nom  = data.get('student_nom')
    matiere      = data.get('matiere')

    emit('match_received', {
        'message':      f"Nouvelle demande d'aide en {matiere} de la part de {student_nom}",
        'recipient_id': recipient_id,
        'matiere':      matiere
    }, room=f"user_{recipient_id}")
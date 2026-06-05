from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_jwt_extended import decode_token
from app.models.messages import Message, Conversation
from app.database import db

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('connect')
def on_connect():
    emit('connected', {'message': 'Connexion établie'})

@socketio.on('join')
def on_join(data):
    conversation_id = data.get('conversation_id')
    join_room(f"conv_{conversation_id}")
    emit('joined', {'conversation_id': conversation_id})

@socketio.on('send_message')
def on_message(data):
    conversation_id = data.get('conversation_id')
    sender_id = data.get('sender_id')
    contenu = data.get('contenu')

    # Sauvegarder en base
    msg = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        contenu=contenu
    )
    db.session.add(msg)
    db.session.commit()

    # Envoyer à tous dans la conversation
    emit('new_message', {
        'sender_id': sender_id,
        'contenu': contenu,
        'date_envoi': msg.date_envoi.isoformat()
    }, room=f"conv_{conversation_id}")

@socketio.on('leave')
def on_leave(data):
    conversation_id = data.get('conversation_id')
    leave_room(f"conv_{conversation_id}")

@socketio.on('notify_match')
def on_match_notification(data):
    recipient_id = data.get('recipient_id')
    student_nom = data.get('student_nom')
    matiere = data.get('matiere')

    # Envoyer la notification à l'étudiant destinataire
    emit('match_received', {
        'message': f"Nouvelle demande d'aide en {matiere} de la part de {student_nom}",
        'recipient_id': recipient_id,
        'matiere': matiere
    }, room=f"user_{recipient_id}")
    
@socketio.on('register')
def on_register(data):
    user_id = data.get('user_id')
    join_room(f"user_{user_id}")
    emit('registered', {'user_id': user_id})
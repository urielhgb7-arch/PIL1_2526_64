"""
Tests Socket.IO — validés contre la version sécurisée de chat.py.

Chaque événement socket exige désormais un champ `token` (JWT valide).
"""
import pytest
from flask_jwt_extended import create_access_token
from app.database import db
from app.models import User, Profile
from app.models.messages import Conversation, Message


# ── helpers ─────────────────────────────────────────────────────────────────

def create_user_direct(email, password, role='student'):
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def create_profile(user, nom='Test', prenom='User', filiere='INFO', niveau='L1'):
    profile = Profile(
        user_id=user.id,
        nom=nom,
        prenom=prenom,
        filiere=filiere,
        niveau=niveau,
        format_preference='hybride',
        bio='',
        telephone=None
    )
    db.session.add(profile)
    db.session.commit()
    return profile


def make_token(app, user_id: int) -> str:
    """Génère un JWT valide pour les tests socket."""
    with app.app_context():
        return create_access_token(identity=str(user_id))


# ── tests ────────────────────────────────────────────────────────────────────

def test_websocket_connect(socketio_client):
    """Le serveur accepte une connexion WebSocket."""
    assert socketio_client.is_connected()


def test_register_with_valid_token(socketio_client, app):
    """L'événement 'register' avec un token valide enregistre l'utilisateur."""
    with app.app_context():
        user = create_user_direct('sock_reg@a.com', 'pass')
        create_profile(user)
        user_id = user.id
        token = create_access_token(identity=str(user_id))

    socketio_client.emit('register', {'token': token})
    received = socketio_client.get_received()

    event_names = [e['name'] for e in received]
    assert 'registered' in event_names


def test_register_with_invalid_token_disconnects(socketio_client, app):
    """L'événement 'register' avec un mauvais token doit renvoyer une erreur."""
    socketio_client.emit('register', {'token': 'bad.token.here'})

    if socketio_client.is_connected():
        received = socketio_client.get_received()
        error_events = [e for e in received if e['name'] == 'error']
        assert len(error_events) > 0
        assert 'Token invalide' in error_events[0]['args'][0]['message']
    else:
        assert socketio_client.is_connected() is False


def test_join_conversation_with_valid_token(socketio_client, app):
    """L'événement 'join' avec token valide et membership correct fonctionne."""
    with app.app_context():
        user_a = create_user_direct('sock_join_a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('sock_join_b@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
        token = create_access_token(identity=str(user_a.id))

    socketio_client.emit('join', {'token': token, 'conversation_id': conv_id})
    received = socketio_client.get_received()

    event_names = [e['name'] for e in received]
    assert 'joined' in event_names


def test_join_conversation_denied_for_outsider(socketio_client, app):
    """Un utilisateur qui n'appartient pas à la conversation reçoit une erreur."""
    with app.app_context():
        user_a = create_user_direct('sock_out_a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('sock_out_b@a.com', 'pass')
        create_profile(user_b)
        outsider = create_user_direct('sock_outsider@a.com', 'pass')
        create_profile(outsider)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
        token = create_access_token(identity=str(outsider.id))

    socketio_client.emit('join', {'token': token, 'conversation_id': conv_id})

    if socketio_client.is_connected():
        received = socketio_client.get_received()
        error_events = [e for e in received if e['name'] == 'error']
        assert len(error_events) > 0
        assert 'Accès refusé' in error_events[0]['args'][0]['message']
    else:
        assert socketio_client.is_connected() is False


def test_send_message_persists_with_token(socketio_client, app):
    """send_message via socket persiste le message avec le vrai sender_id du token."""
    with app.app_context():
        sender = create_user_direct('sock_sender2@a.com', 'pass')
        create_profile(sender)
        receiver = create_user_direct('sock_recv2@a.com', 'pass')
        create_profile(receiver)
        conv = Conversation(user_one_id=sender.id, user_two_id=receiver.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
        sender_id = sender.id
        token = create_access_token(identity=str(sender_id))

    socketio_client.emit('send_message', {
        'token': token,
        'conversation_id': conv_id,
        'contenu': 'Message sécurisé via socket'
    })

    with app.app_context():
        messages = Message.query.filter_by(
            conversation_id=conv_id,
            sender_id=sender_id
        ).all()
        assert len(messages) == 1
        assert messages[0].contenu == 'Message sécurisé via socket'


def test_send_message_rejected_for_outsider(socketio_client, app):
    """Un outsider ne peut pas envoyer de message dans une conversation qui n'est pas la sienne."""
    with app.app_context():
        user_a = create_user_direct('sock_sec_a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('sock_sec_b@a.com', 'pass')
        create_profile(user_b)
        intrus = create_user_direct('sock_intrus@a.com', 'pass')
        create_profile(intrus)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
        token = create_access_token(identity=str(intrus.id))

    socketio_client.emit('send_message', {
        'token': token,
        'conversation_id': conv_id,
        'contenu': 'Intrusion'
    })

    if socketio_client.is_connected():
        received = socketio_client.get_received()
        error_events = [e for e in received if e['name'] == 'error']
        assert len(error_events) > 0
    else:
        assert socketio_client.is_connected() is False

    with app.app_context():
        count = Message.query.filter_by(conversation_id=conv_id).count()
        assert count == 0


def test_leave_conversation(socketio_client, app):
    """L'événement 'leave' avec token valide ne plante pas."""
    with app.app_context():
        user_a = create_user_direct('sock_lv_a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('sock_lv_b@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
        token = create_access_token(identity=str(user_a.id))

    socketio_client.emit('join', {'token': token, 'conversation_id': conv_id})
    socketio_client.get_received()

    socketio_client.emit('leave', {'token': token, 'conversation_id': conv_id})
    assert socketio_client.is_connected()

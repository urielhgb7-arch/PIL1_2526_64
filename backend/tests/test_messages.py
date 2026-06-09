# backend/tests/test_messages.py
"""Tests pour les routes de messages et conversations"""
import json
import pytest
from app.database import db
from app.models import User, Profile
from app.models.messages import Conversation, Message, Notification
from tests.conftest import client, app_context


def test_creer_conversation(client, app_context):
    """Test création conversation"""
    # Setup
    user1 = User(email='user1@test.com', role='student')
    user1.set_password('pass123')
    user2 = User(email='user2@test.com', role='student')
    user2.set_password('pass123')
    
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    
    # Login user1
    resp_login = client.post('/api/auth/login', 
        json={'email': 'user1@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Créer conversation avec user2
    resp = client.post('/api/conversations',
        json={'user_id': user2.id},
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 201
    assert resp.json['conversation_id'] > 0


def test_lister_conversations(client, app_context):
    """Test listing conversations"""
    # Setup
    user1 = User(email='user1@test.com', role='student')
    user1.set_password('pass123')
    user2 = User(email='user2@test.com', role='student')
    user2.set_password('pass123')
    
    db.session.add_all([user1, user2])
    db.session.commit()
    
    # Créer profils
    profile1 = Profile(user_id=user1.id, nom='Test', prenom='User1', 
                      filiere='INFO', niveau='L1')
    profile2 = Profile(user_id=user2.id, nom='Test', prenom='User2',
                      filiere='INFO', niveau='L1')
    db.session.add_all([profile1, profile2])
    db.session.commit()
    
    # Créer conversation
    conv = Conversation(user_one_id=user1.id, user_two_id=user2.id)
    db.session.add(conv)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user1@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Lister
    resp = client.get('/api/conversations',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    assert len(resp.json) > 0


def test_envoyer_message(client, app_context):
    """Test envoi message"""
    # Setup
    user1 = User(email='user1@test.com', role='student')
    user1.set_password('pass123')
    user2 = User(email='user2@test.com', role='student')
    user2.set_password('pass123')
    
    db.session.add_all([user1, user2])
    db.session.commit()
    
    conv = Conversation(user_one_id=user1.id, user_two_id=user2.id)
    db.session.add(conv)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user1@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Envoyer
    resp = client.post(f'/api/conversations/{conv.id}/messages',
        json={'contenu': 'Bonjour!'},
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 201
    assert resp.json['message_id'] > 0


def test_lire_messages(client, app_context):
    """Test lecture messages"""
    # Setup
    user1 = User(email='user1@test.com', role='student')
    user1.set_password('pass123')
    user2 = User(email='user2@test.com', role='student')
    user2.set_password('pass123')
    
    db.session.add_all([user1, user2])
    db.session.commit()
    
    conv = Conversation(user_one_id=user1.id, user_two_id=user2.id)
    db.session.add(conv)
    db.session.commit()
    
    msg = Message(conversation_id=conv.id, sender_id=user1.id, 
                 contenu='Test message')
    db.session.add(msg)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user1@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Lire
    resp = client.get(f'/api/conversations/{conv.id}/messages',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    assert len(resp.json['messages']) == 1
    assert resp.json['messages'][0]['contenu'] == 'Test message'

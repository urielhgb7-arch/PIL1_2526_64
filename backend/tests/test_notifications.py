# backend/tests/test_notifications.py
"""Tests pour les routes de notifications"""
import json
import pytest
from app.database import db
from app.models import User, Profile
from app.models.messages import Notification
from tests.conftest import client, app_context


def test_lister_notifications(client, app_context):
    """Test listing notifications"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    # Créer notifications
    notif1 = Notification(user_id=user.id, titre='Test 1', 
                         contenu='Contenu 1', type='general')
    notif2 = Notification(user_id=user.id, titre='Test 2',
                         contenu='Contenu 2', type='message')
    db.session.add_all([notif1, notif2])
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Lister
    resp = client.get('/api/notifications',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    assert resp.json['total'] == 2
    assert resp.json['unread_count'] == 2


def test_marquer_notification_lue(client, app_context):
    """Test marquage notification comme lue"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    notif = Notification(user_id=user.id, titre='Test',
                        contenu='Contenu', type='general')
    db.session.add(notif)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Marquer lue
    resp = client.put(f'/api/notifications/{notif.id}/read',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    
    # Vérifier
    resp_check = client.get('/api/notifications',
        headers={'Authorization': f'Bearer {token}'})
    assert resp_check.json['unread_count'] == 0


def test_marquer_toutes_lues(client, app_context):
    """Test marquage toutes notifications lues"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    for i in range(3):
        notif = Notification(user_id=user.id, titre=f'Test {i}',
                            contenu=f'Contenu {i}', type='general')
        db.session.add(notif)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Marquer toutes
    resp = client.put('/api/notifications/read-all',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    assert resp.json['count'] == 3
    
    # Vérifier
    resp_check = client.get('/api/notifications',
        headers={'Authorization': f'Bearer {token}'})
    assert resp_check.json['unread_count'] == 0


def test_supprimer_notification(client, app_context):
    """Test suppression notification"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    notif = Notification(user_id=user.id, titre='Test',
                        contenu='Contenu', type='general')
    db.session.add(notif)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Supprimer
    resp = client.delete(f'/api/notifications/{notif.id}',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    
    # Vérifier
    resp_check = client.get('/api/notifications',
        headers={'Authorization': f'Bearer {token}'})
    assert resp_check.json['total'] == 0

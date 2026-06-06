# backend/tests/test_profile.py
"""Tests pour les routes de profil"""
import pytest
from app.database import db
from app.models import User, Profile, Disponible, Matiere
from app.models.services import ProfilCompetence, ProfilLacune
from tests.conftest import client, app_context


def test_get_my_profile(client, app_context):
    """Test récupération profil utilisateur"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    profile = Profile(user_id=user.id, nom='Test', prenom='User',
                     filiere='INFO', niveau='L1')
    db.session.add(profile)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Get profile
    resp = client.get('/api/profile/me',
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    assert resp.json['nom'] == 'Test'
    assert resp.json['prenom'] == 'User'


def test_update_profile(client, app_context):
    """Test mise à jour profil"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    profile = Profile(user_id=user.id, nom='Test', prenom='User',
                     filiere='INFO', niveau='L1')
    db.session.add(profile)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Update
    resp = client.put('/api/profile/me',
        json={'nom': 'NewName', 'bio': 'New bio'},
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 200
    
    # Verify
    resp_check = client.get('/api/profile/me',
        headers={'Authorization': f'Bearer {token}'})
    assert resp_check.json['nom'] == 'NewName'
    assert resp_check.json['bio'] == 'New bio'


def test_add_competence(client, app_context):
    """Test ajout compétence"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    profile = Profile(user_id=user.id, nom='Test', prenom='User',
                     filiere='INFO', niveau='L1')
    db.session.add(profile)
    db.session.commit()
    
    matiere = Matiere(nom='Algorithmique', filiere='INFO', annee='L1')
    db.session.add(matiere)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Add competence
    resp = client.post('/api/profile/competences',
        json={'matiere_id': matiere.id, 'niveau': 'Avancé', 
              'is_available_to_help': True},
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 201


def test_add_lacune(client, app_context):
    """Test ajout lacune (faiblesse)"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    profile = Profile(user_id=user.id, nom='Test', prenom='User',
                     filiere='INFO', niveau='L1')
    db.session.add(profile)
    db.session.commit()
    
    matiere = Matiere(nom='Algorithmique', filiere='INFO', annee='L1')
    db.session.add(matiere)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Add lacune
    resp = client.post('/api/profile/lacunes',
        json={'matiere_id': matiere.id, 'priorite': 'Haute'},
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 201


def test_add_disponibilite(client, app_context):
    """Test ajout disponibilité"""
    # Setup
    user = User(email='user@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    
    profile = Profile(user_id=user.id, nom='Test', prenom='User',
                     filiere='INFO', niveau='L1')
    db.session.add(profile)
    db.session.commit()
    
    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user@test.com', 'password': 'pass123'})
    token = resp_login.json['token']
    
    # Add disponibilité
    resp = client.post('/api/profile/disponibilites',
        json={'jour': 'Lundi', 'creneau': '10:00-12:00'},
        headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 201


def test_delete_lacune(client, app_context):
    """Test suppression d'une lacune"""
    # Setup
    user = User(email='user2@test.com', role='student')
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()

    profile = Profile(user_id=user.id, nom='Test2', prenom='User2',
                     filiere='INFO', niveau='L1')
    db.session.add(profile)
    db.session.commit()

    matiere = Matiere(nom='Algorithmique2', filiere='INFO', annee='L1')
    db.session.add(matiere)
    db.session.commit()

    # Login
    resp_login = client.post('/api/auth/login',
        json={'email': 'user2@test.com', 'password': 'pass123'})
    token = resp_login.json['token']

    # Add lacune
    resp = client.post('/api/profile/lacunes',
        json={'matiere_id': matiere.id, 'priorite': 'Haute'},
        headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201

    # Delete lacune
    resp_del = client.delete('/api/profile/lacunes',
        json={'matiere_id': matiere.id},
        headers={'Authorization': f'Bearer {token}'})
    assert resp_del.status_code == 200

    # Check profile no longer contains lacunes
    resp_check = client.get('/api/profile/me', headers={'Authorization': f'Bearer {token}'})
    assert resp_check.status_code == 200
    assert isinstance(resp_check.json.get('lacunes'), list)
    assert all(l['matiere_id'] != matiere.id for l in resp_check.json.get('lacunes', []))

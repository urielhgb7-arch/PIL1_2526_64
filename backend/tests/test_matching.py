# backend/tests/test_matching.py
"""Tests pour le matching: création de demande crée une conversation."""
from app.database import db
from app.models import User, Profile, Matiere, Conversation
from app.models.services import ProfilCompetence, Matching


def test_request_creates_conversation(client, app_context):
    # Create two users
    seeker = User(email='seeker@test.com', role='student')
    seeker.set_password('pass123')
    helper = User(email='helper@test.com', role='student')
    helper.set_password('pass123')
    db.session.add_all([seeker, helper])
    db.session.commit()

    # Profiles
    seeker_profile = Profile(user_id=seeker.id, nom='Seeker', prenom='One', filiere='INFO', niveau='L1')
    helper_profile = Profile(user_id=helper.id, nom='Helper', prenom='Two', filiere='INFO', niveau='L3')
    db.session.add_all([seeker_profile, helper_profile])
    db.session.commit()

    # Matiere
    matiere = Matiere(nom='TestMat', filiere='INFO', annee='L1')
    db.session.add(matiere)
    db.session.commit()

    # Helper competence (available)
    comp = ProfilCompetence(profile_id=helper_profile.id, matiere_id=matiere.id, niveau='Avancé', is_available_to_help=True)
    db.session.add(comp)
    db.session.commit()

    # Login as seeker
    resp_login = client.post('/api/auth/login', json={'email': 'seeker@test.com', 'password': 'pass123'})
    token = resp_login.json['token']

    # Send request to helper
    resp = client.post(f'/api/matches/{helper.id}/request', json={'matiere_id': matiere.id, 'score': 85}, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    assert 'conversation_id' in resp.json

    conv_id = resp.json['conversation_id']
    # Conversation must exist
    conv = db.session.get(Conversation, conv_id)
    assert conv is not None
    # Matching must exist and be pending
    matching = Matching.query.filter_by(user_one_id=seeker.id, user_two_id=helper.id, matiere_id=matiere.id).first()
    assert matching is not None
    assert matching.status == 'pending'

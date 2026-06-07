# backend/tests/test_matching.py
"""Tests pour le matching: création de demande crée une conversation."""
from app.database import db
from app.models import User, Profile, Matiere, Conversation
from app.models.profile import Disponible
from app.models.services import ProfilCompetence, Matching, Demand


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

    # Create demand with jour/creneau
    demand = Demand(profile_id=seeker_profile.id, matiere_id=matiere.id, jour='Lundi', creneau='14-15', description='Test demand')
    db.session.add(demand)
    db.session.commit()

    # Helper availability on same day/time
    disponible = Disponible(profile_id=helper_profile.id, jour='Lundi', creneau='14-15')
    db.session.add(disponible)
    db.session.commit()

    # Login as seeker
    resp_login = client.post('/api/auth/login', json={'email': 'seeker@test.com', 'password': 'pass123'})
    token = resp_login.json['token']

    # Send request to helper with demand_id
    resp = client.post(f'/api/matches/{helper.id}/request', json={'demand_id': demand.id, 'score': 85}, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    assert 'matching_id' in resp.json

    matching_id = resp.json['matching_id']
    # Matching must exist and be pending
    matching = db.session.get(Matching, matching_id)
    assert matching is not None
    assert matching.status == 'pending'
    assert matching.demand_id == demand.id

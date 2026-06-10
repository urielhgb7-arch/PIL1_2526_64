import pytest
from app.database import db
from app.models.profile import Profile
from app.models.services import Matiere, Offer, ProfilCompetence, ProfilLacune, Matching, Demand
from app.models.user import User

from tests.test_backend import create_user_direct, create_profile, create_matiere, login_user


def test_respond_to_offer_requires_lacune(client, app):
    """Un étudiant sans lacune sur la matière ne peut pas répondre à une offre."""
    with app.app_context():
        matiere = create_matiere('Biologie', annee='L1', filiere='STI2D')
        mentor = create_user_direct('mentor_offer@a.com', 'pass')
        mentor_profile = create_profile(mentor)
        # Mentor a la competence
        comp = ProfilCompetence(profile_id=mentor_profile.id, matiere_id=matiere.id, niveau='Avancé', is_available_to_help=True)
        offer = Offer(profile_id=mentor_profile.id, matiere_id=matiere.id, jour='Lundi', creneau='10-11')
        db.session.add_all([comp, offer])
        db.session.commit()
        offer_id = offer.id

        # Etudiant sans lacune
        student = create_user_direct('student_no_lacune@a.com', 'pass')
        create_profile(student)

    token = login_user(client, 'student_no_lacune@a.com', 'pass').json['token']
    response = client.post(f'/api/offers/{offer_id}/respond', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert 'lacune' in response.json['message']


def test_respond_to_offer_creates_matching_when_lacune_present(client, app):
    """Un étudiant avec une lacune peut répondre et cela crée un matching et une demande."""
    with app.app_context():
        matiere = create_matiere('Informatique', annee='L2', filiere='GL')
        matiere_id = matiere.id
        mentor = create_user_direct('mentor_offer2@a.com', 'pass')
        mentor_profile = create_profile(mentor)
        comp = ProfilCompetence(profile_id=mentor_profile.id, matiere_id=matiere_id, niveau='Expert', is_available_to_help=True)
        offer = Offer(profile_id=mentor_profile.id, matiere_id=matiere_id, jour='Mardi', creneau='14-15')
        db.session.add_all([comp, offer])
        db.session.commit()
        offer_id = offer.id

        # Etudiant avec lacune
        student = create_user_direct('student_with_lacune@a.com', 'pass')
        student_profile = create_profile(student)
        lac = ProfilLacune(profile_id=student_profile.id, matiere_id=matiere_id, priorite='Moyenne')
        db.session.add(lac)
        db.session.commit()

    token = login_user(client, 'student_with_lacune@a.com', 'pass').json['token']
    response = client.post(f'/api/offers/{offer_id}/respond', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert 'matching_id' in response.json

    matching_id = response.json['matching_id']
    with app.app_context():
        matching = db.session.get(Matching, matching_id)
        assert matching is not None
        # verify matching links
        assert matching.matiere_id == matiere_id
        assert matching.demand is not None
        assert matching.demand.matiere_id == matiere_id

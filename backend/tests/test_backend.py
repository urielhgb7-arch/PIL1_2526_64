import json
import pytest
from app.database import db
from app.models.user import User
from app.models.profile import Profile, Disponible
from app.models.services import Matiere, ProfilCompetence, ProfilLacune, Demand
from app.models.messages import Conversation, Message, Notification


def register_user(client, payload):
    return client.post('/api/auth/register', json=payload)


def login_user(client, email, password):
    return client.post('/api/auth/login', json={'email': email, 'password': password})


def create_user_direct(email, password, role='student'):
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def create_profile(user, nom='Test', prenom='User', filiere='STI2D', niveau='L1'):
    profile = Profile(
        user_id=user.id,
        nom=nom,
        prenom=prenom,
        filiere=filiere,
        niveau=niveau,
        bio='Bio',
        telephone='0123456789'
    )
    db.session.add(profile)
    db.session.commit()
    return profile


def create_matiere(nom, annee=None, filiere=None):
    matiere = Matiere(nom=nom, annee=annee, filiere=filiere)
    db.session.add(matiere)
    db.session.commit()
    return matiere


def add_disponibilite(profile, jour, creneau):
    dispo = Disponible(profile_id=profile.id, jour=jour, creneau=creneau)
    db.session.add(dispo)
    db.session.commit()
    return dispo


def add_lacune(profile, matiere, priorite='Moyenne'):
    lacune = ProfilLacune(profile_id=profile.id, matiere_id=matiere.id, priorite=priorite)
    db.session.add(lacune)
    db.session.commit()
    return lacune


def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy', 'database': 'connected'}


def test_register_requires_all_fields(client):
    response = register_user(client, {'email': 'a@a.com', 'password': 'pass'})
    assert response.status_code == 400
    assert 'Champs obligatoires manquants' in response.json['message']
    assert 'nom' in response.json['required']


def test_register_duplicate_email(client):
    payload = {
        'email': 'duplicate@a.com',
        'password': 'pass',
        'nom': 'Dup',
        'prenom': 'User',
        'filiere': 'STI2D',
        'niveau': 'L1'
    }
    response1 = register_user(client, payload)
    assert response1.status_code == 201

    response2 = register_user(client, payload)
    assert response2.status_code == 400
    assert response2.json['message'] == 'Cet email existe déjà'


def test_register_and_login_success(client):
    payload = {
        'email': 'login@a.com',
        'password': 'password123',
        'nom': 'Jean',
        'prenom': 'Dupont',
        'filiere': 'Math',
        'niveau': 'L2'
    }
    response = register_user(client, payload)
    assert response.status_code == 201
    assert 'Compte créé avec succès' in response.json['message']

    login = login_user(client, payload['email'], payload['password'])
    assert login.status_code == 200
    assert 'token' in login.json
    assert login.json['user']['email'] == payload['email']
    assert login.json['user']['role'] == 'student'


def test_user_role_forced_to_student(client):
    payload = {
        'email': 'student@a.com',
        'password': 'pass123',
        'nom': 'Student',
        'prenom': 'Force',
        'filiere': 'Info',
        'niveau': 'L3'
    }
    register_user(client, payload)
    user = User.query.filter_by(email=payload['email']).first()
    assert user is not None
    assert user.role == 'student'


def test_login_invalid_credentials(client):
    response = login_user(client, 'nope@a.com', 'badpass')
    assert response.status_code == 401
    assert response.json['message'] == 'Identifiants invalides'


def test_matching_requires_auth(client):
    response = client.get('/api/matches/suggestions')
    assert response.status_code == 401


def test_matching_returns_no_matches_without_lacunes(client, app):
    with app.app_context():
        user = create_user_direct('student1@a.com', 'password')
        create_profile(user)
    login = login_user(client, 'student1@a.com', 'password')
    token = login.json['token']
    response = client.get('/api/matches/suggestions', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['matches'] == []
    assert 'Aucun candidat trouvé' in response.json['message']


def test_matching_finds_compatible_students(client, app):
    with app.app_context():
        matiere = create_matiere('Maths', annee='L2', filiere='GL')

        seeker = create_user_direct('matching-seeker@a.com', 'password')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='One', filiere='GL', niveau='L2')
        add_lacune(seeker_profile, matiere, priorite='Haute')
        add_disponibilite(seeker_profile, 'Lundi', '10-11')

        helper = create_user_direct('matching-helper@a.com', 'password')
        helper_profile = create_profile(helper, nom='Helper', prenom='Two', filiere='GL', niveau='L2')
        helper_id = helper.id
        competence = ProfilCompetence(profile_id=helper_profile.id, matiere_id=matiere.id, niveau='Avancé')
        add_disponibilite(helper_profile, 'Lundi', '10-11')
        db.session.add(competence)
        db.session.commit()

    login = login_user(client, 'matching-seeker@a.com', 'password')
    token = login.json['token']
    response = client.get('/api/matches/suggestions', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json['total'] == 1
    assert response.json['matches'][0]['student_id'] == helper_id
    assert response.json['matches'][0]['score'] == 100
    assert response.json['matches'][0]['matched_subjects'][0]['nom'] == 'Maths'


def test_get_matieres_returns_list(client, app):
    with app.app_context():
        create_matiere('Physique-Test-API', annee='L1', filiere='STI2D')
        create_matiere('Maths-Test-API', annee='L2', filiere='GL')

    response = client.get('/api/matieres')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    noms = [item['nom'] for item in response.json]
    assert 'Maths-Test-API' in noms
    assert 'Physique-Test-API' in noms


def test_conversation_creation_and_duplicate(client, app):
    with app.app_context():
        user_a = create_user_direct('a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('b@a.com', 'pass')
        create_profile(user_b)
        user_b_id = user_b.id

    token = login_user(client, 'a@a.com', 'pass').json['token']
    response1 = client.post('/api/conversations', json={'user_id': user_b_id}, headers={'Authorization': f'Bearer {token}'})
    assert response1.status_code == 201
    conversation_id = response1.json['conversation_id']

    response2 = client.post('/api/conversations', json={'user_id': user_b.id}, headers={'Authorization': f'Bearer {token}'})
    assert response2.status_code == 200
    assert response2.json['conversation_id'] == conversation_id


def test_send_message_requires_content(client, app):
    with app.app_context():
        user_a = create_user_direct('messa@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('messb@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id

    token = login_user(client, 'messa@a.com', 'pass').json['token']
    response = client.post(f'/api/conversations/{conv_id}/messages', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400
    assert response.json['message'] == 'contenu requis'


def test_send_and_read_message(client, app):
    with app.app_context():
        user_a = create_user_direct('msg1@a.com', 'pass')
        create_profile(user_a)
        user_a_id = user_a.id
        user_b = create_user_direct('msg2@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id

    token = login_user(client, 'msg1@a.com', 'pass').json['token']
    response = client.post(
        f'/api/conversations/{conv_id}/messages',
        json={'contenu': 'Bonjour'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Message envoyé'

    read = client.get(f'/api/conversations/{conv_id}/messages', headers={'Authorization': f'Bearer {token}'})
    assert read.status_code == 200
    assert read.json[0]['contenu'] == 'Bonjour'
    assert read.json[0]['sender_id'] == user_a_id


def test_polling_returns_messages(client, app):
    with app.app_context():
        user_a = create_user_direct('poll1@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('poll2@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        msg = Message(conversation_id=conv.id, sender_id=user_b.id, contenu='Salut')
        db.session.add(msg)
        db.session.commit()

    token = login_user(client, 'poll1@a.com', 'pass').json['token']
    response = client.get('/api/polling/messages', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['nouveaux_messages'] == 1
    assert response.json['messages'][0]['contenu'] == 'Salut'


def test_notifications_can_be_listed_and_marked_read(client, app):
    with app.app_context():
        user = create_user_direct('notify@a.com', 'pass')
        create_profile(user)
        notification = Notification(
            user_id=user.id,
            titre='Match disponible',
            contenu='Un nouveau match a été trouvé pour votre lacune.',
            type='info'
        )
        db.session.add(notification)
        db.session.commit()
        notification_id = notification.id

    token = login_user(client, 'notify@a.com', 'pass').json['token']
    list_response = client.get('/api/notifications', headers={'Authorization': f'Bearer {token}'})
    assert list_response.status_code == 200
    assert isinstance(list_response.json, list)
    assert list_response.json[0]['id'] == notification_id
    assert list_response.json[0]['is_read'] is False

    mark_response = client.put(f'/api/notifications/{notification_id}/read', headers={'Authorization': f'Bearer {token}'})
    assert mark_response.status_code == 200
    assert mark_response.json['message'] == 'Notification marquée comme lue'

    list_after_response = client.get('/api/notifications?unread_only=true', headers={'Authorization': f'Bearer {token}'})
    assert list_after_response.status_code == 200
    assert list_after_response.json == []


def test_send_message_outside_conversation_is_allowed_but_insecure(client, app):
    with app.app_context():
        user_a = create_user_direct('insec1@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('insec2@a.com', 'pass')
        create_profile(user_b)
        third = create_user_direct('insec3@a.com', 'pass')
        create_profile(third)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id

    token = login_user(client, 'insec3@a.com', 'pass').json['token']
    response = client.post(
        f'/api/conversations/{conv_id}/messages',
        json={'contenu': 'Intrus'},
        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert response.json['message'] == 'Message envoyé'

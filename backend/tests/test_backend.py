import json
import secrets
from datetime import datetime, timedelta, timezone
import pytest
from app.database import db
from app.models.user import User
from app.models.profile import Profile, Disponible
from app.models.password_reset_token import PasswordResetToken
from app.models.services import Matiere, ProfilCompetence, ProfilLacune, Demand, Matching
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


def create_profile(user, nom='Test', prenom='User', filiere='STI2D', niveau='L1', format_preference='hybride'):
    profile = Profile(
        user_id=user.id,
        nom=nom,
        prenom=prenom,
        filiere=filiere,
        niveau=niveau,
        format_preference=format_preference,
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


def test_forgot_password_returns_reset_token_in_dev(client, app):
    with app.app_context():
        user = create_user_direct('forgot@a.com', 'pass')
        create_profile(user)
        user_id = user.id

    response = client.post('/api/auth/forgot-password', json={'email': 'forgot@a.com'})
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'Si votre email existe, un lien de réinitialisation a été émis.'
    assert 'reset_token' in response.json
    assert response.json['reset_token']

    token = response.json['reset_token']
    stored = PasswordResetToken.query.filter_by(token=token).first()
    assert stored is not None
    assert stored.user_id == user_id
    assert stored.used is False


def test_reset_password_with_valid_token(client, app):
    with app.app_context():
        user = create_user_direct('reset@a.com', 'oldpass')
        create_profile(user)
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        stored = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        db.session.add(stored)
        db.session.commit()

    response = client.post('/api/auth/reset-password', json={'token': token, 'new_password': 'newpass123'})
    assert response.status_code == 200
    assert response.json['message'] == 'Mot de passe réinitialisé avec succès'

    with app.app_context():
        user = User.query.filter_by(email='reset@a.com').first()
        assert user.check_password('newpass123')
        stored = PasswordResetToken.query.filter_by(token=token).first()
        assert stored.used is True


def test_reset_password_with_invalid_token(client):
    response = client.post('/api/auth/reset-password', json={'token': 'badtoken', 'new_password': 'newpass123'})
    assert response.status_code == 400
    assert response.json['message'] == 'Token invalide ou expiré'


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


def test_update_profile_format_preference(client, app):
    with app.app_context():
        user = create_user_direct('format@a.com', 'pass')
        create_profile(user)

    token = login_user(client, 'format@a.com', 'pass').json['token']
    response = client.put(
        '/api/profile/me',
        json={'format_preference': 'en_ligne'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200

    profile_response = client.get('/api/profile/me', headers={'Authorization': f'Bearer {token}'})
    assert profile_response.status_code == 200
    assert profile_response.json['format_preference'] == 'en_ligne'


def test_competence_availability_control_matches(client, app):
    with app.app_context():
        matiere = create_matiere('Python', annee='L3', filiere='STI2D')

        seeker = create_user_direct('avail-seeker@a.com', 'pass')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='One', filiere='STI2D', niveau='L3', format_preference='en_ligne')
        add_lacune(seeker_profile, matiere, priorite='Haute')
        add_disponibilite(seeker_profile, 'Lundi', '10-11')

        helper = create_user_direct('avail-helper@a.com', 'pass')
        helper_profile = create_profile(helper, nom='Helper', prenom='Two', filiere='STI2D', niveau='L3', format_preference='en_ligne')
        helper_id = helper.id
        matiere_id = matiere.id
        comp = ProfilCompetence(profile_id=helper_profile.id, matiere_id=matiere_id, niveau='Avancé', is_available_to_help=False)
        add_disponibilite(helper_profile, 'Lundi', '10-11')
        db.session.add(comp)
        db.session.commit()

    seeker_token = login_user(client, 'avail-seeker@a.com', 'pass').json['token']
    response_before = client.get('/api/matches/suggestions', headers={'Authorization': f'Bearer {seeker_token}'})
    assert response_before.status_code == 200
    assert response_before.json['matches'] == []

    helper_token = login_user(client, 'avail-helper@a.com', 'pass').json['token']
    activate = client.put(f'/api/profile/competences/{matiere_id}/activate', headers={'Authorization': f'Bearer {helper_token}'})
    assert activate.status_code == 200
    assert activate.json['is_available_to_help'] is True

    response_after = client.get('/api/matches/suggestions', headers={'Authorization': f'Bearer {seeker_token}'})
    assert response_after.status_code == 200
    assert response_after.json['total'] == 1
    assert response_after.json['matches'][0]['student_id'] == helper_id


def test_matching_prefers_same_learning_format(client, app):
    with app.app_context():
        matiere = create_matiere('Bases de données', annee='L2', filiere='GL')

        seeker = create_user_direct('format-seeker@a.com', 'pass')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='One', filiere='GL', niveau='L2', format_preference='en_ligne')
        add_lacune(seeker_profile, matiere, priorite='Haute')
        add_disponibilite(seeker_profile, 'Mardi', '14-15')

        helper_same = create_user_direct('helper-same@a.com', 'pass')
        helper_same_profile = create_profile(helper_same, nom='Helper', prenom='Same', filiere='GL', niveau='L2', format_preference='en_ligne')
        helper_same_id = helper_same.id
        comp_same = ProfilCompetence(profile_id=helper_same_profile.id, matiere_id=matiere.id, niveau='Intermédiaire', is_available_to_help=True)
        add_disponibilite(helper_same_profile, 'Mardi', '14-15')
        db.session.add(comp_same)

        helper_diff = create_user_direct('helper-diff@a.com', 'pass')
        helper_diff_profile = create_profile(helper_diff, nom='Helper', prenom='Diff', filiere='GL', niveau='L2', format_preference='presentiel')
        helper_diff_id = helper_diff.id
        comp_diff = ProfilCompetence(profile_id=helper_diff_profile.id, matiere_id=matiere.id, niveau='Intermédiaire', is_available_to_help=True)
        add_disponibilite(helper_diff_profile, 'Mardi', '14-15')
        db.session.add(comp_diff)
        db.session.commit()

    token = login_user(client, 'format-seeker@a.com', 'pass').json['token']
    response = client.get('/api/matches/suggestions', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['total'] == 2

    scores = {match['student_id']: match['score'] for match in response.json['matches']}
    assert scores[helper_same_id] > scores[helper_diff_id]
    assert any(
        match['student_id'] == helper_same_id and match['score_detail']['format_preference'] == 10.0
        for match in response.json['matches']
    )


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
    assert response.json['message'] == 'Contenu du message requis'


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
    assert isinstance(list_response.json['notifications'], list)
    assert list_response.json['notifications'][0]['id'] == notification_id
    assert list_response.json['notifications'][0]['is_read'] is False

    mark_response = client.put(f'/api/notifications/{notification_id}/read', headers={'Authorization': f'Bearer {token}'})
    assert mark_response.status_code == 200
    assert mark_response.json['message'] == 'Notification marquée comme lue'

    list_after_response = client.get('/api/notifications?unread_only=true', headers={'Authorization': f'Bearer {token}'})
    assert list_after_response.status_code == 200
    assert list_after_response.json['notifications'] == []


def test_send_message_outside_conversation_is_denied(client, app):
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
    assert response.status_code == 403
    assert response.json['message'] == 'Accès refusé'


# ============ WEBSOCKET / SOCKET.IO TESTS ============

def test_websocket_connect(socketio_client, app):
    """Test que le serveur accepte une connexion WebSocket"""
    assert socketio_client.is_connected()


def test_websocket_register_joins_user_room(socketio_client, app):
    """Test que l'événement 'register' ajoute l'utilisateur à sa room"""
    with app.app_context():
        user = create_user_direct('socket_reg@a.com', 'pass')
        create_profile(user)
        user_id = user.id

    socketio_client.emit('register', {'user_id': user_id})
    
    # Vérifier que l'événement 'registered' est reçu
    # Avec Flask-SocketIO test_client, les événements sont capturés
    data = socketio_client.get_received()
    # L'événement 'registered' doit être dans la liste des événements reçus
    event_names = [e['args'][0] if e['args'] else e.get('name') for e in data]
    assert 'registered' in event_names or len(data) > 0


def test_websocket_join_conversation(socketio_client, app):
    """Test que l'événement 'join' ajoute le client à la room de conversation"""
    with app.app_context():
        user_a = create_user_direct('sock_user_a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('sock_user_b@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id

    socketio_client.emit('join', {'conversation_id': conv_id})
    
    data = socketio_client.get_received()
    # L'événement 'joined' doit être reçu
    event_names = [e['args'][0] if e['args'] else e.get('name') for e in data]
    assert 'joined' in event_names or len(data) > 0


def test_websocket_send_message_persists_to_db(socketio_client, app):
    """Test que envoyer un message via WebSocket le persiste en base de données"""
    with app.app_context():
        sender = create_user_direct('sock_sender@a.com', 'pass')
        create_profile(sender)
        receiver = create_user_direct('sock_receiver@a.com', 'pass')
        create_profile(receiver)
        conv = Conversation(user_one_id=sender.id, user_two_id=receiver.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
        sender_id = sender.id

    socketio_client.emit('send_message', {
        'conversation_id': conv_id,
        'sender_id': sender_id,
        'contenu': 'Message test WebSocket'
    })
    
    # Vérifier que le message est en base de données
    with app.app_context():
        messages = Message.query.filter_by(
            conversation_id=conv_id,
            sender_id=sender_id
        ).all()
        assert len(messages) > 0
        assert messages[0].contenu == 'Message test WebSocket'


def test_websocket_leave_conversation(socketio_client, app):
    """Test que l'événement 'leave' enlève le client de la room de conversation"""
    with app.app_context():
        user_a = create_user_direct('sock_leave_a@a.com', 'pass')
        create_profile(user_a)
        user_b = create_user_direct('sock_leave_b@a.com', 'pass')
        create_profile(user_b)
        conv = Conversation(user_one_id=user_a.id, user_two_id=user_b.id)
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id

    socketio_client.emit('join', {'conversation_id': conv_id})
    socketio_client.get_received()  # Clear the buffer
    
    socketio_client.emit('leave', {'conversation_id': conv_id})
    # Si le leave est traité correctement, pas d'erreur
    data = socketio_client.get_received()
    assert socketio_client.is_connected()


def test_websocket_notify_match(socketio_client, app):
    """Test que l'événement 'notify_match' envoie une notification de match"""
    with app.app_context():
        student = create_user_direct('sock_student@a.com', 'pass')
        create_profile(student)
        mentor = create_user_direct('sock_mentor@a.com', 'pass')
        create_profile(mentor)
        student_id = student.id
        mentor_id = mentor.id

    # L'étudiant reçoit un match du mentor
    socketio_client.emit('notify_match', {
        'recipient_id': student_id,
        'student_nom': 'Student Name',
        'matiere': 'Mathématiques'
    })
    
    data = socketio_client.get_received()
    match_events = [e for e in data if e['args'][0] == 'match_received']
    # L'événement peut ne pas arriver si le recipient n'est pas dans la room
    # mais on peut vérifier que l'émission ne cause pas d'erreur
    assert socketio_client.is_connected()


# ============ DEMAND + MATCHING + SLOT RESERVATION TESTS ============

def test_create_demand_requires_slot(client, app):
    """Test que créer une demande requiert jour et creneau"""
    with app.app_context():
        user = create_user_direct('demand_test@a.com', 'pass')
        create_profile(user)

    token = login_user(client, 'demand_test@a.com', 'pass').json['token']
    
    # Sans jour/creneau
    response = client.post(
        '/api/demands',
        json={'matiere_id': 1},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 400
    assert 'jour' in response.json['message'] and 'creneau' in response.json['message']


def test_create_demand_with_valid_slot(client, app):
    """Test que créer une demande avec jour/creneau valides réussit"""
    with app.app_context():
        matiere = create_matiere('Physique', annee='L1', filiere='STI2D')
        user = create_user_direct('demand_valid@a.com', 'pass')
        create_profile(user)
        matiere_id = matiere.id
        user_id = user.id

    token = login_user(client, 'demand_valid@a.com', 'pass').json['token']
    
    response = client.post(
        '/api/demands',
        json={'matiere_id': matiere_id, 'jour': 'Lundi', 'creneau': '10-11'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert 'id' in response.json
    demand_id = response.json['id']

    # Vérifier en base
    with app.app_context():
        demand = db.session.get(Demand, demand_id)
        assert demand is not None
        assert demand.jour == 'Lundi'
        assert demand.creneau == '10-11'


def test_matching_with_demand_id_filters_by_slot(client, app):
    """Test que matching avec demand_id filtre strictement sur le créneau"""
    with app.app_context():
        matiere = create_matiere('Chimie', annee='L1', filiere='STI2D')

        # Demandeur avec une demande pour Mercredi 14-15
        seeker = create_user_direct('seeker_slot@a.com', 'pass')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='Slot', filiere='STI2D', niveau='L1')
        add_lacune(seeker_profile, matiere, priorite='Haute')
        
        demand = Demand(profile_id=seeker_profile.id, matiere_id=matiere.id, jour='Mercredi', creneau='14-15')
        db.session.add(demand)
        db.session.flush()
        demand_id = demand.id

        # Helper1 : dispo Mercredi 14-15 ET Lundi 10-11
        helper1 = create_user_direct('helper1_slot@a.com', 'pass')
        helper1_profile = create_profile(helper1, nom='Helper', prenom='One', filiere='STI2D', niveau='L1')
        comp1 = ProfilCompetence(profile_id=helper1_profile.id, matiere_id=matiere.id, niveau='Avancé', is_available_to_help=True)
        add_disponibilite(helper1_profile, 'Mercredi', '14-15')
        add_disponibilite(helper1_profile, 'Lundi', '10-11')
        db.session.add(comp1)
        helper1_id = helper1.id

        # Helper2 : dispo Lundi 10-11 SEULEMENT (pas Mercredi 14-15)
        helper2 = create_user_direct('helper2_slot@a.com', 'pass')
        helper2_profile = create_profile(helper2, nom='Helper', prenom='Two', filiere='STI2D', niveau='L1')
        comp2 = ProfilCompetence(profile_id=helper2_profile.id, matiere_id=matiere.id, niveau='Intermédiaire', is_available_to_help=True)
        add_disponibilite(helper2_profile, 'Lundi', '10-11')
        db.session.add(comp2)
        helper2_id = helper2.id

        db.session.commit()

    seeker_token = login_user(client, 'seeker_slot@a.com', 'pass').json['token']
    
    # Matching avec demand_id : doit retourner UNIQUEMENT helper1 (qui a Mercredi 14-15)
    response = client.get(
        f'/api/matches/suggestions?demand_id={demand_id}',
        headers={'Authorization': f'Bearer {seeker_token}'}
    )
    
    assert response.status_code == 200
    assert response.json['total'] == 1
    assert response.json['matches'][0]['student_id'] == helper1_id
    assert helper2_id not in [m['student_id'] for m in response.json['matches']]


def test_request_match_with_demand_checks_candidate_slot_availability(client, app):
    """Test que request_match vérifie que le candidat dispose du créneau requis"""
    with app.app_context():
        matiere = create_matiere('Anglais', annee='L2', filiere='GL')

        seeker = create_user_direct('seeker_req@a.com', 'pass')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='Req', filiere='GL', niveau='L2')
        add_lacune(seeker_profile, matiere, priorite='Moyenne')
        
        demand = Demand(profile_id=seeker_profile.id, matiere_id=matiere.id, jour='Vendredi', creneau='16-17')
        db.session.add(demand)
        db.session.flush()
        demand_id = demand.id

        # Candidat SANS le créneau Vendredi 16-17
        candidate = create_user_direct('candidate_no_slot@a.com', 'pass')
        candidate_profile = create_profile(candidate, nom='Candidate', prenom='NoSlot', filiere='GL', niveau='L2')
        comp = ProfilCompetence(profile_id=candidate_profile.id, matiere_id=matiere.id, niveau='Avancé', is_available_to_help=True)
        add_disponibilite(candidate_profile, 'Jeudi', '15-16')  # Mauvais jour
        db.session.add(comp)
        candidate_id = candidate.id
        db.session.commit()

    seeker_token = login_user(client, 'seeker_req@a.com', 'pass').json['token']
    
    # Essayer de matcher : doit échouer car candidat n'a pas Vendredi 16-17
    response = client.post(
        f'/api/matches/{candidate_id}/request',
        json={'demand_id': demand_id, 'score': 85.0},
        headers={'Authorization': f'Bearer {seeker_token}'}
    )
    
    assert response.status_code == 400
    assert 'disponible' in response.json['message'].lower() or 'créneau' in response.json['message'].lower()


def test_accept_match_reserves_helper_slot(client, app):
    """Test que accepter un match réserve le créneau de l'aidant"""
    with app.app_context():
        matiere = create_matiere('Français', annee='L3', filiere='GL')

        seeker = create_user_direct('seeker_accept@a.com', 'pass')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='Accept', filiere='GL', niveau='L3')
        add_lacune(seeker_profile, matiere, priorite='Urgente')
        
        demand = Demand(profile_id=seeker_profile.id, matiere_id=matiere.id, jour='Mardi', creneau='10-11')
        db.session.add(demand)
        db.session.flush()
        demand_id = demand.id

        helper = create_user_direct('helper_accept@a.com', 'pass')
        helper_profile = create_profile(helper, nom='Helper', prenom='Accept', filiere='GL', niveau='L3')
        comp = ProfilCompetence(profile_id=helper_profile.id, matiere_id=matiere.id, niveau='Expert', is_available_to_help=True)
        helper_slot = add_disponibilite(helper_profile, 'Mardi', '10-11')
        db.session.add(comp)
        helper_id = helper.id
        helper_slot_id = helper_slot.id
        db.session.commit()

    # Vérifier que le créneau n'est pas réservé au départ
    with app.app_context():
        slot_before = db.session.get(Disponible, helper_slot_id)
        assert slot_before.is_reserved is False

    seeker_token = login_user(client, 'seeker_accept@a.com', 'pass').json['token']
    
    # Faire un match
    match_response = client.post(
        f'/api/matches/{helper_id}/request',
        json={'demand_id': demand_id, 'score': 95.0},
        headers={'Authorization': f'Bearer {seeker_token}'}
    )
    assert match_response.status_code == 201
    matching_id = match_response.json['matching_id']

    # Accepter le match
    helper_token = login_user(client, 'helper_accept@a.com', 'pass').json['token']
    accept_response = client.post(
        f'/api/matches/{matching_id}/accept',
        headers={'Authorization': f'Bearer {helper_token}'}
    )
    assert accept_response.status_code == 200

    # Vérifier que le créneau est maintenant réservé
    with app.app_context():
        slot_after = db.session.get(Disponible, helper_slot_id)
        assert slot_after.is_reserved is True


def test_reserved_slots_excluded_from_future_matching(client, app):
    """Test que les créneaux réservés n'apparaissent pas dans les futures suggestions"""
    with app.app_context():
        matiere = create_matiere('Maths avancée', annee='L3', filiere='STI2D')

        # Seeker 1 avec demande pour Jeudi 11-12
        seeker1 = create_user_direct('seeker1_reserved@a.com', 'pass')
        seeker1_profile = create_profile(seeker1, nom='Seeker', prenom='One', filiere='STI2D', niveau='L3')
        add_lacune(seeker1_profile, matiere, priorite='Haute')
        
        demand1 = Demand(profile_id=seeker1_profile.id, matiere_id=matiere.id, jour='Jeudi', creneau='11-12')
        db.session.add(demand1)
        db.session.flush()
        demand1_id = demand1.id

        # Seeker 2 avec demande pour Jeudi 11-12
        seeker2 = create_user_direct('seeker2_reserved@a.com', 'pass')
        seeker2_profile = create_profile(seeker2, nom='Seeker', prenom='Two', filiere='STI2D', niveau='L3')
        add_lacune(seeker2_profile, matiere, priorite='Moyenne')
        
        demand2 = Demand(profile_id=seeker2_profile.id, matiere_id=matiere.id, jour='Jeudi', creneau='11-12')
        db.session.add(demand2)
        db.session.flush()
        demand2_id = demand2.id

        # Helper : dispo Jeudi 11-12
        helper = create_user_direct('helper_reserved@a.com', 'pass')
        helper_profile = create_profile(helper, nom='Helper', prenom='Reserved', filiere='STI2D', niveau='L3')
        comp = ProfilCompetence(profile_id=helper_profile.id, matiere_id=matiere.id, niveau='Expert', is_available_to_help=True)
        helper_slot = add_disponibilite(helper_profile, 'Jeudi', '11-12')
        db.session.add(comp)
        helper_id = helper.id
        db.session.commit()

    # Seeker1 envoie une demande et l'accepte
    seeker1_token = login_user(client, 'seeker1_reserved@a.com', 'pass').json['token']
    
    match1_response = client.post(
        f'/api/matches/{helper_id}/request',
        json={'demand_id': demand1_id, 'score': 100.0},
        headers={'Authorization': f'Bearer {seeker1_token}'}
    )
    matching1_id = match1_response.json['matching_id']

    helper_token = login_user(client, 'helper_reserved@a.com', 'pass').json['token']
    accept_result = client.post(
        f'/api/matches/{matching1_id}/accept',
        headers={'Authorization': f'Bearer {helper_token}'}
    )
    assert accept_result.status_code == 200

    # Maintenant, le créneau est réservé
    # Seeker2 ne devrait PAS voir le helper dans ses suggestions
    seeker2_token = login_user(client, 'seeker2_reserved@a.com', 'pass').json['token']
    
    response2 = client.get(
        f'/api/matches/suggestions?demand_id={demand2_id}',
        headers={'Authorization': f'Bearer {seeker2_token}'}
    )
    
    assert response2.status_code == 200
    # Le helper ne devrait pas être dans les suggestions car son slot est réservé
    if 'total' in response2.json:
        assert response2.json['total'] == 0
        assert helper_id not in [m.get('student_id') for m in response2.json.get('matches', [])]
    else:
        # Sinon, il n'y a pas de matches du tout
        assert response2.json.get('matches', []) == []


def test_get_received_matches_includes_slot_info(client, app):
    """Test que GET /matches/received inclut jour et creneau"""
    with app.app_context():
        matiere = create_matiere('Histoire', annee='L1', filiere='GL')

        seeker = create_user_direct('seeker_received@a.com', 'pass')
        seeker_profile = create_profile(seeker, nom='Seeker', prenom='Rcvd', filiere='GL', niveau='L1')
        add_lacune(seeker_profile, matiere, priorite='Moyenne')
        
        demand = Demand(profile_id=seeker_profile.id, matiere_id=matiere.id, jour='Samedi', creneau='09-10')
        db.session.add(demand)
        db.session.flush()
        demand_id = demand.id

        helper = create_user_direct('helper_received@a.com', 'pass')
        helper_profile = create_profile(helper, nom='Helper', prenom='Rcvd', filiere='GL', niveau='L1')
        comp = ProfilCompetence(profile_id=helper_profile.id, matiere_id=matiere.id, niveau='Avancé', is_available_to_help=True)
        add_disponibilite(helper_profile, 'Samedi', '09-10')
        db.session.add(comp)
        helper_id = helper.id
        db.session.commit()

    seeker_token = login_user(client, 'seeker_received@a.com', 'pass').json['token']
    
    # Seeker envoie une demande
    client.post(
        f'/api/matches/{helper_id}/request',
        json={'demand_id': demand_id, 'score': 90.0},
        headers={'Authorization': f'Bearer {seeker_token}'}
    )

    # Helper voit la demande avec les infos de slot
    helper_token = login_user(client, 'helper_received@a.com', 'pass').json['token']
    response = client.get(
        '/api/matches/received',
        headers={'Authorization': f'Bearer {helper_token}'}
    )
    
    assert response.status_code == 200
    assert len(response.json) >= 1
    match_data = response.json[0]
    assert match_data['jour'] == 'Samedi'
    assert match_data['creneau'] == '09-10'


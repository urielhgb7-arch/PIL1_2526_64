import pytest
from app.database import db


def register_user(client, payload):
    return client.post('/api/auth/register', json=payload)


def login_user(client, email, password):
    return client.post('/api/auth/login', json={'email': email, 'password': password})


class TestAuth:
    def test_signup_success(self, client):
        payload = {
            'email': 'test@example.com',
            'password': 'password123',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'filiere': 'GL',
            'niveau': 'L2'
        }
        resp = register_user(client, payload)
        assert resp.status_code == 201
        assert 'Compte créé avec succès' in resp.json['message']

    def test_signup_missing_fields(self, client):
        resp = register_user(client, {'email': 'incomplete@test.com'})
        assert resp.status_code == 400
        assert 'Champs obligatoires manquants' in resp.json['message']

    def test_signup_duplicate_email(self, client):
        payload = {
            'email': 'duplicate@test.com',
            'password': 'pass123',
            'nom': 'Test',
            'prenom': 'User',
            'filiere': 'GL',
            'niveau': 'L1'
        }
        register_user(client, payload)
        resp = register_user(client, payload)
        assert resp.status_code == 400
        assert resp.json['message'] == 'Cet email existe déjà'

    def test_signin_success(self, client):
        payload = {
            'email': 'signin@test.com',
            'password': 'securepass',
            'nom': 'Sign',
            'prenom': 'In',
            'filiere': 'RSI',
            'niveau': 'L3'
        }
        register_user(client, payload)
        resp = login_user(client, 'signin@test.com', 'securepass')
        assert resp.status_code == 200
        assert 'token' in resp.json
        assert resp.json['user']['email'] == 'signin@test.com'

    def test_signin_invalid_credentials(self, client):
        resp = login_user(client, 'unknown@test.com', 'wrongpass')
        assert resp.status_code == 401
        assert resp.json['message'] == 'Identifiants invalides'

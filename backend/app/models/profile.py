from flask import jsonify
from app.database import db
from datetime import datetime, timezone

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    filiere = db.Column(db.String(50), nullable=False)
    niveau = db.Column(db.String(10), nullable=False)
    format_preference = db.Column(db.String(20), nullable=False, default='hybride')
    bio = db.Column(db.Text)
    telephone = db.Column(db.String(20))
    avatar_url = db.Column(db.Text, default='https://via.placeholder.com/150')  # ← AJOUTE ÇA
    disponible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    disponibilites = db.relationship('Disponible', backref='profile', cascade="all, delete-orphan")
    offers = db.relationship('Offer', backref='profile', cascade="all, delete-orphan")
    demands = db.relationship('Demand', backref='profile', cascade="all, delete-orphan")
    competences = db.relationship('ProfilCompetence', backref='profile', cascade="all, delete-orphan")
    lacunes = db.relationship('ProfilLacune', backref='profile', cascade="all, delete-orphan")

class Disponible(db.Model):
    __tablename__ = 'disponibilites'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    jour = db.Column(db.String(15), nullable=False)
    creneau = db.Column(db.String(50), nullable=False)
    is_reserved = db.Column(db.Boolean, default=False, nullable=False)
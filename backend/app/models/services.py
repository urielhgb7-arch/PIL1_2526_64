# backend/app/models/services.py
from app.database import db
from datetime import datetime

class Matiere(db.Model):
    __tablename__ = 'matieres'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)


class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    # FK vers matieres — cohérent avec schema.sql
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matiere = db.relationship('Matiere', foreign_keys=[matiere_id])


class Demand(db.Model):
    __tablename__ = 'demands'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    # FK vers matieres — cohérent avec schema.sql
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matiere = db.relationship('Matiere', foreign_keys=[matiere_id])


class ProfilCompetence(db.Model):
    __tablename__ = 'profil_competences'
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), primary_key=True)
    niveau = db.Column(db.String(20), default='Intermédiaire')


class ProfilLacune(db.Model):
    __tablename__ = 'profil_lacunes'
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), primary_key=True)
    priorite = db.Column(db.String(20), default='Moyenne')

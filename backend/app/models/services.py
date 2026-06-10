# backend/app/models/services.py
from app.database import db
from datetime import datetime, timezone

class Matiere(db.Model):
    __tablename__ = 'matieres'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    annee = db.Column(db.String(10), nullable=True)
    filiere = db.Column(db.String(50), nullable=True)

    offers = db.relationship('Offer', back_populates='matiere', cascade='all, delete-orphan')
    demands = db.relationship('Demand', back_populates='matiere', cascade='all, delete-orphan')
    competences = db.relationship('ProfilCompetence', back_populates='matiere', cascade='all, delete-orphan')
    lacunes = db.relationship('ProfilLacune', back_populates='matiere', cascade='all, delete-orphan')


# backend/app/models/services.py — Offer
class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    description = db.Column(db.Text)
    jour = db.Column(db.String(15), nullable=True)
    creneau = db.Column(db.String(10), nullable=True)
    format_preference = db.Column(db.String(20), default='hybride')
    disponibilites = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    matiere = db.relationship('Matiere', back_populates='offers')

class Demand(db.Model):
    __tablename__ = 'demands'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    jour = db.Column(db.String(15), nullable=True)
    creneau = db.Column(db.String(10), nullable=True)
    description = db.Column(db.Text)
    urgence = db.Column(db.String(20), default='Moyenne')
    format_preference = db.Column(db.String(20), default='hybride')
    disponibilites = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    matiere = db.relationship('Matiere', back_populates='demands')


class ProfilCompetence(db.Model):
    __tablename__ = 'profil_competences'
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), primary_key=True)
    niveau = db.Column(db.String(20), default='Intermédiaire')
    is_available_to_help = db.Column(db.Boolean, default=True, nullable=False)

    matiere = db.relationship('Matiere', back_populates='competences')


class ProfilLacune(db.Model):
    __tablename__ = 'profil_lacunes'
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key=True)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), primary_key=True)
    priorite = db.Column(db.String(20), default='Moyenne')

    matiere = db.relationship('Matiere', back_populates='lacunes')


class Matching(db.Model):
    __tablename__ = 'matching'

    id           = db.Column(db.Integer, primary_key=True)
    user_one_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # demandeur
    user_two_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # candidat
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # qui a swipé
    demand_id    = db.Column(db.Integer, db.ForeignKey('demands.id'), nullable=False)
    offer_id     = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=True)
    matiere_id   = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    status       = db.Column(db.String(20), nullable=False, default='pending')         # pending/accepted/rejected
    score        = db.Column(db.Float, nullable=False)
    created_at   = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    matiere = db.relationship('Matiere', foreign_keys=[matiere_id])
    demand = db.relationship('Demand', foreign_keys=[demand_id])

    __table_args__ = (
        db.UniqueConstraint('user_one_id', 'user_two_id', 'demand_id', name='unique_match'),
    )


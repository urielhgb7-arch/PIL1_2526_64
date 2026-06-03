from app.database import db

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Demand(db.Model):
    __tablename__ = 'demands'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
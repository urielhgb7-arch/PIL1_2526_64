#!/usr/bin/env python3
"""Seed the matieres table from the frontend DEFAULT_MATIERES list."""
import os
import sys
from dotenv import load_dotenv

env_file = '.env.local' if os.path.exists('.env.local') else '.env'
load_dotenv(env_file)

from app import create_app
from app.database import db
from app.models import Matiere

MATIERES = [
    {"nom": "Algorithmique", "filiere": "GL", "annee": "L1"},
    {"nom": "Structures de donnees", "filiere": "GL", "annee": "L2"},
    {"nom": "Base de donnees SQL", "filiere": "GL", "annee": "L1"},
    {"nom": "Programmation Orientee Objet", "filiere": "GL", "annee": "L2"},
    {"nom": "Genie logiciel", "filiere": "GL", "annee": "L3"},
    {"nom": "Architecture des ordinateurs", "filiere": "GL", "annee": "L1"},
    {"nom": "Systemes d'exploitation", "filiere": "GL", "annee": "L2"},
    {"nom": "Web Development", "filiere": "GL", "annee": "L2"},
    {"nom": "Reseaux informatiques", "filiere": "RSI", "annee": "L1"},
    {"nom": "Securite des reseaux", "filiere": "RSI", "annee": "L2"},
    {"nom": "Telecommunications", "filiere": "RSI", "annee": "L2"},
    {"nom": "Administration systeme", "filiere": "RSI", "annee": "L3"},
    {"nom": "Cyberdefense", "filiere": "Securite", "annee": "L3"},
    {"nom": "Cryptographie", "filiere": "Securite", "annee": "L2"},
    {"nom": "Securite des applications", "filiere": "Securite", "annee": "L3"},
    {"nom": "Audit de securite", "filiere": "Securite", "annee": "L3"},
    {"nom": "Intelligence artificielle", "filiere": "GL", "annee": "L3"},
    {"nom": "Machine Learning", "filiere": "GL", "annee": "M1"},
    {"nom": "Big Data", "filiere": "RSI", "annee": "M1"},
    {"nom": "Cloud Computing", "filiere": "GL", "annee": "M1"},
    {"nom": "Developpement mobile", "filiere": "GL", "annee": "L3"},
    {"nom": "Gestion de projet informatique", "filiere": "GL", "annee": "M2"},
    {"nom": "Langage SQL avance", "filiere": "RSI", "annee": "L3"},
    {"nom": "Administration de bases de donnees", "filiere": "RSI", "annee": "M1"},
    {"nom": "Securite web", "filiere": "Securite", "annee": "L3"},
    {"nom": "Ethical Hacking", "filiere": "Securite", "annee": "M1"},
]

app = create_app()

with app.app_context():
    existing = Matiere.query.count()
    if existing > 0:
        print(f"Matières déjà présentes ({existing}), aucune action nécessaire.")
        sys.exit(0)

    for m in MATIERES:
        mat = Matiere(nom=m["nom"], filiere=m["filiere"], annee=m["annee"])
        db.session.add(mat)

    db.session.commit()
    print(f"✅ {len(MATIERES)} matières insérées avec succès.")

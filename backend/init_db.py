#!/usr/bin/env python3
"""
Script d'initialisation et de seed de la base de données locale.

Utilisation:
    python init_db.py          # Crée les tables et seed les données
    python init_db.py --drop   # Supprime tout et recommence (ATTENTION!)
"""

import os
import sys
from dotenv import load_dotenv

# Charge .env.local si présent
env_file = '.env.local' if os.path.exists('.env.local') else '.env'
load_dotenv(env_file)

from app import create_app
from app.database import db
from app.models import User, Profile, Matiere

app = create_app()

def init_db(drop_all=False):
    """Initialise la base de données."""
    with app.app_context():
        if drop_all:
            print("🗑️  Suppression de toutes les tables...")
            db.drop_all()
        
        print("📊 Création des tables...")
        db.create_all()
        
        # Vérifie si des matières existent déjà
        if Matiere.query.first():
            print("✅ Les matières existent déjà. Aucune action supplémentaire.")
            return
        
        print("🌱 Seed des matières...")
        
        matieres_data = [
            # Informatique
            {"nom": "Python", "filiere": "Informatique", "annee": "1"},
            {"nom": "JavaScript", "filiere": "Informatique", "annee": "1"},
            {"nom": "Bases de Données", "filiere": "Informatique", "annee": "2"},
            {"nom": "Développement Web", "filiere": "Informatique", "annee": "2"},
            {"nom": "Mobile Development", "filiere": "Informatique", "annee": "3"},
            {"nom": "Machine Learning", "filiere": "Informatique", "annee": "3"},
            
            # Gestion
            {"nom": "Comptabilité", "filiere": "Gestion", "annee": "1"},
            {"nom": "Finance d'Entreprise", "filiere": "Gestion", "annee": "2"},
            {"nom": "Management", "filiere": "Gestion", "annee": "2"},
            {"nom": "Stratégie d'Entreprise", "filiere": "Gestion", "annee": "3"},
            
            # Marketing
            {"nom": "Marketing Digital", "filiere": "Marketing", "annee": "1"},
            {"nom": "Communication", "filiere": "Marketing", "annee": "1"},
            {"nom": "Branding", "filiere": "Marketing", "annee": "2"},
            {"nom": "Analytics", "filiere": "Marketing", "annee": "3"},
            
            # Réseaux
            {"nom": "Réseaux TCP/IP", "filiere": "Réseaux", "annee": "1"},
            {"nom": "Sécurité Informatique", "filiere": "Réseaux", "annee": "2"},
            {"nom": "Administration Systèmes", "filiere": "Réseaux", "annee": "2"},
            {"nom": "Cloud Computing", "filiere": "Réseaux", "annee": "3"},
            
            # Design
            {"nom": "UI/UX Design", "filiere": "Design", "annee": "1"},
            {"nom": "Graphisme", "filiere": "Design", "annee": "1"},
            {"nom": "Motion Design", "filiere": "Design", "annee": "2"},
            {"nom": "3D Design", "filiere": "Design", "annee": "3"},
            
            # Finance
            {"nom": "Mathématiques Financières", "filiere": "Finance", "annee": "1"},
            {"nom": "Microéconomie", "filiere": "Finance", "annee": "1"},
            {"nom": "Analyse Financière", "filiere": "Finance", "annee": "2"},
            {"nom": "Investissements", "filiere": "Finance", "annee": "3"},
        ]
        
        for mat_data in matieres_data:
            matiere = Matiere(**mat_data)
            db.session.add(matiere)
        
        try:
            db.session.commit()
            print(f"✅ {len(matieres_data)} matières créées avec succès!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors du seed des matières: {e}")
            return False
        
        # Statistiques finales
        matieres_count = Matiere.query.count()
        users_count = User.query.count()
        profiles_count = Profile.query.count()
        
        print("\n📈 Statistiques:")
        print(f"  - Matières: {matieres_count}")
        print(f"  - Utilisateurs: {users_count}")
        print(f"  - Profils: {profiles_count}")
        
        return True

if __name__ == '__main__':
    drop_all = '--drop' in sys.argv
    
    if drop_all:
        confirm = input("⚠️  Êtes-vous sûr? Cela supprimera TOUTES les données. (yes/no): ")
        if confirm != "yes":
            print("❌ Opération annulée.")
            sys.exit(1)
    
    success = init_db(drop_all=drop_all)
    
    if success:
        print("\n✨ Base de données initialisée avec succès!")
        print("📌 Vous pouvez maintenant lancer: python run.py")
    else:
        print("\n❌ Erreur lors de l'initialisation.")
        sys.exit(1)

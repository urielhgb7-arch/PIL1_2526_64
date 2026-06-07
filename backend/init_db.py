#!/usr/bin/env python3
"""
Script d'initialisation et de seed de la base de données locale.

Utilisation:
    python init_db.py          # Crée les tables et seed les données
    python init_db.py --drop   # Supprime tout et recommence (ATTENTION!)
"""

#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

env_file = '.env.local' if os.path.exists('.env.local') else '.env'
load_dotenv(env_file)

from app import create_app
from app.database import db
from app.models import User, Profile

app = create_app()

def init_db(drop_all=False):
    with app.app_context():
        if drop_all:
            print("🗑️  Suppression de toutes les tables...")
            db.drop_all()
        
        print("📊 Création des tables...")
        db.create_all()
        print("📌 Tables créées. Lance ton script SQL pour insérer les matières :")
        print("   psql -U postgres -d mentorlink -f matieres_ifri.sql")

        # Statistiques finales
        matieres_count = db.session.execute(db.text("SELECT COUNT(*) FROM matieres")).scalar()
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
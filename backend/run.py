import os
from dotenv import load_dotenv
from pathlib import Path

# Charge .env.local si on est en dev local, sinon .env (production)
env_file = '.env.local' if os.path.exists('.env.local') else '.env'
load_dotenv(env_file)

from app import create_app
from app.database import db

app = create_app()

def init_db_if_needed():
    """Vérifie et initialise la DB si nécessaire (dev mode uniquement)."""
    with app.app_context():
        flask_env = os.getenv('FLASK_ENV', 'development')
        
        if flask_env == 'development':
            base_dir = Path(__file__).resolve().parent
            instance_dir = base_dir / 'instance'
            db_path = instance_dir / 'dev.db'
            instance_dir.mkdir(parents=True, exist_ok=True)
            
            # Si la DB n'existe pas ou est vide, initialise-la
            if not db_path.exists() or db_path.stat().st_size == 0:
                print("⚠️  Base de données non trouvée. Initialisation en cours...")
                print("📌 Vous pouvez aussi lancer: python init_db.py")
                
                try:
                    db.create_all()
                    print("✅ Tables créées.")
                    
                    # Seed des matières
                    from app.models import Matiere
                    
                    if Matiere.query.first() is None:
                        matieres_data = [
                            {"nom": "Algorithmique", "filiere": "Informatique", "annee": "L1"},
                            {"nom": "Architecture des ordinateurs", "filiere": "Informatique", "annee": "L1"},
                            {"nom": "Base de données (SQL)", "filiere": "Informatique", "annee": "L2"},
                            {"nom": "Programmation Web (HTML/CSS/JS)", "filiere": "Informatique", "annee": "L2"},
                            {"nom": "Réseaux et Télécoms", "filiere": "Informatique", "annee": "L1"},
                            {"nom": "Système d'exploitation Linux", "filiere": "Informatique", "annee": "L1"},
                            {"nom": "Génie Logiciel", "filiere": "Informatique", "annee": "L3"},
                            {"nom": "Intelligence Artificielle", "filiere": "Informatique", "annee": "L3"},
                            {"nom": "Cybersécurité", "filiere": "Informatique", "annee": "M1"},
                            {"nom": "Cloud Computing", "filiere": "Informatique", "annee": "M1"},
                            {"nom": "Data Science", "filiere": "Informatique", "annee": "M2"},
                            {"nom": "DevOps", "filiere": "Informatique", "annee": "M1"},
                            {"nom": "Mobile (Android/iOS)", "filiere": "Informatique", "annee": "L3"},
                        ]
                        
                        for mat_data in matieres_data:
                            db.session.add(Matiere(**mat_data))
                        
                        db.session.commit()
                        print(f"✅ {len(matieres_data)} matières créées.")
                
                except Exception as e:
                    print(f"❌ Erreur lors de l'initialisation: {e}")

if __name__ == '__main__':
    init_db_if_needed()
    print(f"🚀 Lancement du serveur Flask en mode {os.getenv('FLASK_ENV', 'development')}...")
    app.run(debug=os.getenv('FLASK_ENV') == 'development')

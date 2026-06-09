import os
from dotenv import load_dotenv
from pathlib import Path

# Charge .env.local si on est en dev local, sinon .env (production)
base_dir = Path(__file__).resolve().parent
env_file = base_dir / '.env.local'
if not env_file.exists():
    env_file = base_dir / '.env'
load_dotenv(env_file)

from app import create_app
from app.sockets.chat import socketio
from app.database import db

app = create_app()

# Initialiser la base de données en développement
with app.app_context():
    import os
    if os.getenv('FLASK_ENV') != 'production':
        try:
            from sqlalchemy_utils import database_exists, create_database
            if not database_exists(db.engine.url):
                create_database(db.engine.url)
                print("Base de données créée automatiquement !")
            db.create_all()
            try:
                from flask_migrate import upgrade
                upgrade()
            except Exception as mig_err:
                print(f"Migrations ignorées: {mig_err}")
            print("Database tables initialized successfully")
        except Exception as db_error:
            print(f"Database initialization warning: {db_error}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    print(f"Lancement du serveur Flask en mode {os.getenv('FLASK_ENV', 'development')} sur le port {port}...")
    # Pour lancer les tests : cd backend && pytest tests/
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)

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
from app.database import db
from app.sockets.chat import socketio

app = create_app()


if __name__ == '__main__':
    print(f"Lancement du serveur Flask en mode {os.getenv('FLASK_ENV', 'development')}...")
    socketio.run(app, debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0')

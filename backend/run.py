import os
from dotenv import load_dotenv

# Charge .env.local si on est en dev, sinon .env
env_file = '.env.local' if os.path.exists('.env.local') else '.env'
load_dotenv(env_file)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
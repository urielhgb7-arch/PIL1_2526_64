import os
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent
env_file = base_dir / '.env.local'
if not env_file.exists():
    env_file = base_dir / '.env'
load_dotenv(env_file)

from app import app
from app.database import db

# L'initialisation de la base de donnees se fait dans un hook before_first_request
# pour eviter les conflits de session avec le modele de fork de gunicorn.
_init_done = False

@app.before_request
def _init_db_once():
    global _init_done
    if _init_done:
        return
    _init_done = True
    import logging
    logger = logging.getLogger(__name__)
    # Disposer l'engine herite du processus parent (gunicorn fork)
    try:
        db.engine.dispose()
        logger.info("Engine disposed (post-fork cleanup)")
    except Exception as e:
        logger.warning(f"Engine dispose warning: {e}")
    if os.getenv('FLASK_ENV') != 'production':
        try:
            from sqlalchemy_utils import database_exists, create_database
            if not database_exists(db.engine.url):
                create_database(db.engine.url)
                logger.info("Base de donnees creee automatiquement !")
            db.create_all()
            try:
                from flask_migrate import upgrade
                upgrade()
            except Exception:
                pass
            logger.info("Database tables initialized successfully")
        except Exception as db_error:
            logger.warning(f"Database initialization warning: {db_error}")
    else:
        try:
            db.create_all()
            logger.info("Database tables verified in production")
        except Exception as e:
            logger.warning(f"Could not create tables (will retry): {e}")
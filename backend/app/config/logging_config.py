# backend/app/config/logging_config.py
"""
Configuration centralisée du logging pour toute l'application
"""
import logging
import logging.handlers
from pathlib import Path
import os

def setup_logging(app):
    """Configure les logs pour Flask et l'app"""
    
    # Créer dossier logs s'il n'existe pas
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Format des logs
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Handler fichier (rotation)
    log_file = logs_dir / 'app.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler console (en développement)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        root_logger.addHandler(console_handler)
    
    # Logger Flask (moins verbeux)
    logging.getLogger('flask.app').setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    
    app.logger.info("Logging configuré")

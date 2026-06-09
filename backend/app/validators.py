import re
from functools import wraps
from enum import Enum
from flask import request, jsonify
from app.database import db
from app.models.services import Matiere


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BENIN_PHONE_RE = re.compile(r"^01[4569]\d{7}$")

# ─── ENUMS VALIDATION ────────────────────────────────────────────────────────
class FormatPreference(str, Enum):
    """Format d'apprentissage supportés"""
    PRESENTIEL = "presentiel"
    EN_LIGNE = "en_ligne"
    HYBRIDE = "hybride"

class Niveau(str, Enum):
    """Niveaux académiques"""
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    M1 = "M1"
    M2 = "M2"

class NiveauCompetence(str, Enum):
    """Niveaux de compétence"""
    DEBUTANT = "Débutant"
    INTERMEDIAIRE = "Intermédiaire"
    AVANCE = "Avancé"
    EXPERT = "Expert"

class PriorityLevel(str, Enum):
    """Niveaux de priorité pour les lacunes"""
    BASSE = "Basse"
    MOYENNE = "Moyenne"
    HAUTE = "Haute"
    URGENTE = "Urgente"

class Day(str, Enum):
    """Jours de la semaine"""
    LUNDI = "Lundi"
    MARDI = "Mardi"
    MERCREDI = "Mercredi"
    JEUDI = "Jeudi"
    VENDREDI = "Vendredi"
    SAMEDI = "Samedi"
    DIMANCHE = "Dimanche"

class NotificationType(str, Enum):
    """Types de notifications"""
    MATCH_SYSTEM = "match_system"
    MESSAGE = "message"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    GENERAL = "general"

VALID_FORMAT_PREFERENCES = {e.value for e in FormatPreference}
VALID_NIVEAUX = {e.value for e in Niveau}
VALID_COMPETENCE_LEVELS = {e.value for e in NiveauCompetence}
VALID_PRIORITY_LEVELS = {e.value for e in PriorityLevel}
VALID_DAYS = {e.value for e in Day}
VALID_CRENTAUX = {
    '08-09', '09-10', '10-11', '11-12',
    '12-13', '13-14', '14-15', '15-16',
    '16-17', '17-18', '18-19', '19-20',
    '20-21', '21-22'
}
VALID_NOTIFICATION_TYPES = {e.value for e in NotificationType}


def is_valid_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email))


def is_valid_format_preference(value: str) -> bool:
    """Valide format d'apprentissage"""
    return bool(value and value in VALID_FORMAT_PREFERENCES)


def is_valid_niveau(value: str) -> bool:
    """Valide niveau académique"""
    return bool(value and value in VALID_NIVEAUX)


def is_valid_competence_level(value: str) -> bool:
    """Valide niveau de compétence"""
    return bool(value and value in VALID_COMPETENCE_LEVELS)


def is_valid_priority_level(value: str) -> bool:
    """Valide niveau de priorité"""
    return bool(value and value in VALID_PRIORITY_LEVELS)


def is_valid_creneau(value: str) -> bool:
    """Valide créneau horaire"""
    return bool(value and value in VALID_CRENTAUX)


def is_valid_day(value: str) -> bool:
    """Valide jour de la semaine"""
    return bool(value and value in VALID_DAYS)


def is_valid_notification_type(value: str) -> bool:
    """Valide type de notification"""
    return bool(value and value in VALID_NOTIFICATION_TYPES)


def is_valid_benin_phone(value: str) -> bool:
    """Valide un numéro béninois format 01[4569] + 7 chiffres (10 total)"""
    return bool(value and BENIN_PHONE_RE.match(value))


def require_fields(data: dict, fields: list) -> list:
    """Retourne liste des champs manquants"""
    missing = [f for f in fields if not data.get(f)]
    return missing


def matiere_exists(matiere_id: int) -> bool:
    """Vérifie qu'une matière existe"""
    if not matiere_id:
        return False
    return db.session.get(Matiere, matiere_id) is not None


def validate_json(required_fields=None, email_field=None):
    """Decorator for simple JSON validation in routes.

    - required_fields: list of field names that must be present and truthy
    - email_field: name of the field to validate as email
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(force=True, silent=True) or {}
            if required_fields:
                missing = require_fields(data, required_fields)
                if missing:
                    return jsonify({
                        "message": "Champs obligatoires manquants",
                        "required": required_fields,
                        "missing": missing
                    }), 400
            if email_field:
                email = data.get(email_field)
                if not is_valid_email(email):
                    return jsonify({"message": "Email invalide"}), 400
            # attach validated data to request for handler convenience
            request.validated_json = data
            return fn(*args, **kwargs)
        return wrapper
    return decorator

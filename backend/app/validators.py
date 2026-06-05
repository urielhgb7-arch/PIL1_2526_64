import re
from functools import wraps
from flask import request, jsonify
from app.database import db
from app.models.services import Matiere


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_FORMAT_PREFERENCES = {'presentiel', 'en_ligne', 'hybride'}


def is_valid_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email))


def is_valid_format_preference(value: str) -> bool:
    return bool(value and value in VALID_FORMAT_PREFERENCES)


def require_fields(data: dict, fields: list):
    missing = [f for f in fields if not data.get(f)]
    return missing


def matiere_exists(matiere_id: int) -> bool:
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

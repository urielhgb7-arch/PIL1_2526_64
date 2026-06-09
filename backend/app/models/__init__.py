
# backend/app/models/__init__.py
from app.models.user import User
from app.models.profile import Profile, Disponible
from app.models.services import Offer, Demand, Matiere, ProfilCompetence, ProfilLacune, Matching
from app.models.messages import Conversation, Message , Notification
from app.models.password_reset_token import PasswordResetToken


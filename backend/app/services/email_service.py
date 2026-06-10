import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from typing import Optional

logger = logging.getLogger(__name__)


def _send_email(to_email: str, subject: str, html: str) -> bool:
    """Envoie un email HTML via SMTP. Retourne True si réussi, False sinon."""
    config = current_app.config
    smtp_server = config.get('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = config.get('MAIL_PORT', 587)
    smtp_user = config.get('MAIL_USERNAME', '')
    smtp_pass = config.get('MAIL_PASSWORD', '')
    mail_from = config.get('MAIL_FROM', smtp_user)

    if not smtp_user or not smtp_pass:
        logger.warning("SMTP non configuré — email non envoyé")
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = to_email
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(mail_from, [to_email], msg.as_string())
        logger.info(f"Email envoyé à {to_email[:10]}*** — {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP Gmail : échec d'authentification. "
            "Utilise un mot de passe d'application (https://myaccount.google.com/apppasswords)"
        )
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Gmail : échec d'envoi à {to_email[:10]}*** : {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur envoi email : {e}", exc_info=True)
        return False


def send_password_reset_email(to_email: str, token: str) -> bool:
    """Envoie un email de réinitialisation de mot de passe via SMTP."""
    config = current_app.config
    frontend_url = config.get('FRONTEND_URL', 'http://localhost:5500')
    reset_link = f"{frontend_url.rstrip('/')}/pages/reset-password.html?token={token}"

    html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; padding: 32px;">
    <h2 style="color: #7C6FF7; margin-top: 0;">Réinitialisation de mot de passe</h2>
    <p>Bonjour,</p>
    <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
    <p>Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe :</p>
    <div style="text-align: center; margin: 32px 0;">
      <a href="{reset_link}"
         style="display: inline-block; padding: 14px 28px; background: #7C6FF7; color: #fff;
                text-decoration: none; border-radius: 6px; font-size: 16px;">
        Réinitialiser mon mot de passe
      </a>
    </div>
    <p style="color: #666; font-size: 14px;">Ce lien expire dans <strong>1 heure</strong>.</p>
    <p style="color: #666; font-size: 14px;">Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">Équipe MentorLink</p>
  </div>
</body>
</html>"""
    return _send_email(to_email, "Réinitialisation de votre mot de passe - MentorLink", html)


def send_match_notification_email(
    recipient_email: str,
    subject: str,
    sender_name: str,
    score: Optional[float] = None,
    match_type: str = "request",
    accept_url: Optional[str] = None,
) -> bool:
    """Envoie un email de notification pour un événement de matching.

    Args:
        recipient_email: Destinataire
        subject: Sujet de l'email
        sender_name: Nom de l'expéditeur de l'action
        score: Score de compatibilité (optionnel)
        match_type: 'request', 'accept', ou 'reject'
        accept_url: Lien vers le dashboard (optionnel)
    """
    config = current_app.config
    frontend_url = config.get('FRONTEND_URL', 'http://localhost:5500')

    if match_type == "request":
        body = f"""<p>{sender_name} souhaite votre aide en mentorat.</p>"""
        if score is not None:
            body += f"""<p style="font-size: 24px; color: #7C6FF7; font-weight: bold; text-align: center; margin: 20px 0;">Compatibilité : {score}%</p>"""
        body += f"""<div style="text-align: center; margin: 24px 0;">
          <a href="{accept_url or frontend_url}"
             style="display: inline-block; padding: 12px 24px; background: #7C6FF7; color: #fff;
                    text-decoration: none; border-radius: 6px;">Voir la demande</a>
        </div>"""
    elif match_type == "accept":
        body = f"""<p style="font-size: 18px; color: #2DD4A0; font-weight: bold; text-align: center;">✅ {sender_name} a accepté votre demande !</p>
        <p>Vous pouvez maintenant discuter avec {sender_name} via le chat.</p>
        <div style="text-align: center; margin: 24px 0;">
          <a href="{accept_url or frontend_url}"
             style="display: inline-block; padding: 12px 24px; background: #2DD4A0; color: #fff;
                    text-decoration: none; border-radius: 6px;">Ouvrir la conversation</a>
        </div>"""
    elif match_type == "reject":
        body = f"""<p style="font-size: 16px; color: #F97066;">{sender_name} n'est pas disponible pour le moment.</p>
        <p>Ne vous découragez pas — d'autres mentors sont disponibles.</p>
        <div style="text-align: center; margin: 24px 0;">
          <a href="{frontend_url}/pages/matching.html"
             style="display: inline-block; padding: 12px 24px; background: #7C6FF7; color: #fff;
                    text-decoration: none; border-radius: 6px;">Voir d'autres suggestions</a>
        </div>"""
    else:
        body = f"<p>{sender_name}</p>"

    html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; padding: 32px;">
    <h2 style="color: #7C6FF7; margin-top: 0;">MentorLink — Notification</h2>
    {body}
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">Équipe MentorLink</p>
  </div>
</body>
</html>"""
    return _send_email(recipient_email, subject, html)


def send_verification_email(to_email: str, token: str) -> bool:
    """Envoie un email de vérification d'email via SMTP."""
    config = current_app.config
    frontend_url = config.get('FRONTEND_URL', 'http://localhost:5500')
    verify_link = f"{frontend_url.rstrip('/')}/pages/verify-email.html?token={token}"

    html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; padding: 32px;">
    <h2 style="color: #7C6FF7; margin-top: 0;">Vérification de votre email</h2>
    <p>Bonjour,</p>
    <p>Merci pour votre inscription sur MentorLink !</p>
    <p>Veuillez cliquer sur le bouton ci-dessous pour vérifier votre adresse email :</p>
    <div style="text-align: center; margin: 32px 0;">
      <a href="{verify_link}"
         style="display: inline-block; padding: 14px 28px; background: #7C6FF7; color: #fff;
                text-decoration: none; border-radius: 6px; font-size: 16px;">
        Vérifier mon email
      </a>
    </div>
    <p style="color: #666; font-size: 14px;">Ce lien expire dans <strong>24 heures</strong>.</p>
    <p style="color: #666; font-size: 14px;">Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">Équipe MentorLink</p>
  </div>
</body>
</html>"""
    return _send_email(to_email, "Vérification de votre email - MentorLink", html)

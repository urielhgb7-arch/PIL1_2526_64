import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, token: str) -> bool:
    """Envoie un email de réinitialisation de mot de passe via SMTP Gmail.
    
    Retourne True si l'envoi a réussi, False sinon.
    """
    config = current_app.config
    smtp_server = config.get('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = config.get('MAIL_PORT', 587)
    smtp_user = config.get('MAIL_USERNAME', '')
    smtp_pass = config.get('MAIL_PASSWORD', '')
    mail_from = config.get('MAIL_FROM', smtp_user)
    frontend_url = config.get('FRONTEND_URL', 'http://localhost:5500')

    if not smtp_user or not smtp_pass:
        logger.error("MAIL_USERNAME et MAIL_PASSWORD doivent être configurés dans .env")
        return False

    reset_link = f"{frontend_url.rstrip('/')}/pages/reset-password.html?token={token}"

    subject = "Réinitialisation de votre mot de passe - MentorLink"
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
    <p style="color: #666; font-size: 14px;">
      Ce lien expire dans <strong>1 heure</strong>.
    </p>
    <p style="color: #666; font-size: 14px;">
      Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
    </p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">Équipe MentorLink</p>
  </div>
</body>
</html>"""

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
        logger.info(f"Email de réinit envoyé à {to_email[:10]}***")
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
        logger.error(f"Erreur inattendue lors de l'envoi d'email : {e}", exc_info=True)
        return False

from flask import Blueprint, request, jsonify
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.messages import Notification

logger = logging.getLogger(__name__)
notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def lister_notifications():
    """Liste les notifications de l'utilisateur"""
    current_user_id = int(get_jwt_identity())
    
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        query = Notification.query.filter_by(user_id=current_user_id)
        if unread_only:
            query = query.filter_by(is_read=False)

        notifications = query.order_by(Notification.created_at.desc()).all()

        result = [
            {
                'id': n.id,
                'titre': n.titre,
                'contenu': n.contenu,
                'type': n.type,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat()
            }
            for n in notifications
        ]

        unread_count = len([n for n in result if not n['is_read']])
        logger.info(f"✅ Notifications listées: {len(result)} total, {unread_count} non lues pour user={current_user_id}")
        
        return jsonify({
            "total": len(result),
            "unread_count": unread_count,
            "notifications": result
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur listing notifications: {str(e)[:100]}", exc_info=True)
        return jsonify({"message": "Erreur serveur"}), 500


@notifications_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def marquer_notification_lue(notif_id: int):
    """Marque une notification comme lue"""
    current_user_id = int(get_jwt_identity())
    
    try:
        notification = db.session.get(Notification, notif_id)

        if not notification:
            logger.warning(f"Notification inexistante: {notif_id}")
            return jsonify({'message': 'Notification introuvable'}), 404
            
        if notification.user_id != current_user_id:
            logger.warning(f"Accès non autorisé à notification {notif_id} par user={current_user_id}")
            return jsonify({'message': 'Accès refusé'}), 403

        if not notification.is_read:
            notification.is_read = True
            db.session.commit()
            logger.info(f"✅ Notification marquée lue: {notif_id}")
        else:
            logger.info(f"⏭️ Notification déjà lue: {notif_id}")

        return jsonify({'message': 'Notification marquée comme lue'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur marquage notification: {str(e)[:100]}", exc_info=True)
        return jsonify({'message': 'Erreur serveur'}), 500


@notifications_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def marquer_toutes_lues():
    """Marque toutes les notifications comme lues"""
    current_user_id = int(get_jwt_identity())
    
    try:
        notifications = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).all()

        count = len(notifications)
        for n in notifications:
            n.is_read = True
        
        db.session.commit()
        logger.info(f"✅ {count} notifications marquées lues pour user={current_user_id}")

        return jsonify({
            'message': f'{count} notifications marquées comme lues',
            'count': count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur marquage toutes notifications: {str(e)[:100]}", exc_info=True)
        return jsonify({'message': 'Erreur serveur'}), 500


@notifications_bp.route('/notifications/<int:notif_id>', methods=['DELETE'])
@jwt_required()
def supprimer_notification(notif_id: int):
    """Supprime une notification"""
    current_user_id = int(get_jwt_identity())
    
    try:
        notification = db.session.get(Notification, notif_id)

        if not notification:
            logger.warning(f"Notification inexistante pour suppression: {notif_id}")
            return jsonify({'message': 'Notification introuvable'}), 404
            
        if notification.user_id != current_user_id:
            logger.warning(f"Accès non autorisé suppression notification {notif_id} par user={current_user_id}")
            return jsonify({'message': 'Accès refusé'}), 403

        db.session.delete(notification)
        db.session.commit()
        logger.info(f"✅ Notification supprimée: {notif_id}")

        return jsonify({'message': 'Notification supprimée'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur suppression notification: {str(e)[:100]}", exc_info=True)
        return jsonify({'message': 'Erreur serveur'}), 500


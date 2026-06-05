from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.messages import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def lister_notifications():
    current_user_id = int(get_jwt_identity())
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

    return jsonify(result), 200


@notifications_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def marquer_notification_lue(notif_id):
    current_user_id = int(get_jwt_identity())
    notification = db.session.get(Notification, notif_id)

    if not notification:
        return jsonify({'message': 'Notification introuvable'}), 404
    if notification.user_id != current_user_id:
        return jsonify({'message': 'Accès refusé'}), 403

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return jsonify({'message': 'Notification marquée comme lue'}), 200

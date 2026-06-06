from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.services import Offer, Demand

offers_bp = Blueprint('offers', __name__)

# Créer une offre
@offers_bp.route('/offers', methods=['POST'])
@jwt_required()
def create_offer():
    user_id = get_jwt_identity()
    data = request.get_json()
    offer = Offer(
        profile_id=user_id,
        matiere=data['matiere'],
        description=data.get('description', '')
    )
    db.session.add(offer)
    db.session.commit()
    return jsonify({'message': 'Offre créée avec succès'}), 201

# Lire toutes les offres
@offers_bp.route('/offers', methods=['GET'])
def get_offers():
    offers = Offer.query.all()
    return jsonify([{
        'id': o.id,
        'matiere': o.matiere,
        'description': o.description
    } for o in offers]), 200

# Supprimer une offre
@offers_bp.route('/offers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_offer(id):
    offer = Offer.query.get_or_404(id)
    db.session.delete(offer)
    db.session.commit()
    return jsonify({'message': 'Offre supprimée'}), 200


# Créer une demande
@offers_bp.route('/demands', methods=['POST'])
@jwt_required()
def create_demand():
    user_id = get_jwt_identity()
    data = request.get_json()
    demand = Demand(
        profile_id=user_id,
        matiere=data['matiere'],
        description=data.get('description', '')
    )
    db.session.add(demand)
    db.session.commit()
    return jsonify({'message': 'Demande créée avec succès'}), 201

# Lire toutes les demandes
@offers_bp.route('/demands', methods=['GET'])
def get_demands():
    demands = Demand.query.all()
    return jsonify([{
        'id': d.id,
        'matiere': d.matiere,
        'description': d.description
    } for d in demands]), 200

# Supprimer une demande
@offers_bp.route('/demands/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_demand(id):
    demand = Demand.query.get_or_404(id)
    db.session.delete(demand)
    db.session.commit()
    return jsonify({'message': 'Demande supprimée'}), 200
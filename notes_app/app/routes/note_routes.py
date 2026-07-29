from flask import Blueprint, request, jsonify
from flask_login import current_user
from math import ceil
from ..models.note import Note
from ..schemas.note_schemas import NoteSchema, NoteUpdateSchema
from ..extensions import db
from ..utils import jwt_required

note_bp = Blueprint('notes', __name__)


def _error_response(messages, status_code=400):
    """Create error response in array format expected by clients"""
    if isinstance(messages, str):
        messages = [messages]
    return jsonify({'errors': messages}), status_code


def paginate(query, page, per_page):
    """Helper function for pagination"""
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total_pages = ceil(total / per_page) if per_page > 0 else 1
    
    return {
        'items': [item.to_dict() for item in items],
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

@note_bp.route('/', methods=['GET'])
@jwt_required
def get_notes():
    """Get all notes for current user with pagination"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination
        page = max(1, page)
        per_page = min(max(1, per_page), 100)
        
        # Query user's notes
        query = Note.query.filter_by(
            user_id=current_user.id
        ).order_by(Note.created_at.desc())
        
        result = paginate(query, page, per_page)
        return jsonify(result), 200
        
    except Exception as e:
        return _error_response('Failed to fetch notes', 500)

@note_bp.route('/', methods=['POST'])
@jwt_required
def create_note():
    """Create a new note"""
    try:
        schema = NoteSchema()
        data = schema.load(request.get_json())
        
        note = Note(
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'General'),
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'message': 'Note created successfully',
            'note': note.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return _error_response(str(e), 400)

@note_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required
def get_note(note_id):
    """Get a single note by ID"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            user_id=current_user.id
        ).first()
        
        if not note:
            return _error_response('Note not found', 404)
        
        return jsonify(note.to_dict()), 200
        
    except Exception as e:
        return _error_response('Failed to fetch note', 500)

@note_bp.route('/<int:note_id>', methods=['PATCH'])
@jwt_required
def update_note(note_id):
    """Update a note"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            user_id=current_user.id
        ).first()
        
        if not note:
            return _error_response('Note not found', 404)
        
        schema = NoteUpdateSchema()
        data = schema.load(request.get_json())
        note.update(data)
        db.session.commit()
        
        return jsonify({
            'message': 'Note updated successfully',
            'note': note.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return _error_response(str(e), 400)

@note_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required
def delete_note(note_id):
    """Delete a note"""
    try:
        note = Note.query.filter_by(
            id=note_id, 
            user_id=current_user.id
        ).first()
        
        if not note:
            return _error_response('Note not found', 404)
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'message': 'Note deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return _error_response('Failed to delete note', 500)

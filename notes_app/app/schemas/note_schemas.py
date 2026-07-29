from marshmallow import Schema, fields, validate

class NoteSchema(Schema):
    """Validation schema for notes"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(validate=validate.Length(max=50), load_default='General')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)

class NoteUpdateSchema(Schema):
    """Validation schema for note updates"""
    title = fields.Str(validate=validate.Length(min=1, max=200))
    content = fields.Str(validate=validate.Length(min=1))
    category = fields.Str(validate=validate.Length(max=50))

from marshmallow import Schema, fields
from sqlalchemy import Enum as SqlEnum
from enum import Enum as PyEnum

# Enum definitions
class TicketStatusEnum(PyEnum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'


class PriorityEnum(PyEnum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


# Plain Schemas
class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)  # Unique identifier for the user
    username = fields.Str(required=True)  # Required username field
    password = fields.Str(required=True, load_only=True)  # Password field (not included in output)
    role = fields.Str(required=True)  # User role (e.g., admin, support, user)


class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainTicketSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(validate=lambda s: s in [status.value for status in TicketStatusEnum])
    priority = fields.Str(validate=lambda s: s in [priority.value for priority in PriorityEnum])


# Detailed Schemas
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)


class UserSchema(PlainUserSchema):
    tickets_created = fields.List(fields.Nested("TicketSchema", dump_only=True))  # Tickets created by the user
    tickets_assigned = fields.List(fields.Nested("TicketSchema", dump_only=True))  # Tickets assigned to the user
    comments = fields.List(fields.Nested("CommentSchema", dump_only=True))  # Comments made by the user
    activity_logs = fields.List(fields.Nested("ActivityLogSchema", dump_only=True))  # Activity logs for the user

class LoginSchema(Schema):
    username = fields.Str(required=True)  # Required username field
    password = fields.Str(required=True, load_only=True)  # Required password field (not included in output)

class TicketSchema(PlainTicketSchema):
    created_by = fields.Int(required=True, load_only=True)  # User ID of the creator
    creator = fields.Nested(UserSchema(), dump_only=True)  # Nested schema for the creator
    assigned_to = fields.Int(allow_none=True, load_only=True)  # User ID of the assignee
    assignee = fields.Nested(UserSchema(), dump_only=True)  # Nested schema for the assignee
    created_at = fields.DateTime(dump_only=True)  # Auto-generated timestamp
    updated_at = fields.DateTime(dump_only=True)  # Auto-generated timestamp


class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Int(required=True)  # Associated ticket ID
    user_id = fields.Int(required=True)  # User who made the comment
    comment_text = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested(PlainUserSchema, dump_only=True)  # User who made the comment


class AttachmentSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Int(required=True)  # Associated ticket ID
    file_path = fields.Str(required=True)  # File path of the attachment
    uploaded_by = fields.Int(required=True)  # User ID of the uploader
    created_at = fields.DateTime(dump_only=True)  # Auto-generated timestamp



class ActivityLogSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Int(required=True)  # Associated ticket ID
    user_id = fields.Int(required=True)  # User who performed the action
    action = fields.Str(required=True)  # e.g., 'created', 'updated', 'assigned', 'closed'
    created_at = fields.DateTime(dump_only=True)  # Auto-generated timestamp
    user = fields.Nested(PlainUserSchema, dump_only=True)  # User who performed the action


# In schemas.py
class TicketUpdateSchema(Schema):
    title = fields.Str(required=False)  # Optional title field
    description = fields.Str(required=False)  # Optional description field
    status = fields.Str(validate=lambda s: s in TicketStatusEnum.__members__, required=False)  # Optional status field
    priority = fields.Str(validate=lambda s: s in PriorityEnum.__members__, required=False)  # Optional priority field
    assigned_to = fields.Int(allow_none=True, required=False)  # Optional user ID for assignment
from marshmallow import Schema, fields

# Plain Schemas
class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)  # Unique identifier for the user
    username = fields.Str(required=True)  # Required username field
    password = fields.Str(required=True, load_only=True)  # Password field (not included in output)
    role = fields.Str(required=True)  # User role (e.g., admin, support, user)


class PlainTicketSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(required=True)  # Status field
    priority = fields.Str(required=True)  # Priority field


# Detailed Schemas with Controlled Nesting
class TicketSchema(PlainTicketSchema):
    created_by = fields.Int(required=True, load_only=True)  # User ID of the creator
    creator_id = fields.Int(dump_only=True)  # User ID of the creator
    creator_username = fields.Str(dump_only=True)  # Username of the creator
    assigned_to = fields.Int(allow_none=True, load_only=True)  # User ID of the assignee
    assignee_id = fields.Int(allow_none=True, dump_only=True)  # User ID of the assignee
    assignee_username = fields.Str(allow_none=True, dump_only=True)  # Username of the assignee
    created_at = fields.DateTime(dump_only=True)  # Auto-generated timestamp
    updated_at = fields.DateTime(dump_only=True)  # Auto-generated timestamp


class UserSchema(PlainUserSchema):
    # Use lists to hold only the IDs and usernames of tickets
    tickets_created = fields.List(fields.Int(), dump_only=True)  # List of ticket IDs created
    tickets_assigned = fields.List(fields.Int(), dump_only=True)  # List of ticket IDs assigned


class TicketUpdateSchema(Schema):
    title = fields.Str(required=False)  # Optional title field
    description = fields.Str(required=False)  # Optional description field
    status = fields.Str(required=False)  # Optional status field
    priority = fields.Str(required=False)  # Optional priority field
    assigned_to = fields.Int(allow_none=True, required=False)  # Optional user ID for assignment


class LoginSchema(Schema):
    username = fields.Str(required=True)  # Required username field
    password = fields.Str(required=True, load_only=True)  # Required password field (not included in output)

# schemas.py
from marshmallow import Schema, fields

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=True)
    fullname = fields.Str(required=False)
    designation = fields.Str(required=False)
    approver = fields.Bool(required=False)


class PlainTicketSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(required=True)
    priority = fields.Str(required=True)
    category = fields.Str(required=False)
    subcategory = fields.Str(required=False)


class PlainCommentSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


class PlainAttachmentSchema(Schema):
    id = fields.Int(dump_only=True)
    filename = fields.Str(required=True)
    uploaded_at = fields.DateTime(dump_only=True)
    ticket_id = fields.Int(required=True)


class PlainActivityLogSchema(Schema):
    id = fields.Int(dump_only=True)
    action = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True)
    ticket_id = fields.Int(allow_none=True)


class TicketSchema(PlainTicketSchema):
    created_by = fields.Int(required=True, load_only=True)
    assigned_to = fields.Int(allow_none=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    creator = fields.Nested(PlainUserSchema, dump_only=True)
    assignee = fields.Nested(PlainUserSchema, dump_only=True)
    approver = fields.Nested(PlainUserSchema, dump_only=True)
    comments = fields.List(fields.Nested(PlainCommentSchema), dump_only=True)
    activity_logs = fields.List(fields.Nested(PlainActivityLogSchema), dump_only=True)
    attachments = fields.List(fields.Nested(PlainAttachmentSchema), dump_only=True)


class UserSchema(PlainUserSchema):
    tickets_created = fields.List(fields.Nested(PlainTicketSchema), dump_only=True)
    tickets_assigned = fields.List(fields.Nested(PlainTicketSchema), dump_only=True)
    tickets_approved = fields.List(fields.Nested(PlainTicketSchema), dump_only=True)
    comments = fields.List(fields.Nested(PlainCommentSchema), dump_only=True)
    activity_logs = fields.List(fields.Nested(PlainActivityLogSchema), dump_only=True)
    attachments = fields.List(fields.Nested(PlainAttachmentSchema), dump_only=True)


class UpdateUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=False, load_only=True)
    role = fields.Str(required=False)
    fullname = fields.Str(required=False)
    designation = fields.Str(required=False)
    approver = fields.Boolean(required=False)


class CommentSchema(PlainCommentSchema):
    ticket = fields.Nested(PlainTicketSchema, dump_only=True)
    user = fields.Nested(PlainUserSchema, dump_only=True)


class AttachmentSchema(PlainAttachmentSchema):
    ticket = fields.Nested(PlainTicketSchema, dump_only=True)


class ActivityLogSchema(PlainActivityLogSchema):
    user = fields.Nested(PlainUserSchema, dump_only=True)
    ticket = fields.Nested(PlainTicketSchema, allow_none=True, dump_only=True)


class TicketUpdateSchema(Schema):
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    status = fields.Str(required=False)
    priority = fields.Str(required=False)
    category = fields.Str(required=False)
    subcategory = fields.Str(required=False)
    assigned_to = fields.Int(allow_none=True, required=False)
    approved_by = fields.Int(allow_none=True, required=False)


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

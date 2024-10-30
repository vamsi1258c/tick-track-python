# attachment_api.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import AttachmentModel, TicketModel
from schemas import AttachmentSchema
from flask import request, send_file
import os
import mimetypes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

blp = Blueprint("Attachments", "attachments", description="Operations on attachments")
# Function to map file extensions to MIME types
def get_content_type(filepath):
    extension = os.path.splitext(filepath)[1]
    mime_types = {
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        # Add more MIME types as needed
    }
    return mime_types.get(extension, 'application/octet-stream')  # Default type


@blp.route("/ticket/<int:ticket_id>/attachments")
class AttachmentList(MethodView):
    @jwt_required()
    @blp.response(200, AttachmentSchema(many=True))
    def get(self, ticket_id):
        """Get all attachments for a specific ticket"""
        ticket = TicketModel.query.get_or_404(ticket_id)
        return ticket.attachments

    @jwt_required(fresh=True)
    @blp.arguments(AttachmentSchema)
    @blp.response(201, AttachmentSchema)
    def post(self, attachment_data, ticket_id):
        """Create a new attachment record for a specific ticket"""
        # Check if the ticket exists
        ticket = TicketModel.query.get_or_404(ticket_id)

        # Create a new AttachmentModel entry
        attachment = AttachmentModel(
            ticket_id=ticket_id,
            filename=attachment_data["filename"],  # Use filename from request
            filepath='/'  # Initially, filepath will be None
        )

        try:
            db.session.add(attachment)
            db.session.commit()
        except SQLAlchemyError as err:
            print(err);
            abort(500, message="An error occurred while saving the attachment record.")

        return attachment, 201  # Return created attachment record


@blp.route("/ticket/<int:ticket_id>/attachments/<int:attachment_id>/upload")
class AttachmentUpload(MethodView):
    @jwt_required(fresh=True)
    def post(self, ticket_id, attachment_id):
        """Upload the file for a specific attachment"""
        # Check if the attachment exists
        attachment = AttachmentModel.query.get_or_404(attachment_id)

        # Extract the file from the request
        if 'file' not in request.files:
            abort(400, message="No file part in the request.")

        file = request.files['file']

        if file.filename == '':
            abort(400, message="No selected file.")

        # Save the file to a designated location
        file_path = os.path.join(f"uploads/{ticket_id}", file.filename).replace('\\', '/')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        # Update the attachment record with the file path
        attachment.filepath = file_path

        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while saving the file path.")

        return {"Success":"Attachments saved"}, 201  # Return updated attachment


@blp.route("/ticket/<int:ticket_id>/attachment/<int:attachment_id>")
class Attachment(MethodView):
    @jwt_required()
    @blp.response(200, AttachmentSchema)
    def get(self, ticket_id, attachment_id):
        """Get a specific attachment by its ID"""
        attachment = AttachmentModel.query.filter_by(ticket_id=ticket_id, id=attachment_id).first_or_404()
        return attachment

    @jwt_required()
    def delete(self, ticket_id, attachment_id):
        """Delete a specific attachment"""
        attachment = AttachmentModel.query.filter_by(ticket_id=ticket_id, id=attachment_id).first_or_404()

        # Remove the file from the file system
        try:
            if os.path.exists(attachment.filepath):
                os.remove(attachment.filepath)
        except Exception as e:
            abort(500, message="An error occurred while deleting the file from the system.")

        try:
            db.session.delete(attachment)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the attachment from the database.")

        return {"message": "Attachment deleted."}



@blp.route("/ticket/<int:ticket_id>/attachments/<int:attachment_id>/download")
class AttachmentDownload(MethodView):
    @jwt_required()
    def get(self, ticket_id, attachment_id):
        """Download a specific attachment by its ID"""
        logging.info(f"Downloading attachment {attachment_id} for ticket {ticket_id}.")
        # Check if the attachment exists
        attachment = AttachmentModel.query.filter_by(ticket_id=ticket_id, id=attachment_id).first_or_404()

        # Check if the file exists
        if not os.path.exists(attachment.filepath):
            abort(404, message="File not found.")

        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(attachment.filepath)
        print("FileTyp", mime_type)

        try:
            response = send_file(attachment.filepath, as_attachment=True)

            # Set the correct Content-Type
            response.headers['Content-Type'] = mime_type or 'application/octet-stream'  # Fallback MIME type
            response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment.filepath)}"'

            # Disable caching
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response
        except Exception as e:
            abort(500, message=f"An error occurred while downloading the file: {str(e)}")

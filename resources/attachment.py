from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import AttachmentModel, TicketModel
from schemas import AttachmentSchema
from flask import request, send_file, current_app
import os
import mimetypes

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
        logger = current_app.logger
        ticket = TicketModel.query.get_or_404(ticket_id)
        logger.info(f"Retrieved attachments for ticket ID {ticket_id}.")
        return ticket.attachments

    @jwt_required(fresh=True)
    @blp.arguments(AttachmentSchema)
    @blp.response(201, AttachmentSchema)
    def post(self, attachment_data, ticket_id):
        """Create a new attachment record for a specific ticket"""
        logger = current_app.logger
        ticket = TicketModel.query.get_or_404(ticket_id)

        attachment = AttachmentModel(
            ticket_id=ticket_id,
            filename=attachment_data["filename"],
            filepath='/'
        )

        try:
            db.session.add(attachment)
            db.session.commit()
            logger.info(f"Created attachment for ticket ID {ticket_id}: {attachment_data['filename']}.")
        except SQLAlchemyError as err:
            logger.error(f"Error while saving attachment record: {err}")
            abort(500, message="An error occurred while saving the attachment record.")

        return attachment, 201


@blp.route("/ticket/<int:ticket_id>/attachments/<int:attachment_id>/upload")
class AttachmentUpload(MethodView):
    @jwt_required(fresh=True)
    def post(self, ticket_id, attachment_id):
        """Upload the file for a specific attachment"""
        logger = current_app.logger
        attachment = AttachmentModel.query.get_or_404(attachment_id)

        if 'file' not in request.files:
            logger.warning(
                f"No file part in the upload request for ticket ID {ticket_id}, attachment ID {attachment_id}.")
            abort(400, message="No file part in the request.")

        file = request.files['file']

        if file.filename == '':
            logger.warning(f"No file selected for upload for ticket ID {ticket_id}, attachment ID {attachment_id}.")
            abort(400, message="No selected file.")

        file_path = os.path.join(f"uploads/{ticket_id}", file.filename).replace('\\', '/')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        attachment.filepath = file_path

        try:
            db.session.commit()
            logger.info(
                f"File uploaded and saved for ticket ID {ticket_id}, attachment ID {attachment_id}: {file.filename}.")
        except SQLAlchemyError as e:
            logger.error(f"Error while saving file path to the database: {e}")
            abort(500, message="An error occurred while saving the file path.")

        return {"message": "Attachment saved successfully."}, 201


@blp.route("/ticket/<int:ticket_id>/attachment/<int:attachment_id>")
class Attachment(MethodView):
    @jwt_required()
    @blp.response(200, AttachmentSchema)
    def get(self, ticket_id, attachment_id):
        """Get a specific attachment by its ID"""
        logger = current_app.logger
        attachment = AttachmentModel.query.filter_by(ticket_id=ticket_id, id=attachment_id).first_or_404()
        logger.info(f"Retrieved attachment ID {attachment_id} for ticket ID {ticket_id}.")
        return attachment

    @jwt_required()
    def delete(self, ticket_id, attachment_id):
        """Delete a specific attachment"""
        logger = current_app.logger
        attachment = AttachmentModel.query.filter_by(ticket_id=ticket_id, id=attachment_id).first_or_404()

        try:
            if os.path.exists(attachment.filepath):
                os.remove(attachment.filepath)
                logger.info(f"File deleted for attachment ID {attachment_id} and ticket ID {ticket_id}.")
        except Exception as e:
            logger.error(f"Error while deleting file for attachment ID {attachment_id}, ticket ID {ticket_id}: {e}")
            abort(500, message="An error occurred while deleting the file from the system.")

        try:
            db.session.delete(attachment)
            db.session.commit()
            logger.info(f"Attachment record deleted for ID {attachment_id} and ticket ID {ticket_id}.")
        except SQLAlchemyError as e:
            logger.error(f"Error while deleting attachment record: {e}")
            abort(500, message="An error occurred while deleting the attachment from the database.")

        return {"message": "Attachment deleted."}


@blp.route("/ticket/<int:ticket_id>/attachments/<int:attachment_id>/download")
class AttachmentDownload(MethodView):
    @jwt_required()
    def get(self, ticket_id, attachment_id):
        """Download a specific attachment by its ID"""
        logger = current_app.logger
        logger.info(f"Download initiated for attachment ID {attachment_id} and ticket ID {ticket_id}.")

        attachment = AttachmentModel.query.filter_by(ticket_id=ticket_id, id=attachment_id).first_or_404()

        if not os.path.exists(attachment.filepath):
            logger.warning(f"File not found for attachment ID {attachment_id} and ticket ID {ticket_id}.")
            abort(404, message="File not found.")

        mime_type, _ = mimetypes.guess_type(attachment.filepath)

        try:
            response = send_file(attachment.filepath, as_attachment=True)

            response.headers['Content-Type'] = mime_type or 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment.filepath)}"'

            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            logger.info(f"File downloaded successfully for attachment ID {attachment_id} and ticket ID {ticket_id}.")
            return response
        except Exception as e:
            logger.error(f"Error while downloading file for attachment ID {attachment_id}, ticket ID {ticket_id}: {e}")
            abort(500, message=f"An error occurred while downloading the file: {str(e)}")

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from flask_mail import Message
from schemas import MailSchema
from flask import current_app

# Define the Blueprint
blp = Blueprint("Mail", "mail", description="Operations related to sending emails")


@blp.route("/mail/send")
class MailSender(MethodView):
    @jwt_required()
    @blp.arguments(MailSchema)
    def post(self, mail_data):
        """Email specified recipients."""
        logger = current_app.logger
        # Extract email details from the request
        subject = mail_data["subject"]
        recipients = mail_data["recipients"]
        body = mail_data.get("body", "")
        sender = mail_data.get("sender",
                               current_app.config["MAIL_DEFAULT_SENDER"])  # Use default sender if not provided
        try:
            # Use Flask-Mail to send the email
            with current_app.app_context():
                msg = Message(subject=subject, recipients=recipients, body=body, sender=sender)
                current_app.extensions["mail"].send(msg)

            logger.info(f"Email sent successfully to recipients: {recipients}.")
        except Exception as e:
            logger.error(f"Error occurred while sending email: {e}")
            abort(500, message=f"An error occurred while sending the email: {str(e)}")

        return {"message": "Email sent successfully."}, 200

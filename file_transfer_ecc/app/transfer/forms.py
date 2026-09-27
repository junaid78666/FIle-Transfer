"""
app/transfer/forms.py — Transfer WTForms
==========================================
Form for initiating a secure file transfer.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError


class SendFileForm(FlaskForm):
    """
    Form for sending a file to another user.

    Fields:
        file:        The file to transfer (required, validated extension)
        receiver_id: The ID of the recipient user
    """

    file = FileField(
        "Select File",
        validators=[
            FileRequired(message="Please select a file to transfer."),
        ],
        render_kw={
            "id": "send-file-input",
            "accept": (
                ".pdf,.docx,.doc,.xlsx,.xls,.pptx,.ppt,.txt,.csv,.json,.xml,"
                ".png,.jpg,.jpeg,.gif,.bmp,.webp,"
                ".zip,.tar,.gz,.7z,.mp4,.avi,.mkv,.mov,.mp3,.wav,"
                ".py,.js,.html,.css,.md"
            ),
        },
    )

    receiver_id = IntegerField(
        "Recipient",
        validators=[
            DataRequired(message="Please select a recipient."),
            NumberRange(min=1, message="Invalid recipient selected."),
        ],
        render_kw={"id": "send-receiver-id"},
    )

    submit = SubmitField("Send Securely", render_kw={"id": "send-submit"})

    def validate_receiver_id(self, field):
        """Ensure the receiver is a real, active user."""
        from app.models.user import User
        from flask_login import current_user

        user = User.query.filter_by(id=field.data, is_active=True).first()
        if not user:
            raise ValidationError("Selected recipient does not exist.")
        if current_user.is_authenticated and user.id == current_user.id:
            raise ValidationError("You cannot send a file to yourself.")


class DownloadForm(FlaskForm):
    """
    CSRF-protected form for triggering a file download/decrypt operation.
    No additional fields required — transfer_id is in the URL.
    """
    submit = SubmitField("Decrypt & Download", render_kw={"id": "download-submit"})

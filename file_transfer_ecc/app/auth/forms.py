"""
app/auth/forms.py — Authentication WTForms
===========================================
Defines and validates forms for user registration and login.

Forms:
  - RegistrationForm  →  POST /auth/register
  - LoginForm         →  POST /auth/login
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Regexp, ValidationError
)


class RegistrationForm(FlaskForm):
    """
    New user registration form.

    Validates:
      - username: unique, 3–50 characters, alphanumeric + underscores
      - email:    unique, valid email format
      - password: strong password policy
      - confirm_password: must match password
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(
                min=3, max=50,
                message="Username must be between 3 and 50 characters."
            ),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Username may only contain letters, numbers, and underscores."
            ),
        ],
        render_kw={"placeholder": "e.g. alice_smith", "id": "reg-username"},
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address."),
            Length(max=150, message="Email must not exceed 150 characters."),
        ],
        render_kw={"placeholder": "alice@example.com", "id": "reg-email"},
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(
                min=8, max=128,
                message="Password must be at least 8 characters long."
            ),
            Regexp(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&_\-#^])",
                message=(
                    "Password must contain at least one uppercase letter, "
                    "one lowercase letter, one digit, and one special character "
                    "(@$!%*?&_-#^)."
                ),
            ),
        ],
        render_kw={"placeholder": "••••••••", "id": "reg-password"},
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "••••••••", "id": "reg-confirm-password"},
    )

    submit = SubmitField("Create Account", render_kw={"id": "reg-submit"})

    # ── Custom DB-level validators ────────────────────────────
    def validate_username(self, field):
        """Check that the username is not already taken."""
        from app.models.user import User
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError("This username is already taken. Please choose another.")

    def validate_email(self, field):
        """Check that the email is not already registered."""
        from app.models.user import User
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("An account with this email already exists. Please log in.")


class LoginForm(FlaskForm):
    """
    User login form.

    Validates:
      - email:    required, valid format
      - password: required
    """

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address."),
        ],
        render_kw={"placeholder": "alice@example.com", "id": "login-email"},
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
        ],
        render_kw={"placeholder": "••••••••", "id": "login-password"},
    )

    remember_me = BooleanField(
        "Keep me logged in",
        render_kw={"id": "login-remember"},
    )

    submit = SubmitField("Sign In", render_kw={"id": "login-submit"})

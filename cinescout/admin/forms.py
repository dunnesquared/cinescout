# =====================  ADMIN FORMS  =======================
# Code adapted from:
# https://github.com/flask-admin/flask-admin/tree/master/examples/auth-flask-login 
# Many thanks.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Regexp, Length
from cinescout.models import User

# Application context required since package updates in v1.7.4
from cinescout import app

class AdminLoginForm(FlaskForm):
    """Form for admin to login into admin panel with views to database."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


def userlist():
    """Helper functions that builds value-pairs used in the Reset Password form's dropdown list"""
    # Get names from from users' list.
    # Require application context before query since v1.7.4
    with app.app_context():
        usernames = [ user.username for user in User.query.all() ]

    # Build value-label list for dropdown menu.
    valuelabels = [ (name, name) for name in usernames ]
    valuelabels.insert(0, (None, "Select a name"))
    return valuelabels


class AdminResetPasswordForm(FlaskForm):
    """Form to change password of existing user. Useful in case user forgets password."""
    username = SelectField('Username',
                             choices=userlist(),
                             validators=[DataRequired()],
                             validate_choice=True)

    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8,
                                  message="Password must be at least 8 characters long.")])


class AdminAddUserForm(FlaskForm):
    """Form for new users to register with site."""
    
    # Class data
    username = StringField('Username',
                            validators=[DataRequired(),
                                        Regexp('^\w+$',
                                        message="Username must contain only alphanumeric or underscore characters.")
                            ])

    email = EmailField('Email', validators=[ DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired(),
                            EqualTo('password2', message="Passwords do not match."),
                            Length(min=8,
                                  message="Password must be at least 8 characters long.")
                            ])

    password2 = PasswordField('Re-enter Password',
                              validators=[DataRequired()])


    def validate_username(self, username):
        """Checks that username has not already been used.

        Args:
            username: String representing username of user.

        Raises:
            ValidationError: if username already in use.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please use another.')

    def validate_email(self, email):
        """Checks that user is not creating multiple accounts with same
        email.

        Args:
            email: String representing user's email.

        Raises:
            ValidationError: if email already in use.

        """
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('An account already exists with this email address. Please use another.')
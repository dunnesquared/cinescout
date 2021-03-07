"""Implements logic to render and validate web forms for login and user registration."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """Form for new users to log-in to site."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# For disabled RegistrationForm
# ------------------------------
# from wtforms.fields.html5 import EmailField
# from wtforms.validators import  ValidationError, Email, EqualTo, Regexp, Length
# from cinescout.models import User


# Disabled as of v1.1.0
# class RegistrationForm(FlaskForm):
#     """Form for new users to register with site."""
    
#     # Class data
#     username = StringField('Username',
#                             validators=[DataRequired(),
#                                         Regexp('^\w+$',
#                                         message="Username must contain only alphanumeric or underscore characters.")
#                             ])

#     email = EmailField('Email', validators=[ DataRequired(), Email()])

#     password = PasswordField('Password', validators=[DataRequired(),
#                             EqualTo('password2', message="Passwords do not match."),
#                             Length(min=8,
#                                   message="Password must be at least 8 characters long.")
#                             ])

#     password2 = PasswordField('Re-enter Password',
#                               validators=[DataRequired()])

#     submit = SubmitField('Register')


#     def validate_username(self, username):
#         """Checks that username has not already been used.

#         Args:
#             username: String representing username of user.

#         Raises:
#             ValidationError: if username already in use.
#         """
#         user = User.query.filter_by(username=username.data).first()
#         if user:
#             raise ValidationError('Username already taken. Please use another.')

#     def validate_email(self, email):
#         """Checks that user is not creating multiple accounts with same
#         email.

#         Args:
#             email: String representing user's email.

#         Raises:
#             ValidationError: if email already in use.

#         """
#         user = User.query.filter_by(email=email.data).first()

#         if user:
#             raise ValidationError('An account already exists with this email address. Please use another.')
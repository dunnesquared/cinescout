from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from cinescout.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Re-enter Password',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


    def validate_username(self, username):
        """Checks that username has not already been used"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User name already taken. Please use another.')

    def validate_email(self, email):
        """Checks that user is not creating multiple accounts with same
        email."""

        print(f"EMAIL={self.email.data}")

        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('An account already exists with this email address. Please use another.')

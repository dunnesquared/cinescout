from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Regexp, Length
from cinescout.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(),
                                        Regexp('^\w+$',
                                        message="Username must contain only alphanumeric or underscore characters.")
                            ])
    email = EmailField('Email', validators=[ DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired(),
                            EqualTo('password2', message="Passwords do not match."),
                            Length(min=8, message="Password must be at least 8 characters long.")
                            ])
    password2 = PasswordField('Re-enter Password',
                              validators=[DataRequired()])
    submit = SubmitField('Register')


    def validate_username(self, username):
        """Checks that username has not already been used"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please use another.')

    def validate_email(self, email):
        """Checks that user is not creating multiple accounts with same
        email."""

        print(f"EMAIL={self.email.data}")

        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('An account already exists with this email address. Please use another.')

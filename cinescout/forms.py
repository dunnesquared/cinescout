"""Implements logic to render and validate web forms for cinescout features."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Regexp, Length
from cinescout.models import User

class LoginForm(FlaskForm):
    """Form for new users to log-in to site."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
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

    submit = SubmitField('Register')


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


class SearchByTitleForm(FlaskForm):
    """Form to search for movie by title keywords"""
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Search')

# Different departments that people in the movie industry might work in
TMDB_DEPARTMENTS = ["Art", "Acting", "Camera", "Costume & Make-Up", "Crew",
                    "Editing",  "Directing", "Lighting", "Production",
                    "Visual Effects", "Writing"]

def value_label_list():
    """Returns list of tuples with value-label pairs required for selection
    list."""
    tuple_list = [ (department, department) for department in TMDB_DEPARTMENTS ]
    tuple_list.insert(0, ("All", "Search all categories"))
    return tuple_list

class SearchByPersonForm(FlaskForm):
    """Form to search for movie by person's name."""
    name = StringField('Name', validators=[DataRequired()])
    known_for = SelectField('Known For',
                             choices=value_label_list(),
                             validators=[DataRequired()],
                             validate_choice=True)
    submit = SubmitField('Search')


# =====================  ADMIN FORMS  =======================
# Code adapted from:
# https://github.com/flask-admin/flask-admin/tree/master/examples/auth-flask-login 
# Many thanks.

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


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

    # submit = SubmitField('Register')


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
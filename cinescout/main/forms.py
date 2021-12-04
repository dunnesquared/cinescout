"""Implements logic to render and validate web forms for cinescout features."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Regexp, Length
from cinescout.models import User


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


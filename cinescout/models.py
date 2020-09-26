"""Implements database table models via SqlAlchemy ORM."""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from cinescout import db
from cinescout import login_manager


@login_manager.user_loader
def load_user(id):
    """Helps flask_login to get user information from database."""
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """Model that represents users of web app. Passwords hashed."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.username}, {self.email}"


class Film(db.Model):
    """Model that represents films."""

    __tablename__ = "films"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=True)
    director = db.Column(db.String(80), nullable=True)

    def __repr__(self):
        return f"{self.id}, {self.title}, {self.year}, {self.tmdb_id}, {self.director}"


class CriterionFilm(db.Model):
    """Model that represents films from The Criterion Collection."""

    __tablename__ = "criterion_films"
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'), nullable=False)
    
    # Create a backref so foreign keys can show up in flask-admin.
    films = db.relationship('Film', backref=db.backref('CriterionFilm', lazy=True))

    def __repr__(self):
        return f"{self.id}, film_id: {self.film_id}"


class PersonalFilm(db.Model):
    """Model that represents films chosen by app creator. Not used in v0.1."""

    __tablename__ = "personal_films"
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'), nullable=False)

    def __repr__(self):
        return f"{self.id}, film_id: {self.film_id}"


class FilmListItem(db.Model):
    """Model that represents movies on users' personal lists."""

    __tablename__ = "movie_lists"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False) 
    year = db.Column(db.Integer, nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=True)
    date = db.Column(db.String(10), nullable=True)
    original_title = db.Column(db.String(80), nullable=True)

    # Create a backref so foreign keys can show up in flask-admin.
    users = db.relationship('User', backref=db.backref('FilmListItem', lazy=True))

    def __repr__(self):
        return f"{self.id}, user_id: {self.user_id}, title: {self.title}, year: {self.year}, tmdb_id: {self.tmdb_id}, date: {self.date}, original title: {self.original_title}"

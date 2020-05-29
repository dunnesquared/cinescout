from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from cinescout import db
from cinescout import login_manager

@login_manager.user_loader
def load_user(id):
    """Helps flask_login to get user information from database."""
    return User.query.get(int(id))


class User(UserMixin, db.Model):
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




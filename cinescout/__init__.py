"""Defines cinescout directory as package, i.e. a folder that other modules
can import. File executed when package imported."""

print("***Executing __init__.py...***")

# Import PyPi modules.
from flask import Flask
print("Flask successfully imported.")

from config import Config
print("Config successfully imported.")

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
print("SQLAlchemy and Migrate successfully imported.")

from flask_login import LoginManager
print("LoginManager imported.")

from flask_wtf.csrf import CSRFProtect
print("Flask_wtf CSRFProtect imported.")

from flask_admin import Admin
print("Flask_Admin imported.")

from flask_admin.contrib.sqla import ModelView
print("Flask_Admin ModelView imported.")


# Initialize and configure objects.
app = Flask(__name__)
print("app object created.")

app.config.from_object(Config)
print("app configured with Config object.")

db = SQLAlchemy(app)
print("db object created.")

migrate = Migrate(app, db)
print("Migration engine created.")

login_manager = LoginManager()
login_manager.init_app(app)
print("LoginManager object created and initialized.")

csrf = CSRFProtect()
csrf.init_app(app)
print("CSRF object created and applied to app.")

admin = Admin()
admin.init_app(app)
print("FlaskAdmin object created and applied to app.")

# Import application modules.
from cinescout import views
print("cinescout.views imported.")

from cinescout import models
print("cinescout.models imported.")

from cinescout import errors
print("cinescout.errors imported.")

from cinescout import movies
print("cinescout.movies imported.")

# More configuration...
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Film, db.session))
admin.add_view(ModelView(models.CriterionFilm, db.session))
admin.add_view(ModelView(models.PersonalFilm, db.session))
admin.add_view(ModelView(models.FilmListItem, db.session))

print("***End of __init__.py***")

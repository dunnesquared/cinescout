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


# Import application modules.
from cinescout import views
print("cinescout.views imported.")

from cinescout import models
print("cinescout.models imported.")

from cinescout import errors
print("cinescout.errors imported.")

from cinescout import movies
print("cinescout.movies imported.")

# ========== Admin panel configuration ===============
# Code adapted from:
# https://github.com/flask-admin/flask-admin/tree/master/examples/auth-flask-login 
# Many thanks.

print("Setting up admin panel...")

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
print("flask_admin classes imported.")

# Link admin panel with map. 
admin = Admin(app, 'Cinescout: Admin Panel', 
              index_view=views.MyAdminIndexView(),
              base_template="admin/accesscontrol.html")
print("FlaskAdmin object initialized and applied to app.")

# Add which views of database tables you want authenticated supersuser(s) to see.
admin.add_view(views.CinescoutModelView(models.User, db.session))
admin.add_view(views.CinescoutModelView(models.Film, db.session))
admin.add_view(views.CinescoutModelView(models.CriterionFilm, db.session))
admin.add_view(views.CinescoutModelView(models.FilmListItem, db.session))
print("flask_admin database views added.")

print("***End of __init__.py***")
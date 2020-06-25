"""Defines cinescout directory as package, i.e. a folder that other modules
can import. File executed when package imported."""

print("***Executing __init__.py...***")

from flask import Flask
print("Flask successfully imported.")

from config import Config
print("Config successfully imported.")

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
print("SQLAlchemy and Migrate successfully imported.")

from flask_login import LoginManager
print("LoginManager imported.")

app = Flask(__name__)
print("app object created.")

app.config.from_object(Config)
print("app configured with Config object.")

db = SQLAlchemy(app)
print("db object created.")

migrate = Migrate(app, db)
print("Migration engine created")

login_manager = LoginManager()
login_manager.init_app(app)
print("LoginManager object created and initialized.")

from cinescout import views
print("cinescout.views imported.")

from cinescout import models
print("cinescout.models imported.")

from cinescout import errors
print("cinescout.errors imported.")

from cinescout import movies
print("cinescout.movies imported.")

print("***End of __init__.py***")

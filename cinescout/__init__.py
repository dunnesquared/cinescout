"""Defines cinescout directory as package, i.e. can be imnported. 
File executed when package imported."""

print("Executing __init__.py...")

from flask import Flask
print("Flask successfully imported.")

from config import Config
print("Config successfully imported.")

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
print("SQLAlchemy and Migrate successfully imported.")

app = Flask(__name__)
print("app object created.")

app.config.from_object(Config)
print("app configured with Config object.")

db = SQLAlchemy(app)
print("db object created.")

migrate = Migrate(app, db)
print("Migration engine created")

from cinescout import routes
print("routes imported.")

from cinescout import models
print("models imported.")

print("End of __init__.py")

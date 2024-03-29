"""Defines cinescout directory as package, i.e. a folder that other modules
can import. File executed when package imported."""

print("*** Executing __init__.py... ***")

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

# Rate limit access to resources, especially public APIs. 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(app, key_func=get_remote_address, retry_after=30)
print("Limiter object created. Retry allowed from remote address after 30 seconds.")

# Register Blueprint packages.
from cinescout.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from cinescout.auth import bp as auth_bp
app.register_blueprint(auth_bp)

# from cinescout.admin import bp as admin_bp
# app.register_blueprint(admin_bp)

from cinescout.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from cinescout.main import bp as main_bp
app.register_blueprint(main_bp)

print("Blueprints registered.")

# Import models. This will create the schema of your database via SqlAlchemy magic!
from cinescout import models
print("cinescout.models imported.")


# ========================= Admin panel configuration ==============================
# Code adapted from:
# https://github.com/flask-admin/flask-admin/tree/master/examples/auth-flask-login 
# Many thanks.

# print("Setting up admin panel...")

# from flask_admin import Admin, AdminIndexView
# from flask_admin.contrib.sqla import ModelView
# print("flask_admin classes imported.")

# from cinescout import admin

# # Link admin panel with map. 
# x_admin = Admin(app, 'Cinescout: Admin Panel', 
#               index_view=admin.routes.MyAdminIndexView(),
#               base_template="admin/accesscontrol.html")
# print("FlaskAdmin object initialized and applied to app.")

# # Add which views of database tables you want authenticated supersuser(s) to see.
# x_admin.add_view(admin.routes.CinescoutModelView(models.User, db.session))
# x_admin.add_view(admin.routes.CinescoutModelView(models.Film, db.session))
# x_admin.add_view(admin.routes.CinescoutModelView(models.CriterionFilm, db.session))
# x_admin.add_view(admin.routes.CinescoutModelView(models.FilmListItem, db.session))
# print("flask_admin database views added.")

print("***End of __init__.py***")

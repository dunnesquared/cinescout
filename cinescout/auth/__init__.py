from flask import Blueprint

bp = Blueprint('auth', __name__)

from cinescout.auth import routes
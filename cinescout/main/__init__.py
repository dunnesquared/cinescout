from flask import Blueprint

bp = Blueprint("main", __name__)

from cinescout.main import routes
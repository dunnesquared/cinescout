from flask import Blueprint

bp = Blueprint('errors', __name__)

from cinescout.errors import handlers
from flask import Blueprint

bp = Blueprint('api', __name__)

from cinescout.api import criterion, usermovielist, nytreview
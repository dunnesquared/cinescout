from flask import Blueprint

# Can't call admin because Blueprint has this name reserved??
bp = Blueprint('superuser', __name__)

from cinescout.admin import routes
from flask import Blueprint

module = Blueprint('api', __name__)

from . import routes

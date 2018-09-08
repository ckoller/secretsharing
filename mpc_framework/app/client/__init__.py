from flask import Blueprint

module = Blueprint('client', __name__)

from . import routes

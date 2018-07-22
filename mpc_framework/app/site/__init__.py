from flask import Blueprint

module = Blueprint('site', __name__)

from . import routes

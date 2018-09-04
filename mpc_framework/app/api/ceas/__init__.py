from flask import Blueprint

module = Blueprint('api/ceas/', __name__)

from app.api.ceas import routes

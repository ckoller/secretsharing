from flask import Blueprint

module = Blueprint('api/ceps/', __name__)

from app.api.ceps import routes

from flask import Blueprint

module = Blueprint('api/preprocessor.py/', __name__)

from app.api.ceps_speed import routes
from flask import Blueprint

module = Blueprint('api/ceps_speed.py/', __name__)

from app.api.ceps_speed import routes
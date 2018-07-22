from flask import Flask
from celery import Celery
import argparse
import config

celery = Celery(__name__)
celery.config_from_object('jobs.celeryconfig')

def create_app():
    app = Flask(__name__)
    from .api import module as api_blueprint
    from .site import module as site_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(site_blueprint)
    return app

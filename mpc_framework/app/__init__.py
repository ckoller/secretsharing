from flask import Flask
from celery import Celery

celery = Celery(__name__)
celery.config_from_object('jobs.celeryconfig')

def create_app():
    app = Flask(__name__)
    from .api.ceas import module as api_ceas_blueprint
    from .api.ceps import module as api_ceps_blueprint

    from .site import module as site_blueprint
    app.register_blueprint(api_ceas_blueprint, url_prefix='/api/ceas')
    app.register_blueprint(api_ceps_blueprint, url_prefix='/api/ceps')

    app.register_blueprint(site_blueprint)
    return app

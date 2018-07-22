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
    setup()
    return app

def setup():
    host, port, id, player_count = get_host_info()
    players = create_player_dict(host, port, player_count)
    config.CONFIG_VALUES['players'] = players
    config.CONFIG_VALUES['host'] = host
    config.CONFIG_VALUES['port'] = port
    config.CONFIG_VALUES['id'] = id

def get_host_info():
    parser = argparse.ArgumentParser(description='P2P multiparty computation app')
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--player_id')
    parser.add_argument('--player_count')
    args = parser.parse_args()
    return args.host, args.port, args.player_id, args.player_count

def create_player_dict(ip, my_port, player_count):
    players = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1) if 5000 + x != int(my_port)}
    return players

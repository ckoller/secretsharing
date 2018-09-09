from app import create_app
import argparse
import config
from app.api.ceps.ceps import Ceps
from app.client.routes import Client


def setup():
    host, port, id, player_count = get_host_info()
    players = create_player_dict(host, port, player_count)
    config.players = players
    config.host = host
    config.port = port
    config.id = id
    config.player_count = int(player_count)
    config.protocol = Ceps(Client().create_circuit())

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

if __name__ == '__main__':
    setup()
    host = config.host
    port = config.port
    app = create_app()
    app.run(debug=True, host=host, port=port)



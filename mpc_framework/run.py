from app import create_app
import argparse, requests
import config, prod_config
from app.api.ceps.ceps import Ceps
from app.api.ceps_speed.ceps_speed import Ceps_Speed

from app.client.routes import Client


class Prod:
    def setup(self):
        player_count, my_player_id, players, all = self.create_player_dict()
        config.players = players
        config.host = "0.0.0.0"
        config.port = "80"
        config.id = my_player_id
        config.player_count = player_count
        config.all_players = all
        config.protocol = Ceps(Client().create_circuit())

    def create_player_dict(self):
        my_ip = requests.get('https://ipapi.co/ip/').text
        player_list = prod_config.players_prod
        player_count = len(player_list)
        my_player_id = player_list.index(my_ip) + 1
        players = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x] != my_ip}
        all = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x]}
        return player_count, my_player_id, players, all

class Test:

    def setup(self):
        host, port, id, _ = self.get_host_info()
        player_count, players, all = self.create_player_dict(id)
        config.players = players
        config.host = host
        config.port = port
        config.id = id
        config.player_count = int(player_count)
        config.all_players = all
        config.protocol = Ceps(Client().create_circuit())

    def get_host_info(self):
        parser = argparse.ArgumentParser(description='P2P multiparty computation app')
        parser.add_argument('--host')
        parser.add_argument('--port')
        parser.add_argument('--player_id')
        parser.add_argument('--player_count')
        args = parser.parse_args()
        return args.host, args.port, args.player_id, args.player_count

    def create_player_dict(self, id):
        player_list = prod_config.players_test
        my_ip = player_list[int(id) - 1]
        player_count = len(player_list)
        players = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x] != my_ip}
        all = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x]}
        return player_count, players, all


class Dev:
    def setup(self):
        host, port, id, player_count = self.get_host_info()
        players, all = self.create_player_dict(host, port, player_count)
        config.players = players
        config.host = host
        config.port = port
        config.id = id
        config.player_count = int(player_count)
        config.all_players = all
        config.protocol = Ceps(Client().create_circuit())

    def get_host_info(self):
        parser = argparse.ArgumentParser(description='P2P multiparty computation app')
        parser.add_argument('--host')
        parser.add_argument('--port')
        parser.add_argument('--player_id')
        parser.add_argument('--player_count')
        args = parser.parse_args()
        return args.host, args.port, args.player_id, args.player_count

    def create_player_dict(self, ip, my_port, player_count):
        players = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1) if 5000 + x != int(my_port)}
        all = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1)}
        return players, all

def print_config():
    print(config.players)
    print(config.all_players)
    print(config.host)
    print(config.port)
    print(config.id)
    print(config.player_count)

if __name__ == '__main__':
    s = Prod()
    s.setup()
    print_config()


    host = config.host
    port = config.port
    app = create_app()
    app.run(debug=True, host=host, port=port)
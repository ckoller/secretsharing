from app import create_app
import argparse, urllib

import config, prod_config
from app.api.ceps.ceps import Ceps
from app.api.ceps_speed.ceps_speed import Ceps_Speed

from app.client.routes import Client


class SetupProd:
    def setup(self):
        players, all = self.create_player_dict()
        config.players = players
        config.host = "0.0.0.0"
        config.port = None
        config.id = "5"
        config.player_count = 5
        config.all_players = all
        config.protocol = Ceps(Client().create_circuit())

    def create_player_dict(self):
        player_list = prod_config.players
        players = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x] != "ec2-18-222-238-248.us-east-2.compute.amazonaws.com"}
        all = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x]}
        return players, all

class SetupDevProd: # spin up 4
    def setup(self):
        host, port, id, player_count = self.get_host_info()
        players, all = self.create_player_dict(host, port, player_count)
        config.players = players
        config.host = host
        config.port = port
        config.id = id
        config.player_count = int(5)
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
        players[5] = "ec2-18-222-238-248.us-east-2.compute.amazonaws.com"
        all[5] = "ec2-18-222-238-248.us-east-2.compute.amazonaws.com"
        return players, all


class SetupDev:
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

if __name__ == '__main__':
    s = SetupProd()
    s.setup()
    host = config.host
    port = config.port
    app = create_app()
    app.run(debug=True, host=host, port=port)
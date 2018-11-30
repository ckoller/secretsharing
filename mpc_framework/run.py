from app import create_app
import argparse, requests
import player_config, config
from tests.setup import TestSetupLocalShell
from app.api.ceps.ceps import Ceps
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.ceps_speed.strategies.sharing import BooleanLayerSharingStrategyByPlayerId
from app.api.ceps_speed.strategies.evaluation import BooleanLayerEvaluationStrategy
from app.api.ceps.strategies.sharing import ShareByWirePlayerId
from tests.routes import Client
from tests.arithmeticCircuits.arithmetic_circuits import ArithmeticCircuits

class Prod:
    def setup(self):
        player_count, my_player_id, players, all = self.create_player_dict()
        config.players = players
        config.host = "0.0.0.0"
        config.port = "80"
        config.id = my_player_id
        config.player_count = player_count
        config.all_players = all
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        config.ceps_speed = Ceps_Speed(circuit=circuit,
                                       sharingStrategy=BooleanLayerSharingStrategyByPlayerId(),
                                       evaluationStrategy=BooleanLayerEvaluationStrategy(Client()))
        config.ceps = Ceps(circuit=Client().create_circuit(0), sharingStrategy=ShareByWirePlayerId())

    def create_player_dict(self):
        my_ip = requests.get('https://ipapi.co/ip/').text
        player_list = player_config.players_prod
        player_count = len(player_list)
        my_player_id = player_list.index(my_ip) + 1
        players = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x] != my_ip}
        all = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x]}
        return player_count, my_player_id, players, all

class Emulate_Prod:

    def setup(self):
        host, port, id, _ = self.get_host_info()
        player_count, players, all = self.create_player_dict(id)
        config.players = players
        config.host = host
        config.port = port
        config.id = id
        config.player_count = int(player_count)
        config.all_players = all
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        config.ceps_speed = Ceps_Speed(circuit=circuit,
                                       sharingStrategy=BooleanLayerSharingStrategyByPlayerId(),
                                       evaluationStrategy=BooleanLayerEvaluationStrategy(Client()))
        config.ceps = Ceps(circuit=Client().create_circuit(0), sharingStrategy=ShareByWirePlayerId())


    def get_host_info(self):
        parser = argparse.ArgumentParser(description='P2P multiparty computation app')
        parser.add_argument('--host')
        parser.add_argument('--port')
        parser.add_argument('--player_id')
        parser.add_argument('--player_count')
        args = parser.parse_args()
        return args.host, args.port, args.player_id, args.player_count

    def create_player_dict(self, id):
        player_list = player_config.players_test
        my_ip = player_list[int(id) - 1]
        player_count = len(player_list)
        players = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x] != my_ip}
        all = {x + 1: player_list[x] for x in range(0, len(player_list)) if player_list[x]}
        return player_count, players, all

class Server:
    def __init__(self, setup):
        setup = setup
        setup.setup()
        self.host = config.host
        self.port = config.port
        self.app = create_app()

    def start(self, result_arr):
        config.result = result_arr
        self.app.run(debug=True, host=self.host, port=self.port, use_reloader=False)

    def print_config(self):
        print(config.players)
        print(config.all_players)
        print(config.host)
        print(config.port)
        print(config.id)
        print(config.player_count)

if __name__ == '__main__':
    setup = Prod()
    setup.setup()
    print(config.players)
    print(config.all_players)
    print(config.host)
    print(config.port)
    print(config.id)
    print(config.player_count)
    host = config.host
    port = config.port
    app = create_app()
    app.run(debug=True, host=host, port=port)

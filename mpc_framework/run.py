from app import create_app
import argparse, requests
import config, prod_config
from app.api.ceps.ceps import Ceps
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.strategies.sharing import ArithmeticSharingStrategy, BooleanSharingStrategy, BooleanLayerSharingStrategy
from app.api.strategies.evaluation import ArithmeticEvaluationStrategy, BooleanEvaluationStrategy, BooleanLayerEvaluationStrategy
from app.tests.routes import Client
from app.tests.arithmeticCircuits.arithmetic_circuits import ArithmeticCircuits



class Prod:
    def setup(self):
        player_count, my_player_id, players, all = self.create_player_dict()
        config.players = players
        config.host = "0.0.0.0"
        config.port = "80"
        config.id = my_player_id
        config.player_count = player_count
        config.all_players = all

    def create_player_dict(self):
        my_ip = requests.get('https://ipapi.co/ip/').text
        player_list = prod_config.players_prod
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


class TestSetup:

    def __init__(self, host, port, id, player_count):
        self.host = host
        self.port = port
        self.id = id
        self.player_count = player_count

    def setup(self):
        players, all = self.create_player_dict(self.host, self.port, self.player_count)
        config.players = players
        config.host = self.host
        config.port = self.port
        config.id = self.id
        config.player_count = int(self.player_count)
        config.all_players = all

    def create_player_dict(self, ip, my_port, player_count):
        players = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1) if 5000 + x != int(my_port)}
        all = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1)}
        return players, all


class Dev:
    def setup(self):
        host, port, id, player_count, type = self.get_host_info()
        players, all = self.create_player_dict(host, port, player_count)
        config.players = players
        config.host = host
        config.port = port
        config.id = id
        config.player_count = int(player_count)
        config.all_players = all
        if type == "arit":
            self.arithmetic_circuit_setup()
        elif type == "bool":
            self.boolean_circuit_setup()
        elif type == "bool_layer":
            self.boolean_circuit_layer_setup()



    def get_host_info(self):
        parser = argparse.ArgumentParser(description='P2P multiparty computation app')
        parser.add_argument('--host')
        parser.add_argument('--port')
        parser.add_argument('--player_id')
        parser.add_argument('--player_count')
        parser.add_argument('--type')
        args = parser.parse_args()
        return args.host, args.port, args.player_id, args.player_count, args.type

    def create_player_dict(self, ip, my_port, player_count):
        players = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1) if 5000 + x != int(my_port)}
        all = {x: ip + ":" + str(5000 + x) for x in range(1, int(player_count) + 1)}
        return players, all

    def arithmetic_circuit_setup(self):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        # choose strategies
        sharingStrategy = ArithmeticSharingStrategy()
        evaluationStrategy = ArithmeticEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0))

    def boolean_circuit_setup(self):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        # choose strategies
        sharingStrategy = BooleanSharingStrategy()
        evaluationStrategy = BooleanEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0))

    def boolean_circuit_layer_setup(self):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        # choose strategies
        sharingStrategy = BooleanLayerSharingStrategy()
        evaluationStrategy = BooleanLayerEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0))


class Server:
    def __init__(self, setup):
        setup = setup
        setup.setup()
        self.host = config.host
        self.port = config.port
        self.app = create_app()

    def start(self, result_arr):
        print("***************** starting ******************")
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
    setup = Dev()
    setup.setup()
    config.ceps = Ceps(Client().create_circuit(0))
    host = config.host
    port = config.port
    app = create_app()
    app.run(debug=True, host=host, port=port)

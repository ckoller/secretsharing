import config, argparse
from app.api.ceps.ceps import Ceps
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.ceps_speed.strategies.sharing import ArithmeticSharingStrategy, BooleanSharingStrategy, BooleanLayerSharingStrategy, BooleanLayerSharingStrategyByPlayerId
from app.api.ceps_speed.strategies.evaluation import ArithmeticEvaluationStrategy, BooleanEvaluationStrategy, BooleanLayerEvaluationStrategy
from app.api.ceps.strategies.sharing import ShareByWireId, ShareByWirePlayerId
from tests.routes import Client
from tests.arithmeticCircuits.arithmetic_circuits import ArithmeticCircuits

class TestSetupLocalProcess:

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


class TestSetupLocalShell:
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
        elif type == "bool_player_id":
            self.boolean_bool_player_id_setup()

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
        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())

    def boolean_circuit_setup(self):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        # choose strategies
        sharingStrategy = BooleanSharingStrategy()
        evaluationStrategy = BooleanEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())

    def boolean_circuit_layer_setup(self):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        # choose strategies
        sharingStrategy = BooleanLayerSharingStrategy()
        evaluationStrategy = BooleanLayerEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())

    def boolean_bool_player_id_setup(self):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        # choose strategies
        sharingStrategy = BooleanLayerSharingStrategyByPlayerId()
        evaluationStrategy = BooleanLayerEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)

        config.ceps = Ceps(Client().create_circuit(0), ShareByWirePlayerId())
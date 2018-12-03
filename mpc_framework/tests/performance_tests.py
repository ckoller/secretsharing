from unittest import TestCase
from tests.setup import TestSetupLocalProcess
from run import Server
import requests, subprocess, config, json
from time import sleep
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.ceps.ceps import Ceps
from app.api.ceps.strategies.sharing import ShareByWirePlayerId
from app.api.ceps_speed.strategies.sharing import BooleanLayerSharingStrategyByPlayerId
from app.api.ceps_speed.strategies.evaluation import BooleanEvaluationStrategy, BooleanLayerEvaluationStrategy
from tests.routes import Client
from multiprocessing import Process, Manager
from tests.circuit import BooleanCircuitReader, BooleanCircuitCreator

class TestCepsSpeedBoolLayer(TestCase):
    def test_create_circuit(self):
        c = BooleanCircuitCreator()
        #c.and_gate(c.and_gate(c.and_gate(c.and_gate(c.and_gate(c.and_gate(c.and_gate(c.and_gate(c.and_gate(c.and_gate(
        #,c.input(1)),c.input(1)),c.input(1)),c.input(1)),c.input(1)),c.input(1)),c.input(1)),c.input(1)),c.input(1)),c.input(1))


class TestCepsBoolLayer(TestCase):

    def setUp(self):
        self.result_arr = None
        self.process = None

    def tearDown(self):
        # kill all gnome-shell instances
        subprocess.call(['./kill.sh'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        # stop the thread containing the server we test on
        self.process.terminate()

    def test_and_00(self):
        player_count = 3
        protocol_type = "bool_player_id"
        circuit_type = "bool"
        protocol_name = 'ceps'
        circuit_id = 10
        input = [0]*20
        circuit_input = json.dumps(input)

        self.start_test_server(player_count)
        start_parties_in_gnome_shells(2, player_count, protocol_type)

        setup_protocol(protocol_name, player_count, circuit_type, circuit_id, circuit_input)
        start_protocol(protocol_name, player_count)

    def start_test_server(self, player_count):
        # choose circuit for the party that we test on
        c = BooleanCircuitReader()
        c.init_parsed_circuit("single_and.txt")
        circuit = c.get_circuit()

        # read config parameters
        test_setup = TestSetupLocalProcess(host='127.0.0.1', port='5001', id='1', player_count=player_count)

        # create shares memory (a list) between test tread and server tread for getting the result of the computaiton.
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()

        # choose strategies and start the server
        s = Server(setup=test_setup)
        client = Client()
        sharingStrategy = BooleanLayerSharingStrategyByPlayerId()
        evaluationStrategy = BooleanEvaluationStrategy(client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0), ShareByWirePlayerId())


        # start the server in a thread
        self.process = Process(target=s.start, args=[self.result_arr])
        self.process.start()

class TestCepsSpeedBoolLayer(TestCase):

    def setUp(self):
        self.result_arr = None
        self.process = None

    def tearDown(self):
        # kill all gnome-shell instances
        subprocess.call(['./kill.sh'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        # stop the thread containing the server we test on
        self.process.terminate()

    def test_and_0_0(self):
        player_count = 3
        protocol_type = "bool_player_id"
        protocol_name = 'ceps_speed'
        circuit_type = 'bool'
        circuit_id = 80
        circuit_input = json.dumps([0, 0]*80)

        self.start_test_server(player_count)
        start_parties_in_gnome_shells(player_count-1, player_count, protocol_type)
        setup_protocol(protocol_name, player_count, circuit_type, circuit_id, circuit_input)
        start_protocol(protocol_name, player_count)


    def start_test_server(self, player_count):
        # choose circuit for the party that we test on
        c = BooleanCircuitReader()
        c.init_parsed_circuit("single_and.txt")
        circuit = c.get_circuit()
        # read config parameters
        test_setup = TestSetupLocalProcess(host='127.0.0.1', port='5001', id='1', player_count=player_count)

        # create shares memory (a list) between test tread and server tread for getting the result of the computaiton.
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()

        # choose strategies and start the server
        s = Server(setup=test_setup)
        client = Client()
        sharingStrategy = BooleanLayerSharingStrategyByPlayerId()
        evaluationStrategy = BooleanLayerEvaluationStrategy(client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0), ShareByWirePlayerId())

        # start the server in a thread
        self.process = Process(target=s.start, args=[self.result_arr])
        self.process.start()

def start_protocol(protocol_name, number_of_players):
    for x in range(5001, 5001+number_of_players):
        url = "http://127.0.0.1:" + str(x) + "/"+ protocol_name + "/run/"
        r = requests.get(url)
    sleep(2)

def setup_protocol(protocol_name, number_of_players, circuit_type, circuit_id, circuit_input):
    for x in range(5001, 5001 + number_of_players):
            server_name = "http://127.0.0.1:" + str(x)
            params = "/"+ protocol_name + "/setup/" + circuit_type + "/" + str(circuit_id) + "/" + circuit_input
            url = server_name + params
            r = requests.get(url)
    sleep(2)

def start_parties_in_gnome_shells(parties, number_of_players, protocol_type):
    directory = "/home/koller/Projects/secretsharing/mpc_framework/"
    command = ['./test_run.sh', str(parties), str(number_of_players), protocol_type]
    subprocess.call(command, cwd=directory)
    sleep(2)
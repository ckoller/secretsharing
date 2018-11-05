from unittest import TestCase
from run import Server, TestSetup
import requests, subprocess, config, json
from time import sleep
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.strategies.sharing import ArithmeticSharingStrategy
from app.api.strategies.evaluation import ArithmeticEvaluationStrategy
from app.tests.arithmeticCircuits.arithmetic_circuits import ArithmeticCircuits
from app.tests.routes import Client
from multiprocessing import Process, Array, Manager



class TestCepsSpeedArit(TestCase):

    def setUp(self):
        self.result_arr = None
        self.process = None


    def tearDown(self):
        # kill all gnome-shell instances
        subprocess.call(['./kill.sh'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        # stop the thread containing the server we test on
        self.process.terminate()

    def test_add_mult_3players(self):
        # start the server we want to test on
        self.start_test_server(player_count=3)

        # start 2 parties in gnome-shells
        self.start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="arit")

        # choose protocol and input for players
        input = json.dumps([8,8])
        self.setup_ceps_speed(number_of_players=3, circuit_id=1, circuit_input=input)

        # start protocols
        self.start_ceps_speed(number_of_players=3)

        # 8 + 8 * 8 = 72
        self.assertListEqual(list(self.result_arr), [72])

    def test_mult_add_5_people_where_one_person_has_multiple_inputs(self):
        number_of_players = 6
        circuit_id = 2
        input = json.dumps([8, 8, 8])

        # start the server we want to test on
        self.start_test_server(number_of_players)

        # start 2 parties in gnome-shells
        parties = number_of_players -1
        self.start_parties_in_gnome_shells(parties=parties, number_of_players=number_of_players, protocol_type="arit")

        # choose protocol and input for players
        self.setup_ceps_speed(number_of_players, circuit_id, circuit_input=input)

        # start protocols
        self.start_ceps_speed(number_of_players)

        # 8*8+(8+8+8)*8) = 256
        self.assertListEqual(list(self.result_arr), [256])


    def test_add_mult_scalarmult_where_some_player_has_no_input(self):
        number_of_players = 9
        circuit_id = 3
        input = json.dumps([4])

        # start the server we want to test on
        self.start_test_server(number_of_players)

        # start 2 parties in gnome-shells
        parties = number_of_players -1
        self.start_parties_in_gnome_shells(parties=parties, number_of_players=number_of_players, protocol_type="arit")

        # choose protocol and input for players
        self.setup_ceps_speed(number_of_players, circuit_id, circuit_input=input)

        # start protocols
        self.start_ceps_speed(number_of_players)

        # (4*4 + 4*4)*2) = 64
        self.assertListEqual(list(self.result_arr), [64])


    def test_add_mult_scalarmult_with_multiple_outputs(self):
        number_of_players = 4
        circuit_id = 4
        input = json.dumps([8,8,8,8,8,8])

        # start the server we want to test on
        self.start_test_server(number_of_players)

        # start 2 parties in gnome-shells
        parties = number_of_players -1
        self.start_parties_in_gnome_shells(parties=parties, number_of_players=number_of_players, protocol_type="arit")

        # choose protocol and input for players
        self.setup_ceps_speed(number_of_players, circuit_id, circuit_input=input)

        # start protocols
        self.start_ceps_speed(number_of_players)

        # (8*8 + 8*8)*2) * 8  = 2048
        # (8*8 + 8*8)*2) * 8  = 2048
        self.assertListEqual(list(self.result_arr), [2048, 2048])

    def start_test_server(self, player_count):
        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()

        # read config parameters
        test_setup = TestSetup(host='127.0.0.1', port='5001', id='1', player_count=player_count)

        # create shares memory (a list) between test tread and server tread for getting the result of the computaiton.
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()

        # choose strategies and start the server
        s = Server(setup=test_setup)
        client = Client()
        sharingStrategy = ArithmeticSharingStrategy()
        evaluationStrategy = ArithmeticEvaluationStrategy(client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)

        # start the server in a thread
        self.process = Process(target=s.start, args=[self.result_arr])
        self.process.start()

    def start_ceps_speed(self, number_of_players):
        for x in range(5001, 5001+number_of_players):
            url = "http://127.0.0.1:" + str(x) + "/ceps_speed/run/"
            r = requests.get(url)
        sleep(2)

    def setup_ceps_speed(self, number_of_players, circuit_id, circuit_input):
        for x in range(5001, 5001 + number_of_players):
            url = "http://127.0.0.1:" + str(x) + "/ceps_speed/setup/" + str(circuit_id) + "/" + circuit_input
            r = requests.get(url)
        sleep(2)

    def start_parties_in_gnome_shells(self, parties, number_of_players, protocol_type):
        directory = "/home/koller/Projects/secretsharing/mpc_framework/"
        command = ['./test_run.sh', str(parties), str(number_of_players), protocol_type]
        subprocess.call(command, cwd=directory)
        sleep(2)


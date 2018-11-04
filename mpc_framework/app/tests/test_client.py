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



class TestApplication(TestCase):

    def setUp(self):

        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()

        # read config parameters
        test_setup = TestSetup(host='127.0.0.1', port='5003', id='3', player_count=3)

        # choose strategies and start the server
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()
        s = Server(setup=test_setup)
        self.client = Client()
        sharingStrategy = ArithmeticSharingStrategy()
        evaluationStrategy = ArithmeticEvaluationStrategy(self.client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)

        # start the server in a thread
        self.process = Process(target=s.start, args=(circuit, sharingStrategy, evaluationStrategy, self.result_arr))
        self.process.start()

    def tearDown(self):
        # kill all gnome-shell instances
        #subprocess.call(['./kill.sh'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        # stop the thread containing the server we test on
        self.process.terminate()

    def test_create_circuit(self):
        # start 2 parties in gnome-shells
        subprocess.call(['./test_run.sh', '2', '3', 'arit'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        sleep(2)

        # choose protocol and input for players
        circuit_id = '1'
        circuit_input = json.dumps([8])
        for x in range(5001, 5004):
            url = "http://127.0.0.1:" + str(x) + "/ceps_speed/setup/" + circuit_id + "/"  + circuit_input
            r = requests.get(url)
        sleep(2)

        # start protocols
        for x in range(5001, 5004):
            url = "http://127.0.0.1:" + str(x) + "/ceps_speed/run/"
            r = requests.get(url)
        sleep(5)
        # 8 + 8 * 8 = 72
        print("foo", self.result_arr)

        self.assertListEqual(list(self.result_arr), [72])

from unittest import TestCase
from run import Server, TestSetup
import requests, subprocess, config
from time import sleep
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.strategies.sharing import ArithmeticSharingStrategy
from app.api.strategies.evaluation import ArithmeticEvaluationStrategy
from app.client.ArithmeticCircuits.arithmetic_circuits import ArithmeticCircuits
from app.client.routes import Client
from multiprocessing import Process


class TestApplication(TestCase):

    def setUp(self):

        # choose circuit for the party that we test on
        circuit = ArithmeticCircuits().add_1_mult_2_3()
        circuit_input = [8 for x in range(128)]

        # read config parameters
        test_setup = TestSetup(host='127.0.0.1', port='5003', id='3', player_count=3)

        # choose strategies and start the server

        s = Server(setup=test_setup)
        sharingStrategy = ArithmeticSharingStrategy(circuit_input)
        evaluationStrategy = ArithmeticEvaluationStrategy(Client())
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)

        # start the server in a thread
        self.process = Process(target=s.start, args=())
        self.process.start()

    def tearDown(self):
        # kill all gnome-shell instances
        subprocess.call(['./kill.sh'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        # stop the thread containing the server we test on
        self.process.terminate()

    def test_create_circuit(self):
        # start 2 parties in gnome-shells
        subprocess.call(['./test_run.sh', '2', '3', 'arit'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")


        sleep(2)
        for x in range(5001, 5004):
            url = "http://127.0.0.1:" + str(x) + "/ceps_speed"
            print(url)
            r = requests.get(url)

        sleep(2)

        self.assertEqual(1,1)

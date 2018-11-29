from unittest import TestCase
from run import Server, TestSetup
import requests, subprocess, config, json
from time import sleep
from app.api.ceps_speed.ceps_speed import Ceps_Speed
from app.api.ceps.ceps import Ceps
from app.api.ceps_speed.strategies.sharing import ArithmeticSharingStrategy, BooleanSharingStrategy, BooleanLayerSharingStrategy
from app.api.ceps_speed.strategies.evaluation import ArithmeticEvaluationStrategy, BooleanEvaluationStrategy, BooleanLayerEvaluationStrategy
from app.tests.arithmeticCircuits.arithmetic_circuits import ArithmeticCircuits
from app.api.ceps.strategies.sharing import ShareByWireId
from app.tests.routes import Client
from multiprocessing import Process, Manager
from app.tests.circuit import BooleanCircuitReader
from Crypto.Cipher import AES

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
        number_of_players = 3
        self.start_test_server(number_of_players)

        # start 2 parties in gnome-shells
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="arit")

        # choose protocol and input for players
        input = json.dumps([8,8])
        setup_protocol('ceps_speed', number_of_players, circuit_type='arit', circuit_id=1, circuit_input=input)

        # start protocols
        start_protocol('ceps_speed', number_of_players)

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
        start_parties_in_gnome_shells(parties=parties, number_of_players=number_of_players, protocol_type="arit")

        # choose protocol and input for players
        setup_protocol('ceps_speed', number_of_players, circuit_type='arit', circuit_id=circuit_id, circuit_input=input)

        # start protocols
        start_protocol('ceps_speed', number_of_players)

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
        start_parties_in_gnome_shells(parties=parties, number_of_players=number_of_players, protocol_type="arit")

        # choose protocol and input for players
        setup_protocol('ceps_speed', number_of_players, circuit_type='arit', circuit_id=circuit_id, circuit_input=input)

        # start protocols
        start_protocol('ceps_speed', number_of_players)

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
        start_parties_in_gnome_shells(parties=parties, number_of_players=number_of_players, protocol_type="arit")

        # choose protocol and input for players
        setup_protocol('ceps_speed', number_of_players, circuit_type='arit', circuit_id=circuit_id, circuit_input=input)

        # start protocols
        start_protocol('ceps_speed', number_of_players)

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
        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())

        # start the server in a thread
        self.process = Process(target=s.start, args=[self.result_arr])
        self.process.start()

class TestCepsSpeedBool(TestCase):

    def setUp(self):
        self.result_arr = None
        self.process = None

    def tearDown(self):
        # kill all gnome-shell instances
        subprocess.call(['./kill.sh'], cwd="/home/koller/Projects/secretsharing/mpc_framework/")
        # stop the thread containing the server we test on
        self.process.terminate()

    def test_add_0_0(self):
        number_of_players = 3
        # start the server we want to test on
        self.start_test_server(player_count=3)

        # start 2 parties in gnome-shells
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")

        # choose protocol and input for players
        input = json.dumps([0,0])
        # choose protocol and input for players
        setup_protocol('ceps_speed', number_of_players, circuit_type='bool', circuit_id=1, circuit_input=input)

        # start protocols
        start_protocol('ceps_speed', number_of_players)

        self.assertListEqual(list(self.result_arr), [0])

    def test_add_0_1(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([0,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=1, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0])

    def test_add_1_0(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,0])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=1, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0])

    def test_add_1_1(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=1, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [1])

    def test_xor_0_0(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([0,0])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=2, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0])

    def test_xor_0_1(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([0,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=2, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [1])

    def test_xor_1_0(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,0])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=2, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [1])

    def test_xor_1_1(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=2, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0])

    def test_single_not_0(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([0])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=3, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [1])

    def test_single_not_1(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=3, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0])

    def test_3_single_and_11_11_11(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,1,1,1,1,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=4, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [1,1,1])

    def test_3_single_and_11_10_01(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,1,1,0,0,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=4, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [1,0,0])

    def test_3_single_xor_11_11_11(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,1,1,1,1,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=5, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0,0,0])

    def test_3_single_xor_11_10_01(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        input = json.dumps([1,1,1,0,0,1])
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=5, circuit_input=input)
        start_protocol('ceps_speed', 3)
        self.assertListEqual(list(self.result_arr), [0,1,1])

    def test_mixed_input_xor_and_000(self):
        input = json.dumps([0,0,0])
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=6, circuit_input=input)
        start_protocol('ceps_speed', 3)
        # (a xor b) and c
        self.assertListEqual(list(self.result_arr), [0])

    def test_mixed_input_xor_and_101(self):
        input = json.dumps([1, 0, 1])
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=6, circuit_input=input)
        start_protocol('ceps_speed', 3)
        # (a xor b) and c
        self.assertListEqual(list(self.result_arr), [1])

    def test_mixed_input_xor_and_011(self):
        input = json.dumps([1, 0, 1])
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=6, circuit_input=input)
        start_protocol('ceps_speed', 3)
        # (a xor b) and c
        self.assertListEqual(list(self.result_arr), [1])

    def test_mixed_input_xor_and_111(self):
        input = json.dumps([1, 1, 1])
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol('ceps_speed', 3, circuit_type='bool', circuit_id=6, circuit_input=input)
        start_protocol('ceps_speed', 3)
        # (a xor b) and c
        self.assertListEqual(list(self.result_arr), [0])

    def start_test_server(self, player_count):
        # choose circuit for the party that we test on
        c = BooleanCircuitReader()
        c.init_parsed_circuit("single_and.txt")
        circuit = c.get_circuit()
        # read config parameters
        test_setup = TestSetup(host='127.0.0.1', port='5001', id='1', player_count=player_count)

        # create shares memory (a list) between test tread and server tread for getting the result of the computaiton.
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()

        # choose strategies and start the server
        s = Server(setup=test_setup)
        client = Client()
        sharingStrategy = BooleanSharingStrategy()
        evaluationStrategy = BooleanEvaluationStrategy(client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())

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
        number_of_players = 3
        # start the server we want to test on
        self.start_test_server(player_count=3)

        # start 2 parties in gnome-shells
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool_layer")

        # choose protocol and input for players
        input = json.dumps([0,0])
        # choose protocol and input for players
        setup_protocol('ceps_speed', number_of_players, circuit_type='bool', circuit_id=1, circuit_input=input)

        # start protocols
        start_protocol('ceps_speed', number_of_players)

        self.assertListEqual(list(self.result_arr), [0])

    def test_adder_0_plus_1(self):
        n1 = [0 for x in range(32)]
        n2 = [0 for x in range(32)]
        n3 = [0 for x in range(33)]
        n1[0] = 0
        n2[0] = 1
        n3[0] = 1
        input = json.dumps(n1 + n2)

        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool_layer")
        setup_protocol(protocol_name='ceps_speed', number_of_players=3, circuit_type='bool', circuit_id=7, circuit_input=input)
        start_protocol(protocol_name='ceps_speed', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def test_adder_10_plus_1(self):
        n1 = [0 for x in range(32)]
        n2 = [0 for x in range(32)]
        n3 = [0 for x in range(33)]
        n1[0] = 1
        n2[1] = 1
        n3[0] = 1
        n3[1] = 1
        input = json.dumps(n1 + n2)
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool_layer")
        setup_protocol(protocol_name='ceps_speed', number_of_players=3, circuit_type='bool', circuit_id=7, circuit_input=input)
        start_protocol(protocol_name='ceps_speed', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def test_adder_1010101010_plus_1000110(self):
        n1_val = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        n2_val = [1, 0, 0, 0, 1, 1, 0]
        res = [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0]
        n1_val.reverse()
        n2_val.reverse()
        res.reverse()
        n1 = n1_val + [0 for x in range(22)]
        n2 = n2_val + [0 for x in range(25)]
        n3 = res + [0 for x in range(22)]
        input = json.dumps(n1 + n2)
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool_layer")
        setup_protocol(protocol_name='ceps_speed', number_of_players=3, circuit_type='bool', circuit_id=7, circuit_input=input)
        start_protocol(protocol_name='ceps_speed', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def AES(self):
        n1 = [0 for x in range(128)]
        ascii_0 = [0, 0, 1, 1, 0, 0, 0, 0]
        n2 = ascii_0 * 16
        n2 = [0 for x in range(128)]
        input = json.dumps(n1 + n2)
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool_layer")
        setup_protocol(protocol_name='ceps_speed', number_of_players=3, circuit_type='bool', circuit_id=7, circuit_input=input)
        start_protocol(protocol_name='ceps_speed', number_of_players=3)
        self.assertListEqual(list(self.result_arr), "")
        # self.assertListEqual(list(self.result_arr), n3)

    def start_test_server(self, player_count):
        # choose circuit for the party that we test on
        c = BooleanCircuitReader()
        c.init_parsed_circuit("single_and.txt")
        circuit = c.get_circuit()
        # read config parameters
        test_setup = TestSetup(host='127.0.0.1', port='5001', id='1', player_count=player_count)

        # create shares memory (a list) between test tread and server tread for getting the result of the computaiton.
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()

        # choose strategies and start the server
        s = Server(setup=test_setup)
        client = Client()
        sharingStrategy = BooleanLayerSharingStrategy()
        evaluationStrategy = BooleanLayerEvaluationStrategy(client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)
        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())

        # start the server in a thread
        self.process = Process(target=s.start, args=[self.result_arr])
        self.process.start()

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
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")

        input = json.dumps([0,0])
        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=1, circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        self.assertListEqual(list(self.result_arr), [0])

    def test_and_11(self):
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")

        input = json.dumps([1,1])
        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=1, circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        self.assertListEqual(list(self.result_arr), [1])

    def test_adder_0_plus_0(self):

        n1 = [0 for x in range(32)]
        n2 = [0 for x in range(32)]
        n3 = [0 for x in range(33)]
        input = json.dumps(n1+n2)

        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")

        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=7, circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def test_adder_0_plus_1(self):
        n1 = [0 for x in range(32)]
        n2 = [0 for x in range(32)]
        n3 = [0 for x in range(33)]
        n1[0] = 0
        n2[0] = 1
        n3[0] = 1
        input = json.dumps(n1 + n2)

        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=7,
                       circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def test_adder_10_plus_1(self):
        n1 = [0 for x in range(32)]
        n2 = [0 for x in range(32)]
        n3 = [0 for x in range(33)]
        n1[0] = 1
        n2[1] = 1
        n3[0] = 1
        n3[1] = 1
        input = json.dumps(n1 + n2)

        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=7,
                       circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def test_adder_1010101010_plus_1000110(self):
        n1_val = [1,0,1,0,1,0,1,0,1,0]
        n2_val = [1,0,0,0,1,1,0]
        res = [0,1,0,1,1,1,1,0,0,0,0]
        n1_val.reverse()
        n2_val.reverse()
        res.reverse()
        n1 = n1_val + [0 for x in range(22)]
        n2 = n2_val + [0 for x in range(25)]
        n3 = res + [0 for x in range(22)]
        input = json.dumps(n1 + n2)
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=7, circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        self.assertListEqual(list(self.result_arr), n3)

    def test_AES(self):
        n1 = [0 for x in range(128)]
        ascii_0 = [0,0,1,1,0,0,0,0]
        n2 = ascii_0 * 16
        n2 = [0 for x in range(128)]
        input = json.dumps(n1 + n2)
        self.start_test_server(player_count=3)
        start_parties_in_gnome_shells(parties=2, number_of_players=3, protocol_type="bool")
        setup_protocol(protocol_name='ceps', number_of_players=3, circuit_type='bool', circuit_id=8,
                       circuit_input=input)
        start_protocol(protocol_name='ceps', number_of_players=3)
        #self.assertListEqual(list(self.result_arr), n3)

    def crypto_aes(self):
        plaintext = b'0000000000000000'
        key = b'0000000000000000'
        IV = b'0000000000000000'

        obj = AES.new(key, AES.MODE_CBC, IV)
        ciphertext = obj.encrypt(plaintext)
        print(ciphertext)
        print(list(ciphertext))
        print("aes", [int.to_bytes(ciphertext, byteorder='big')])
        print("aes", [int.to_bytes(ciphertext, byteorder='little')])
        print("aes", [int.to_bytes(ciphertext, byteorder='big', signed=True)])
        print("aes", [int.to_bytes(ciphertext, byteorder='big', signed=False )])

        print("{0:b}".format(20))
        print("{0:b}".format(125))




    def start_test_server(self, player_count):
        # choose circuit for the party that we test on
        c = BooleanCircuitReader()
        c.init_parsed_circuit("single_and.txt")
        circuit = c.get_circuit()

        # read config parameters
        test_setup = TestSetup(host='127.0.0.1', port='5001', id='1', player_count=player_count)

        # create shares memory (a list) between test tread and server tread for getting the result of the computaiton.
        multiprocessing_manager = Manager()
        self.result_arr = multiprocessing_manager.list()

        # choose strategies and start the server
        s = Server(setup=test_setup)
        client = Client()
        sharingStrategy = BooleanSharingStrategy()
        evaluationStrategy = BooleanEvaluationStrategy(client)
        config.ceps_speed = Ceps_Speed(circuit, sharingStrategy, evaluationStrategy)

        config.ceps = Ceps(Client().create_circuit(0), ShareByWireId())


        # start the server in a thread
        self.process = Process(target=s.start, args=[self.result_arr])
        self.process.start()

def print_circuit(circuit):
    for gate in circuit:
        print("id", gate.id)
        print("type", gate.type)
        print("wires_in", gate.wires_in)
        print("wires_out", gate.wires_out)
        print("shares", gate.shares)
        print("output_value", gate.output_value)
        print("a", gate.a)
        print("b", gate.b)
        print("c", gate.c)
        print("r", gate.r)
        print("r_open", gate.r_open)
    print("\n\n")

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
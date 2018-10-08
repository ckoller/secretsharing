from unittest import TestCase
from run import Server, TestSetup, Client
import os, requests
from threading import Thread
from time import sleep


class TestApplication(TestCase):
    def test_create_circuit(self):
        c1 = Client()
        c2 = Client()
        c3 = Client()

        path = file = os.getcwd() + "/booleanCircuits/adder_32bit.txt"
        circuit1 = c1.create_circuit(0, path)
        circuit2 = c2.create_circuit(0, path)
        circuit3 = c3.create_circuit(0, path)

        test_setup1 = TestSetup(host='127.0.0.1', port='5001', id='1', player_count=3)
        test_setup2 = TestSetup(host='127.0.0.1', port='5002', id='2', player_count=3)
        test_setup3 = TestSetup(host='127.0.0.1', port='5003', id='3', player_count=3)
        print("got this far")
        s1 = Server(test_setup1, circuit1)

        t1 = Thread(target=s1.start())
        print("got thisss far")


        print("got this far")
        requests.get("http://127.0.0.1:5001/ceps")
        requests.get("http://127.0.0.1:5002/ceps")
        requests.get("http://127.0.0.1:5003/ceps")

        self.assertEqual(1,1)

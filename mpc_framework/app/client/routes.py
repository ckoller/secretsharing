from . import module
import config, json, requests
from app.api.ceps.ceps import Ceps
from app.circuit import CircuitCreator


@module.route('/')
def home():
    config.protocol.run(my_value=8)
    return "Welcome"

class Client:
    def create_circuit(self):
        c = CircuitCreator()
        #c.mult(c.add(c.input(1),c.input(2)), c.input(3))
        #c.add(c.mult(c.input(1),c.input(2)), c.input(3))
        #c.add(c.mult(c.input(1),c.input(2)), c.add(c.input(3), c.input(4)))

        c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4)))
        return c.circuit

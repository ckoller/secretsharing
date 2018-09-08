from . import module
import config, json, requests
from app.api.ceps.ceps import Ceps, CircuitCreator

@module.route('/')
def home():
    config.protocol.run(my_value=5)
    return "Welcome"

class Client:
    def create_circuit(self):
        c = CircuitCreator()
        c.add(c.input(1),c.add(c.input(2),c.input(3)))
        return c.circuit

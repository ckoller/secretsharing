from . import module
import config
from app.client.circuit import CircuitCreator
from app.api.polynomials import Polynomials

@module.route('/<protocol>')
def home(protocol):
    if protocol == "ceps":
        config.ceps.run(my_value=8)
    if protocol == "ceps_speed":
        if config.id == '5':
            config.ceps_speed.run(my_value=Polynomials().mult_invers(8))
        else:
            config.ceps_speed.run(my_value=8)
    return "Welcome"


@module.route('/<protocol>/<int:circuit_id>')
def setup_new_circuit(protocol, circuit_id):
    c = Client()
    circuit = c.create_circuit(circuit_id)
    if protocol == "ceps":
        config.ceps.set_new_circuit(circuit)
    if protocol == "ceps_speed":
        config.ceps_speed.set_new_circuit(circuit)
    return "Welcome"

class Client:
    def create_circuit(self, id):
        c = CircuitCreator()
        if id == 0:
            c.mult(c.add(c.input(1),c.input(2)), c.input(3))                               # 8*(8+8)   =   128     n=3
        elif id == 1:
            c.add(c.mult(c.input(1),c.input(2)), c.input(3))                               # 8*8+8     =   72      n=3
        elif id == 2:
            c.add(c.mult(c.input(1),c.input(2)), c.add(c.input(3), c.input(4)))            # 8*8+8+8   =   80      n=4
        elif id == 3:
            c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4)))           # 8*8 + 8*8 =   128     n=4

        elif id == 4:
            c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2)                     # (8*8 + 8*8)*2)/2  = 256
        else:
            c.mult(c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(5))   # (8*8 + 8*8)*2)*8  = 2048
        circuit = c.get_circuit()
        #c.print_circuit_v2(circuit[0])
        return circuit




    def get_response(self, result, circuit):
        CircuitCreator().print_circuit_v2(circuit)
        print("client got result", result)



    #TODO multiple protocols
    #TODO multiple input per player
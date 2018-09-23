from . import module
import config
from app.client.circuit import CircuitCreator
from app.api.polynomials import Polynomials

@module.route('/')
def home():
    if config.id == '5':
        config.protocol.run(my_value=Polynomials().mult_invers(8))
    else:
        config.protocol.run(my_value=8)

    return "Welcome"

class Client:

    def create_circuit(self):
        c = CircuitCreator()
        #c.mult(c.add(c.input(1),c.input(2)), c.input(3))                               # 8*(8+8)   =   128     n=3
        #c.add(c.mult(c.input(1),c.input(2)), c.input(3))                               # 8*8+8     =   72      n=3
        #c.add(c.mult(c.input(1),c.input(2)), c.add(c.input(3), c.input(4)))            # 8*8+8+8   =   80      n=4
        c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4)))           # 8*8 + 8*8 =   128     n=4
        #c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2)                     # (8*8 + 8*8)*2)/2  = 256
        #c.mult(c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(5))   # (8*8 + 8*8)*2)*8  = 2048
        circuit = c.get_circuit()
        return circuit


    def get_response(self, result, circuit):
        print("client got result", result)
        CircuitCreator().print_circuit_v2(circuit)




    #TODO multiple protocols
    #TODO multiple input per player
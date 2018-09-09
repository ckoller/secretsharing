from . import module
import config
from app.circuit import CircuitCreator
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
        #c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4)))           # 8*8 + 8*8 =   128     n=4
        #c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2)                     # (8*8 + 8*8)*2)/2  = 256

        c.mult(c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(5))   # (8*8 + 8*8)*2)*8  = 2048

        return c.circuit

    def get_response(self, response):
        print("client got this", response)

    #TODO run mulitple protocols in one run and check if they calculate correct
    #TODO circuit return on create
    #TODO output list saved in last notes shares
    #TODO return the circuit with all info
    #TODO 3-n multiplicaton circuit
    #TODO multiple protocols
    #TODO Test multiple protocols
from . import module
import config
from app.client.circuit import ArithmeticCircuit, BooleanCircuit

@module.route('/<protocol>')
def home(protocol):
    if protocol == "ceps":
        config_aes()
    if protocol == "ceps_speed":
        #config.ceps_speed.run(my_value=Polynomials().mult_invers(8))

        config.ceps_speed.run(my_values=[8,8,8,8,8])
    return "Welcome"

def config_adder():
    n1_val = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    n2_val = [1, 0, 0, 0, 1, 1, 0]
    res = [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0]
    n1_val.reverse()
    n2_val.reverse()
    res.reverse()
    n1 = n1_val + [0 for x in range(22)]
    n2 = n2_val + [0 for x in range(25)]
    n3 = res + [0 for x in range(22)]
    input = n1 + n2
    config.ceps.run(input)

def config_aes():
    n1 = [0 for x in range(128)]
    n2 = [0 for x in range(128)]
    config.ceps.run(n1+n2)


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
        c = ArithmeticCircuit()
        if id == 0:
            #(c.mult(c.input(1), c.input(1)))  # 8*8+8     =   72      n=3
            c = BooleanCircuit()
            c.init_parsed_circuit()
            return c.get_circuit()

        elif id == 1:
            c.add(c.mult(c.input(1),c.input(2)), c.input(3))                               # 8*8+8     =   72      n=3
        elif id == 2:
            c.add(c.mult(c.input(5),c.input(3)), c.mult(c.add(c.add(c.input(3), c.input(5)), c.input(1)), c.input(1)))          # 8*8+8+8   =   80      n=3
        elif id == 3:
            c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4)))           # 8*8 + 8*8 =   128     n=4
        elif id == 4:
            c.scalar_mult(c.add(c.mult(c.input(7),c.input(1)), c.mult(c.input(8), c.input(4))), scalar=2)                       # (8*8 + 8*8)*2)/2  = 256
        else:
            c.mult(c.scalar_mult(c.add(c.mult(c.input(2),c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(1))   # (8*8 + 8*8)*2)*8  = 2048'
            c.output()
            c.mult(c.scalar_mult(c.add(c.mult(c.input(2), c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(1))
        circuit = c.get_circuit()
        #c.print_circuit_v2(circuit[0])
        return circuit

    def get_response(self, result, circuit, mv):
        ArithmeticCircuit().print_circuit(circuit)
        #print("n1", mv[:32])
        #print("n2", mv[32:])
        print("res", result)
        #print("len", len(result))
        #res = [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0]
        #res.reverse()
        #n3 = res + [0 for x in range(22)]
        #print("exp", n3)



    # TODO multiple outputs
    # TODO read boolean circuit from file
    # TODO evaluate boolean circuit by emulation
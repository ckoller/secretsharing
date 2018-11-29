from . import module
import config, json
from app.tests.circuit import ArithmeticCircuitCreator, BooleanCircuitReader
from app.tests.arithmeticCircuits.arithmetic_circuits import ArithmeticCircuits

# these routes are made to the purpose of testing the correctness of the protocols.
# the should not be a part of the API, if you wish use this app in production

@module.route('/<protocol>/setup/<circuit_type>/<int:circuit_id>/<input_values>')
def setup(protocol, circuit_type, circuit_id, input_values):
    my_input_values = json.loads(input_values)
    if circuit_type == "bool":
        circuit = get_bool_circuit(circuit_id)
    elif circuit_type == "arit":
        circuit = get_arit_circuit(circuit_id)

    if protocol == "ceps_speed":
        # config.ceps_speed.run(my_value=Polynomials().mult_invers(8))
        config.ceps_speed.setup(circuit, my_input_values)
    if protocol == "ceps":
        config.ceps.setup(circuit, my_input_values)
    return "Welcome"

@module.route('/<protocol>/run/')
def run(protocol):
    if protocol == "ceps_speed":
        config.ceps_speed.run()
    elif protocol == "ceps":
        config.ceps.run()
    return "Welcome"

def get_bool_circuit(circuit_id):
    c = BooleanCircuitReader()
    if circuit_id == 1:
        c.init_parsed_circuit("single_and.txt")
    elif circuit_id == 2:
        c.init_parsed_circuit("single_xor.txt")
    elif circuit_id == 3:
        c.init_parsed_circuit("single_not.txt")
    elif circuit_id == 4:
        c.init_parsed_circuit("3_single_and.txt")
    elif circuit_id == 5:
        c.init_parsed_circuit("3_single_xor.txt")
    elif circuit_id == 6:
        c.init_parsed_circuit("mixed_input_xor_and.txt")
    elif circuit_id == 7:
        c.init_parsed_circuit("adder_32bit_with_layer.txt")
    elif circuit_id == 8:
        c.init_parsed_circuit("AES.txt")
    elif circuit_id == 10:
        c.init_parsed_circuit("10_and")
    elif circuit_id == 20:
        c.init_parsed_circuit("20_and")
    elif circuit_id == 30:
        c.init_parsed_circuit("30_and")
    elif circuit_id == 40:
        c.init_parsed_circuit("40_and")
    elif circuit_id == 50:
        c.init_parsed_circuit("50_and")
    elif circuit_id == 60:
        c.init_parsed_circuit("60_and")
    elif circuit_id == 80:
        c.init_parsed_circuit("80_and")
    circuit = c.get_circuit()
    return circuit

def get_arit_circuit(circuit_id):
    if circuit_id == 1:
        return ArithmeticCircuits().add_1_mult_2_3()
    elif circuit_id == 2:
        return ArithmeticCircuits().mult_add_5_people_where_one_person_has_multiple_inputs()
    elif circuit_id == 3:
        return ArithmeticCircuits().add_mult_scalarmult_where_some_player_has_no_input()
    elif circuit_id == 4:
        return ArithmeticCircuits().add_mult_scalarmult_with_multiple_outputs()




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

class Client:
    def __init__(self):
        self.result = []

    def create_circuit(self, id):
        c = ArithmeticCircuitCreator()
        if id == 0:
            #(c.mult(c.input(1), c.input(1)))  # 8*8+8     =   72      n=3
            c = BooleanCircuitReader()
            c.init_parsed_circuit("AES.txt")
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
        self.result = result
        self.print_circuit(circuit)
        print("res", self.result)

    def print_circuit(self, circuit):
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

            print("")
        print("\n\n")
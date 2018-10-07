import config

class Gate:
    def __init__(self, id, type, wires_in):
        self.id = id
        self.type = type
        self.wires_in = wires_in
        self.wires_out = []
        self.output_value = None
        self.shares = [None] * config.player_count
        self.scalar = 1
        self.a = None
        self.b = None
        self.c = None
        self.r = None
        self.r_open = None

class CircuitCreator:
    def __init__(self):
        self.circuit = []
        self.gate_id = 0
        self.m_gates = []
        self.o_gates = []
        self.i_gates = []

    def create_circuit(self):
        # 1*2 + 3*4 * 4
        self.scalar_mult(self.add(self.mult(self.input(1), self.input(2)), self.mult(self.input(3), self.input(4))), 4)

    def get_circuit(self):
        self.output()
        return [self.circuit, self.i_gates, self.m_gates, self.o_gates]

    def output(self):
        gate = Gate(id=self.gate_id, type="output", wires_in=[self.gate_id - 1])
        self.o_gates.append(gate)
        self.circuit.insert(self.gate_id, gate)
        self.gate_id = self.gate_id + 1


    def input(self, player_id):
        gate = Gate(id=self.gate_id, type="input", wires_in=[player_id])
        self.circuit.insert(self.gate_id, gate)
        self.i_gates.append(gate)
        self.gate_id = self.gate_id + 1
        return self.gate_id - 1;

    def add(self, gid_in_l, gid_in_r):
        gate = Gate(id=self.gate_id, type="add", wires_in=[gid_in_l, gid_in_r])
        self.update_input_gate(gid_in_l)
        self.update_input_gate(gid_in_r)
        self.update_circuit(gate)
        return self.gate_id - 1;

    def scalar_mult(self, gid_in, scalar):
        gate = Gate(id=self.gate_id, type="scalar_mult", wires_in=[gid_in])
        gate.scalar = scalar
        self.update_input_gate(gid_in)
        self.update_circuit(gate)
        return self.gate_id - 1;

    def mult(self, gid_in_l, gid_in_r):
        gate = Gate(id=self.gate_id, type="mult", wires_in=[gid_in_l, gid_in_r])
        self.m_gates.append(self.gate_id)
        self.update_input_gate(gid_in_l)
        self.update_input_gate(gid_in_r)
        self.update_circuit(gate)
        return self.gate_id - 1;

    def div(self, gid_in_l, gid_in_r):
        gate = Gate(id=self.gate_id, type="div", wires_in=[gid_in_l, gid_in_r])
        self.update_input_gate(gid_in_l)
        self.update_input_gate(gid_in_r)
        self.update_circuit(gate)
        self.gate_id = self.gate_id + 1
        return self.gate_id - 1;

    def update_input_gate(self, gid_in):
        g_in = self.circuit[gid_in]
        g_in.wires_out.append(self.gate_id)

    def update_circuit(self, gate):
        self.circuit.insert(self.gate_id, gate)
        self.gate_id = self.gate_id + 1

    def print_gate(self, gate):
        print("id", gate.id)
        print("type", gate.type)
        print("wires_in", gate.wires_in)
        print("wires_out", gate.wires_out)
        print("output_value", gate.output_value)
        print("scalar", gate.scalar)
        print("")

    def print_circuit(self, circuit):
        for gate in circuit:
            print("id", gate.id)
            print("type", gate.type)
            print("wires_in", gate.wires_in)
            print("wires_out", gate.wires_out)
            print("shares", gate.shares)
            print("output_value", gate.output_value)
            print("scalar", gate.scalar)
            print("")
        print("\n\n")

    def print_circuit_v2(self, circuit):
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

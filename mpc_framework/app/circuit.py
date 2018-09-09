
class Gate:
    def __init__(self, id, type, wires_in):
        self.id = id
        self.type = type
        self.wires_in = wires_in
        self.wires_out = []
        self.output_value = None
        self.shares = []
        self.scalar = 1

class CircuitCreator:
    def __init__(self):
        self.circuit = []
        self.gate_id = 0

    def create_circuit(self):
        # 1*2 + 3*4 * 4
        self.scalar_mult(self.add(self.mult(self.input(1), self.input(2)), self.mult(self.input(3), self.input(4))), 4)

    def get_circuit(self):
        gate = Gate(id=self.gate_id, type="output", wires_in=[self.gate_id - 1])
        self.circuit.insert(self.gate_id, gate)
        return self.circuit

    def input(self, player_id):
        gate = Gate(id=self.gate_id, type="input", wires_in=[player_id])
        self.circuit.insert(self.gate_id, gate)
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

from app.api.polynomials import Polynomials
import config, json, requests


class Ceps:
    def __init__(self, circuit):
        self.circuit = circuit
        self.cur_gid = 0
        self.output_shares = []
        self.pol = Polynomials()

    def run(self, my_value):
        self.share_my_intput_value(my_value)

    def share_my_intput_value(self, my_value):
        n = config.player_count
        for gate in self.circuit:
            if gate.type == 'input' and gate.wires_in[0] == int(config.id):
                poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
                print("my_poly", poly)
                print("my_shares", shares)
                for player_id, player in config.players.items():
                    url = "http://" + player + "/api/ceps/share/"
                    data = {"share": json.dumps(shares[player_id - 1]),
                            "gate_id": json.dumps(gate.id)}
                    r = requests.post(url, data)
                gate.output_value = shares[int(config.id) - 1]
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def share_my_mult_value(self, my_value, gate):
        n = config.player_count
        poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/mult_share/"
            data = {"share": json.dumps(shares[player_id - 1]),
                    "gate_id": json.dumps(gate.id)}
            requests.post(url, data)
        gate.shares.append(shares[int(config.id) - 1])
        if self.received_all_mult_shares(gate):
            result = self.reconstruct(gate.shares)[1]
            gate.output_value = result
            self.cur_gid = self.cur_gid + 1
            self.evaluate_circuit()

    def share_my_output_value(self, my_value):
        n = config.player_count
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/output_share/"
            data = {"share": json.dumps(my_value)}
            requests.post(url, data)
        if self.received_all_output_shares():
            result = self.reconstruct(self.output_shares)[1]
            self.protocol_done(result)

    def handle_input_share(self, share, gate_id):
        gate = self.circuit[gate_id]
        gate.output_value = share
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def handle_mult_share(self, share, gate_id):
        gate = self.circuit[gate_id]
        gate.shares.append(share)
        if self.received_all_mult_shares(gate):
            result = self.reconstruct(gate.shares)[1]
            gate.output_value = result
            self.cur_gid = self.cur_gid + 1
            self.evaluate_circuit()

    def handle_output_share(self, share):
        self.output_shares.append(share)
        if self.received_all_output_shares():
            result = self.reconstruct(self.output_shares)[1]
            self.protocol_done(result)

    def protocol_done(self, result):
        print("Result", result)
        print("output shares", self.output_shares)

    def received_all_input_shares(self):
        for gate in self.circuit:
            if gate.type == 'input' and gate.output_value == None:
                return False
        return True

    def received_all_mult_shares(self, gate):
        return len(gate.shares) == config.player_count

    def received_all_output_shares(self):
        return len(self.output_shares) == config.player_count

    def evaluate_circuit(self):
        for gate_id in range(self.cur_gid, len(self.circuit)):
            gate = self.circuit[gate_id]
            if gate.type == 'input':
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'add':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                gate.output_value = val_in_l + val_in_r
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'scalar_mult':
                val_in = self.circuit[gate.wires_in[0]].output_value
                scalar = gate.scalar
                gate.output_value = val_in * scalar
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'mult':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                prod = val_in_l * val_in_r
                self.share_my_mult_value(prod, gate)
                break
            elif gate.type == 'div':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                mult_invers = self.pol.extended_gcd(5, prime)[0]
                gate.output_value = val_in_l * mult_invers
                self.share_my_mult_value(prod, gate)
                break
            if False:
                print("id", gate.id)
                print("type", gate.type)
                print("wires_in", gate.wires_in)
                print("wires_out", gate.wires_out)
                print("output_value", gate.output_value)
                print("scalar", gate.scalar)
                print("")

        if self.cur_gid == len(self.circuit):
            gate = self.circuit[self.cur_gid-1]
            self.cur_gid = self.cur_gid + 1
            result =  gate.output_value
            self.output_shares.append(result)
            self.share_my_output_value(result)





    def reconstruct(self, shares):
        rec = self.pol.lagrange_interpolate(shares)
        return rec


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

    def eval_circuit(self):
        for gate in self.circuit:
            if gate.type == 'add':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                gate.output_value = val_in_l + val_in_r
            elif gate.type == 'scalar_mult':
                val_in = self.circuit[gate.wires_in[0]].output_value
                scalar = gate.scalar
                gate.output_value = val_in * scalar
            elif gate.type == 'mult':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                gate.output_value = val_in_l * val_in_r
            elif gate.type == 'div':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                gate.output_value = val_in_l / val_in_r
            if True:
                print("id", gate.id)
                print("type", gate.type)
                print("wires_in", gate.wires_in)
                print("wires_out", gate.wires_out)
                print("output_value", gate.output_value)
                print("scalar", gate.scalar)
                print("")
        last_gate = self.circuit[len(self.circuit)-1]
        return last_gate.output_value

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
            print("output_value", gate.output_value)
            print("scalar", gate.scalar)
            print("")
        print("\n\n")

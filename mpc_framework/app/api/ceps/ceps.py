from app.api.polynomials import Polynomials
import config, json, requests
from app.client.routes import Client

class Ceps:
    def __init__(self, circuit):
        self.circuit = circuit["circuit"]
        self.output_gate_count = len(circuit["output_gates"])
        self.input_gates = circuit["input_gates"]
        self.circuit_type = circuit["type"]
        self.cur_gid = 0
        self.pol = Polynomials()
        self.output = []
        self.mv = []

    def run(self, my_values):
        self.mv = my_values
        self.share_my_input_value(my_values)

    def set_new_circuit(self, circuit):
        self.circuit = circuit[0]
        self.cur_gid = 0

    def share_my_input_value(self, my_values):
        n = config.player_count
        value_count = 0
        for gate in self.circuit:
            if gate.type == 'input':
                poly, shares = None, None
                if self.circuit_type == "arit" and gate.wires_in[0] == int(config.id):
                    my_value = my_values[value_count]
                    poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
                    value_count = value_count + 1
                    for player_id, player in config.players.items():
                        url = "http://" + player + "/api/ceps/share/"
                        data = {"share": json.dumps(shares[player_id - 1]),
                                "gate_id": json.dumps(gate.id),
                                "sender_id": json.dumps(config.id)}
                        requests.post(url, data)
                    gate.output_value = shares[int(config.id) - 1]
                elif self.circuit_type == "bool" and config.id == '1':
                    my_value = my_values[gate.wires_in[0]]
                    poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
                    print("poly", poly)
                    print("shares", shares)
                    for player_id, player in config.players.items():
                        url = "http://" + player + "/api/ceps/share/"
                        data = {"share": json.dumps(shares[player_id - 1]),
                                "gate_id": json.dumps(gate.id),
                                "sender_id": json.dumps(config.id)}
                        requests.post(url, data)
                    gate.output_value = shares[int(config.id) - 1]

        if self.received_all_input_shares():
            self.evaluate_circuit()

    def share_input_values(self, my_values):
        for gate in self.circuit:
            if gate.type == 'input' and gate.wires_in[0] == int(config.id):
                my_value = my_values[value_count]
                poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
                value_count = value_count + 1
                print("my_poly", poly)
                print("my_shares", shares)
                for player_id, player in config.players.items():
                    url = "http://" + player + "/api/ceps/share/"
                    data = {"share": json.dumps(shares[player_id - 1]),
                            "gate_id": json.dumps(gate.id),
                            "sender_id": json.dumps(config.id)}
                    requests.post(url, data)
                gate.output_value = shares[int(config.id) - 1]
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def share_my_mult_value(self, my_value, gate):
        n = config.player_count
        poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/mult_share/"
            data = {"share": json.dumps(shares[player_id - 1]),
                    "gate_id": json.dumps(gate.id),
                    "sender_id": json.dumps(config.id)}
            requests.post(url, data)
        id = int(config.id)
        gate.shares[id - 1] = shares[id - 1]
        if self.received_all_mult_shares(gate):
            result = self.reconstruct(gate.shares)[1]
            gate.output_value = result
            if gate.type != "xor":
                self.cur_gid = self.cur_gid + 1
            self.evaluate_circuit()

    def share_my_output_value(self, my_value, output_gate):
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/output_share/"
            data = {"share": json.dumps(my_value),
                    "gate_id": json.dumps(output_gate.id),
                    "sender_id": json.dumps(config.id)}
            requests.post(url, data)
        if self.received_all_output_shares(output_gate):
            result = self.reconstruct(output_gate.shares)[1]
            self.output.append((output_gate.id, result))
            if len(self.output) == self.output_gate_count:
                print("******************", "output gate_count", self.output_gate_count, len(self.output), "******************")
                self.output.sort()
                results = [ self.output[i][1] for i in range(len( self.output))]
                self.protocol_done(results)
            else:
                output_gate.output_value = result
                self.cur_gid = self.cur_gid + 1
                self.evaluate_circuit()


    def handle_input_share(self, share, gate_id):
        gate = self.circuit[gate_id]
        gate.output_value = share
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def handle_mult_share(self, share, gate_id, sender_id):
        gate = self.circuit[gate_id]
        gate.shares[sender_id - 1] = share
        if self.received_all_mult_shares(gate):
            result = self.reconstruct(gate.shares)[1]
            gate.output_value = result
            if gate.type != "xor":
                self.cur_gid = self.cur_gid + 1
            self.evaluate_circuit()

    def handle_output_share(self, share, gate_id, sender_id):
        output_gate = self.circuit[gate_id]
        output_gate.shares[sender_id - 1] = share
        if self.received_all_output_shares(output_gate):
            result = self.reconstruct(output_gate.shares)[1]
            self.output.append((output_gate.id, result))
            if len(self.output) == self.output_gate_count:
                print("******************", "output gate_count", self.output_gate_count, len(self.output), "******************")
                self.output.sort()
                results = [ self.output[i][1] for i in range(len( self.output))]
                self.protocol_done(results)
            else:
                output_gate.output_value = result
                self.cur_gid = self.cur_gid + 1
                self.evaluate_circuit()

    def protocol_done(self, result):
        Client().get_response(result, self.circuit, self.mv)

    def received_all_input_shares(self):
        for gate in self.circuit:
            if gate.type == 'input' and gate.output_value == None:
                return False
        return True

    def received_all_mult_shares(self, gate):
        return None not in gate.shares

    def received_all_output_shares(self, gate):
        return None not in gate.shares

    def evaluate_circuit(self):
        for gate_id in range(self.cur_gid, len(self.circuit)):
            gate = self.circuit[gate_id]
            #print("******************", "in eval", gate_id, gate.type, "******************")

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
            elif gate.type == 'inv':
                val_in = self.circuit[gate.wires_in[0]].output_value
                gate.output_value = 1 - val_in
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'mult' or gate.type == 'and':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                if val_in_l is None:
                    print("l", gate.wires_in[0], self.circuit[gate.wires_in[0]].type)
                    break
                elif val_in_r is None:
                    print("r", gate.wires_in[1], self.circuit[gate.wires_in[1]].type)
                prod = val_in_l * val_in_r
                self.share_my_mult_value(prod, gate)
                break
            elif gate.type == 'xor':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                if gate.output_value is None:
                    prod = val_in_l * val_in_r
                    self.share_my_mult_value(prod, gate)
                    break
                else:
                    result = (val_in_l + val_in_r) - 2*(gate.output_value)
                    gate.output_value = result
                    self.cur_gid = self.cur_gid + 1
            elif gate.type == 'output':
                prev_gate = self.circuit[self.cur_gid - 1]
                gate.output_value = prev_gate.output_value
                result = gate.output_value
                gate.shares[int(config.id) - 1] = result
                self.share_my_output_value(result, gate)
                break
                #print("******************", "share my output value", "******************")

    def reconstruct(self, shares):
        rec = self.pol.lagrange_interpolate(shares[0:])
        return rec



from app.api.polynomials import Polynomials
import config, json, requests
from app.client.routes import Client

class Ceps:
    def __init__(self, circuit):
        self.circuit = circuit
        self.cur_gid = 0
        self.pol = Polynomials()

    def run(self, my_value):
g        self.share_my_intput_value(my_value)

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
            output_gate = self.circuit[-1]
            result = self.reconstruct(output_gate.shares)[1]
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
        output_gate = self.circuit[-1]
        output_gate.shares.append(share)
        if self.received_all_output_shares():
            result = self.reconstruct(output_gate.shares)[1]
            self.protocol_done(result)

    def protocol_done(self, result):
        Client().get_response(result, self.circuit)

    def received_all_input_shares(self):
        for gate in self.circuit:
            if gate.type == 'input' and gate.output_value == None:
                return False
        return True

    def received_all_mult_shares(self, gate):
        return len(gate.shares) == config.player_count

    def received_all_output_shares(self):
        output_gate = self.circuit[-1]
        return len(output_gate.shares) == config.player_count

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
                prod = val_in_l * self.pol.mult_invers(val_in_r)
                self.share_my_mult_value(prod, gate)
                break
            elif gate.type == 'output':
                prev_gate = self.circuit[self.cur_gid - 1]
                gate.output_value = prev_gate.output_value
                self.cur_gid = self.cur_gid + 1
                result = gate.output_value
                gate.shares.append(result)
                self.share_my_output_value(result)



    def reconstruct(self, shares):
        rec = self.pol.lagrange_interpolate(shares)
        return rec



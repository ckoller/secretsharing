from app.api.polynomials import Polynomials
import config, json, requests, time

class Ceps:
    def __init__(self, circuit, sharingStrategy):
        self.sharingStrategy = sharingStrategy
        self.circuit = circuit["circuit"]
        self.output_gate_count = len(circuit["output_gates"])
        self.input_gates = circuit["input_gates"]
        self.circuit_type = circuit["type"]
        self.cur_gid = 0
        self.pol = Polynomials()
        self.output = []
        self.mv = []
        self.cur_layer = 1
        self.start = None

    def run(self):
        if self.start is None:
            self.start = time.time()
        self.share_my_input_values(self.mv)

    def setup(self, circuit, my_values):
        self.mv = my_values
        self.circuit = circuit["circuit"]
        self.output_gate_count = len(circuit["output_gates"])
        self.input_gates = circuit["input_gates"]
        self.circuit_type = circuit["type"]
        self.cur_gid = 0

    def share_my_input_values(self, my_values):
        self.sharingStrategy.share_my_input_values(my_values=my_values, circuit=self.circuit)
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def handle_input_shares(self, shares):
        if self.start is None:
            self.start = time.time()
        self.sharingStrategy.handle_input_shares(shares, self.circuit)
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def handle_mult_share(self, shares, gate_id, sender_id):
        if sender_id is not config.id:
            for tuple in shares:
                gate_id = tuple[0]
                share = tuple[1]
                gate = self.circuit[gate_id]
                gate.shares[sender_id-1] = share
        if self.received_all_mult_shares(shares):
            #print("got all")
            for tuple in shares:
                gate_id = tuple[0]
                gate = self.circuit[gate_id]
                result = self.reconstruct(gate.shares)[1]
                if gate.type == 'xor':
                    val_in_l = self.circuit[gate.wires_in[0]].output_value
                    val_in_r = self.circuit[gate.wires_in[1]].output_value
                    result = (val_in_l + val_in_r) - 2 * (result)
                    gate.output_value = result
                gate.output_value = result
            self.cur_layer = self.cur_layer + 1
            self.evaluate_circuit()

    def received_all_input_shares(self):
        for gate in self.circuit:
            if gate.type == 'input' and gate.output_value == None:
                return False
        return True

    def received_all_mult_shares(self, shares):
        for tuple in shares:
            gate_id = tuple[0]
            gate = self.circuit[gate_id]
            if None in gate.shares:
                #print(gate.shares, gate.id, gate.type)
                return False
        return True

    def evaluate_circuit(self):
        n = config.player_count
        layer_shares = {}
        found_gate_in_layer = True
        while found_gate_in_layer:
            found_gate_in_layer = False
            for gate in self.circuit:
                if gate.layer == self.cur_layer:
                    if gate.type == 'input':
                        found_gate_in_layer = True
                    elif gate.type == 'inv':
                        val_in = self.circuit[gate.wires_in[0]].output_value
                        gate.output_value = 1 - val_in
                        found_gate_in_layer = True
                    elif gate.type == 'and' or gate.type == 'xor':
                        val_in_l = self.circuit[gate.wires_in[0]].output_value
                        val_in_r = self.circuit[gate.wires_in[1]].output_value
                        prod = val_in_l * val_in_r
                        poly, shares = self.pol.create_poly_and_shares(prod, degree=int(n / 3), shares=n)
                        for player_id, player in config.players.items():
                            if player_id not in layer_shares:
                                layer_shares[player_id] = []
                            share = shares[player_id - 1]
                            tuple = (gate.id, share)
                            layer_shares[player_id].append(tuple)
                        gate.shares[int(config.id)-1] = shares[int(config.id)-1]
                        found_gate_in_layer = True
                    elif gate.type == 'output':
                        val_in = self.circuit[gate.wires_in[0]].output_value
                        gate.output_value = val_in
                        for player_id, player in config.players.items():
                            if player_id not in layer_shares:
                                layer_shares[player_id] = []
                            tuple = (gate.id, gate.output_value)
                            layer_shares[player_id].append(tuple)
                        gate.shares[int(config.id)-1] = gate.output_value
                        found_gate_in_layer = True

            # TODO output reconstruction in the end?

            # deal layer gate shares
            what = []
            if layer_shares != {}:
                for player_id, player in config.players.items():
                    what = layer_shares[player_id]
                    url = "http://" + player + "/api/ceps/mult_share/"
                    data = {"shares": json.dumps(what),
                            "sender_id": json.dumps(config.id)}
                    requests.post(url, data)
                if self.received_all_mult_shares(what):
                    self.handle_mult_share(what, 0, config.id)
                break
            self.cur_layer = self.cur_layer + 1
            #print("layer: ", self.cur_layer, "last: ", found_gate_in_layer)
            if not found_gate_in_layer:
                for gate in self.circuit:
                    if gate.type == "output":
                        self.output.append(gate.output_value)
                self.protocol_done(self.output)

    def reconstruct(self, shares):
        rec = self.pol.lagrange_interpolate(shares[0:])
        return rec

    def protocol_done(self, result):
        config.result[:] = result
        end = time.time()
        print("Time:",   end - self.start)
        #Client().get_response(result, self.circuit, self.mv)




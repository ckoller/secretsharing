import config, requests, json
import numpy as np

class ArithmeticSharingStrategy:
    def share_my_input_value(self, circuit, my_input_values):
        counter = 0
        for gate in circuit:
            if gate.type == 'input' and gate.wires_in[0] == int(config.id):
                d = my_input_values[counter] + gate.r_open
                counter = counter + 1
                for player_id, player in config.all_players.items():
                    url = "http://" + player + "/api/ceps_speed/input_d_shares/"
                    data = {"d": d, "gid": gate.id}
                    requests.post(url, data)

    def handle_input_share(self, d, gate_id, circuit):
        gate = circuit[gate_id]
        gate.output_value = d - gate.r

    def received_all_input_shares(self, circuit, is_preprocessed):
        for gate in circuit:
            if gate.type == 'input' and gate.output_value is None:
                return False
            if not is_preprocessed:
                return False
        return True

    def add_random_input_values_to_circuit(self, input_random_shares, input_gates):
        shares = np.concatenate(input_random_shares).tolist()
        for gate in input_gates:
            r = shares.pop()
            gate.r = r
            player_id = gate.wires_in[0]
            player = config.all_players[player_id]
            url = "http://" + player + "/api/ceps_speed/input_shares/"
            data = {"r": r, "gid": gate.id}
            requests.post(url, data)

class BooleanSharingStrategy:
    def share_my_input_value(self, circuit, my_input_values):
        counter = 0
        for gate in circuit:
            if gate.type == 'input' and config.id == '1':
                #print(counter, "hahah")
                d = my_input_values[counter] + gate.r_open
                counter = counter + 1
                for player_id, player in config.all_players.items():
                    url = "http://" + player + "/api/ceps_speed/input_d_shares/"
                    data = {"d": d, "gid": gate.id}
                    requests.post(url, data)

    def handle_input_share(self, d, gate_id, circuit):
        gate = circuit[gate_id]
        gate.output_value = d - gate.r

    def received_all_input_shares(self, circuit, is_preprocessed):
        for gate in circuit:
            if gate.type == 'input' and gate.output_value is None:
                return False
            if is_preprocessed is False:
                return False
        return True

    def add_random_input_values_to_circuit(self, input_random_shares, input_gates):
        shares = np.concatenate(input_random_shares).tolist()
        for gate in input_gates:
            r = shares.pop()
            gate.r = r
            player_id = 1
            player = config.all_players[player_id]
            url = "http://" + player + "/api/ceps_speed/input_shares/"
            data = {"r": r, "gid": gate.id}
            requests.post(url, data)

class BooleanLayerSharingStrategy:

    def __init__(self):
        self.received_input_shares = False

    def share_my_input_value(self, circuit, my_input_values):
        d_values = {}
        for gate in circuit:
            if gate.type == 'input' and config.id == '1':
                input_wire_id = gate.wires_in[0]
                d = my_input_values[input_wire_id] + gate.r_open
                d_values[gate.id] = d
        if d_values != {}:
            for player_id, player in config.all_players.items():
                url = "http://" + player + "/api/ceps_speed/input_d_dict/"
                data = {"d": json.dumps(d_values)}
                requests.post(url, data)

    def handle_input_share(self, d, gate_id, circuit):
        #print("*****************", d)
        for gate_id, d_val in d.items():
            gate = circuit[int(gate_id)]
            gate.output_value = d_val - gate.r
            #print(gate.id, gate.output_value)
        self.received_input_shares = True

    def received_all_input_shares(self, circuit, is_preprocessed):
        if not is_preprocessed:
            return False
        else:
            return self.received_input_shares

    def add_random_input_values_to_circuit(self, input_random_shares, input_gates):
        shares = np.concatenate(input_random_shares).tolist()
        for gate in input_gates:
            r = shares.pop()
            gate.r = r
            player_id = 1
            player = config.all_players[player_id]
            url = "http://" + player + "/api/ceps_speed/input_shares/"
            data = {"r": r, "gid": gate.id}
            requests.post(url, data)



class BooleanLayerSharingStrategyByPlayerId:

    def __init__(self):
        self.received_input_shares = False

    def share_my_input_value(self, circuit, my_input_values):
        d_values = {}
        counter = 0
        for gate in circuit:
            if gate.type == 'input' and config.id == str(gate.wires_in[0]):
                d = my_input_values[counter] + gate.r_open
                counter = counter + 1
                d_values[gate.id] = d
        if d_values != {}:
            for player_id, player in config.all_players.items():
                url = "http://" + player + "/api/ceps_speed/input_d_dict/"
                data = {"d": json.dumps(d_values)}
                requests.post(url, data)

    def handle_input_share(self, d, gate_id, circuit):
        #print("*****************", d)
        for gate_id, d_val in d.items():
            gate = circuit[int(gate_id)]
            gate.output_value = d_val - gate.r
            #print(gate.id, gate.output_value)
        self.received_input_shares = True

    def received_all_input_shares(self, circuit, is_preprocessed):
        if not is_preprocessed:
            return False
        else:
            return self.received_input_shares

    def add_random_input_values_to_circuit(self, input_random_shares, input_gates):
        shares = np.concatenate(input_random_shares).tolist()
        for gate in input_gates:
            r = shares.pop()
            gate.r = r
            player_id = gate.wires_in[0]
            player = config.all_players[player_id]
            url = "http://" + player + "/api/ceps_speed/input_shares/"
            data = {"r": r, "gid": gate.id}
            requests.post(url, data)



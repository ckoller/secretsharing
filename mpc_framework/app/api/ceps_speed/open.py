from app.api.polynomials import Polynomials
import requests, json, config
import numpy as np

class Open:
    def __init__(self):
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.shares = {}

    def request(self, data, type):
        king = config.all_players[1]
        url = "http://" + king + "/api/ceps_speed/protocolOpen/share/"
        data = {"shares": json.dumps(np.array(data).tolist()), "type": type}
        r = requests.post(url, data)

    def request_with_load_balancing(self, data, type):
        counter = 0
        shares_for_players = {}
        for gate in data:
            king_id = counter % config.player_count + 1
            counter = counter + 1
            if king_id in shares_for_players:
                shares_for_players[king_id].append(gate)
            else:
                shares_for_players[king_id] = [gate]

        for player_id, player in config.all_players.items():
            if int(player_id) in shares_for_players:
                url = "http://" + player + "/api/ceps_speed/protocolOpen/share/"
                data = {"shares": json.dumps(np.array(shares_for_players[player_id]).tolist()), "type": type}
                r = requests.post(url, data)

    def handle_request(self, data, type):
        if type in self.shares.keys():
            array = self.shares[type]
            array.append(data)
        else:
            self.shares[type] = [data]
        received_all = len(self.shares[type]) == config.player_count
        if received_all:

            rec = None
            if type == "layer":
                sorted = self.sort_layer_list(self.shares[type])
                rec = self.reconstruct_layer(sorted)
            elif type == "D":
                x = self.shares[type]
                shares = [[x[i][j] for i in range(0, len(x))] for j in range(0, len(x[0]))]
                rec = [self.pol.lagrange_interpolate(shares[x])[1] for x in range(0, len(x[0]))]
            elif type == "alpha_beta" or type == "and" or type == "xor":
                aplha = [self.shares[type][x][0] for x in range(len(self.shares[type]))]
                beta = [self.shares[type][x][1] for x in range(len(self.shares[type]))]
                rec_aplha = self.pol.lagrange_interpolate(aplha)[1]
                rec_beta = self.pol.lagrange_interpolate(beta)[1]
                rec = [rec_aplha, rec_beta]
            elif type == "output":
                rec = self.pol.lagrange_interpolate(self.shares[type])[1]
            else:
                rec = self.pol.lagrange_interpolate(self.shares[type])[1]
            del self.shares[type]

            for player_id, player in config.all_players.items():
                url = "http://" + player + "/api/ceps_speed/protocolOpen/reconstruction/"
                data = {"rec": json.dumps(rec), "type": type}
                requests.post(url, data)

    def sort_layer_list(self, layer_list):
        sorted = {}
        for player_input in layer_list:
            for gate in player_input:
                gate_id = gate[0]
                gate_type = gate[1]
                if (gate_id, gate_type) not in sorted:
                    sorted[(gate_id, gate_type)] = [[], []]
                if gate_type == 'xor' or gate_type == 'and':
                    alpha = int(gate[2])
                    beta = int(gate[3])
                    sorted[(gate_id, gate_type)][0].append(alpha)
                    sorted[(gate_id, gate_type)][1].append(beta)
                elif gate_type == 'output':
                    value = int(gate[2])
                    sorted[(gate_id, gate_type)][0].append(value)
        return sorted

    def reconstruct_layer(self, sorted):
        rec = []
        for gate, shares in sorted.items():
            gate_id = gate[0]
            gate_type = gate[1]
            if gate_type == 'xor' or gate_type == 'and':
                alpha = shares[0]
                beta = shares[1]
                rec_a = self.pol.lagrange_interpolate(alpha)[1]
                rec_b = self.pol.lagrange_interpolate(beta)[1]
                rec.append([gate_id, gate_type, rec_a, rec_b])
            elif gate_type == 'output':
                output_shares = shares[0]
                rec_o = self.pol.lagrange_interpolate(output_shares)[1]
                rec.append([gate_id, gate_type, rec_o])
        return rec





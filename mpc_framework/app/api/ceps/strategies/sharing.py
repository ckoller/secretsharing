import config, json, requests
from app.api.polynomials import Polynomials

class ShareByWireId:

    def __init__(self):
        self.pol = Polynomials()

    def share_my_input_values(self, my_values, circuit):
        n = config.player_count
        input_shares = {}
        for gate in circuit:
            if gate.type == 'input':
                if config.id == '1':
                    my_value = my_values[gate.wires_in[0]]
                    poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
                    for player_id, player in config.players.items():
                        if player_id not in input_shares:
                            input_shares[player_id] = []
                        input_shares[player_id].append([gate.id, shares[player_id - 1]])
                        gate.output_value = shares[int(config.id) - 1]
        if input_shares != {}:
            self.send_input_shares(input_shares)

    def send_input_shares(self, input_shares):
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/share/"
            data = {"shares": json.dumps(input_shares[player_id]),
                    "sender_id": json.dumps(config.id)}
            requests.post(url, data)


    def handle_input_shares(self, shares, circuit):
        for share in shares:
            gate_id = share[0]
            point = share[1]
            gate = circuit[gate_id]
            gate.output_value = point

class ShareByWirePlayerId:

    def __init__(self):
        self.pol = Polynomials()

    def share_my_input_values(self, my_values, circuit):
        print("***************** in sharing **************")
        n = config.player_count
        input_shares = {}
        counter = 0
        for gate in circuit:
            if gate.type == 'input':
                if config.id == str(gate.wires_in[0]):
                    print("*************** inside my input ****************")
                    my_value = my_values[counter]
                    counter = counter + 1
                    poly, shares = self.pol.create_poly_and_shares(my_value, degree=int(n / 3), shares=n)
                    for player_id, player in config.players.items():
                        if player_id not in input_shares:
                            input_shares[player_id] = []
                        input_shares[player_id].append([gate.id, shares[player_id - 1]])
                        gate.output_value = shares[int(config.id) - 1]
        if input_shares != {}:
            self.send_input_shares(input_shares)

    def send_input_shares(self, input_shares):
        print("***************** sending input shares *******************")
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/share/"
            data = {"shares": json.dumps(input_shares[player_id]),
                    "sender_id": json.dumps(config.id)}
            requests.post(url, data)


    def handle_input_shares(self, shares, circuit):
        print("******************** got input shares *****************")
        for share in shares:
            gate_id = share[0]
            point = share[1]
            gate = circuit[gate_id]
            gate.output_value = point
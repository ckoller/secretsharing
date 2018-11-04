import config, requests

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



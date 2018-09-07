from app.api.polynomials import Polynomials
import config, json, requests

class Ceps:
    def __init__(self):
        self.poly = []
        self.shares = []
        self.share_dict = {}
        self.output_shares = []
        self.input_shares = []

    def input_sharing(self, my_value):
        self.share_value(my_value, "input")

    def share_value(self, value, share_type):
        pol = Polynomials()
        n = config.player_count
        poly, shares = pol.create_poly_and_shares(value, degree=int(n / 3), shares=n)
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/share/"
            data = {"share": json.dumps(shares[player_id - 1]),
                    "share_type": share_type,
                    "sender_id": config.id}
            r = requests.post(url, data)
        self.set_share(int(config.id), shares[int(config.id) - 1], share_type)

    def set_share(self, owner_id, share, share_type):
        if self.share_dict == {}:
            self.share_dict["input"] = {player_id: None for player_id in range(1, config.player_count + 1)}
            self.share_dict["output"] = {player_id: None for player_id in range(1, config.player_count + 1)}
            self.share_dict["output_list"] = []
        if self.share_dict[share_type][int(owner_id)] is None:
            self.share_dict[share_type][int(owner_id)] = share
            if share_type == "output":
                self.output_shares.append(share)
            if share_type == "input":
                self.input_shares.append(share)

    def output_sharing(self, y):
        for player_id, player in config.players.items():
            url = "http://" + player + "/api/ceps/share/"
            data = {"share": json.dumps(y),
                    "share_type": "output",
                    "sender_id": config.id}
            r = requests.post(url, data)
        self.set_share   (config.id, y, "output")
        if self.received_all_shares("output"):
            print(self.reconstruct(self.output_shares)[1], "res")

    def reconstruct(self, shares):
        pol = Polynomials()
        rec = pol.lagrange_interpolate(shares)
        return rec

    def received_all_shares(self, share_type):
        return self.share_dict != {} and share_type in self.share_dict and None not in self.share_dict[share_type].values()

    def add_all(self):
        result = sum(self.input_shares)
        self.output_sharing(result)

    def mul_all(self):
        prod = 1
        for x in self.input_shares:
            prod = self.mult(x, prod)
        self.output_sharing(prod)

    def computation_phase(self):
        print("ha")

    def output_reconstruction(self):
        print("ha")


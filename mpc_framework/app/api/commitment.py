import config, json, requests
from .polynomials import Polynomials

class Commitment:
    def __init__(self, prover_id, commit_id):
        self.prover_id = prover_id
        self.commit_id = commit_id
        self.my_id = config.id
        self.players = config.players
        self.player_count = config.player_count
        self.degree = int(self.player_count / 3)
        self.pol = Polynomials()
        self.con_vals = {player_id: 0.0 for player_id in range(1, self.player_count + 1)
                         if player_id != prover_id and player_id != int(self.my_id)}

    def commit_to_value(self, value):
        poly, shares = self.pol.create_poly_and_shares(secret=value, degree=self.degree, shares=self.player_count)
        for player_id in self.players:
            player = self.players[player_id]
            url = "http://" + player + "/api/commit/"
            share = json.dumps(shares[player_id].tolist())
            data = {"share": share, "prover_id" : self.my_id, "commit_id" : self.commit_id}
            r = requests.post(url, data)
            print("request sent to: ", url)
            print(r.status_code)

    def share_con_values(self, share):
        share_poly = share
        for player_id in self.players:
            if player_id != self.prover_id:
                player = self.players[player_id]
                consistency_value = self.pol.eval_poly(share_poly, player_id)
                url = "http://" + player + "/api/commit/" + str(self.commit_id) + "/consistency/"
                data = {"consistency_value": consistency_value,
                        "prover_id": self.prover_id,
                        "sender_id": self.my_id,
                        "commit_id" : self.commit_id}
                r = requests.post(url, data)
                print("request sent to: ", url)
                print(r.status_code)

    def check_con_value(self, con_val, sender_id):
        self.con_vals[sender_id] = con_val
        if not self.con_vals.__contains__(0.0):
            print("got all")
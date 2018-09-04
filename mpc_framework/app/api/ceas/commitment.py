import config, json, requests
from app.api.polynomials import Polynomials
import numpy as np
from collections import Counter

class Commitment:
    def __init__(self, prover_id, commit_id):
        self.prover_id = prover_id
        self.commit_id = commit_id
        self.my_id = config.id
        self.players = config.players
        self.player_count = config.player_count
        self.degree = int(self.player_count / 3)
        self.pol = Polynomials()
        self.con_vals = {player_id: None for player_id in range(1, self.player_count + 1)
                            if player_id != prover_id and player_id != int(self.my_id)}
        self.disputes = {player_id: None for player_id in range(1, self.player_count + 1)
                            if player_id != prover_id and player_id != int(self.my_id)}
        self.accusations_con = {player_id: None for player_id in range(1, self.player_count + 1)
                            if player_id != int(prover_id)}
        self.accusations_share = {player_id: None for player_id in range(1, self.player_count + 1)
                            if player_id != int(prover_id)}
        self.received = {player_id: None for player_id in range(1, self.player_count + 1)
                            if player_id != int(prover_id)}
        self.dispute_flag = True

    # 1. create poly and broadcast shares.
    def commit_to_value(self, value):
        global shares
        poly, shares = self.pol.create_poly_and_shares_bi(secret=value, degree=self.degree, shares=self.player_count)
        for player_id in self.players:
            player = self.players[player_id]
            url = "http://" + player + "/api/ceas/commit/"
            share = json.dumps(shares[player_id].tolist())
            data = {"share": share, "prover_id": self.my_id, "commit_id": self.commit_id}
            r = requests.post(url, data)
        return poly # poly

    # 2. broadcast consistency values
    def share_con_values(self, share):
        global share_poly
        share_poly = share
        for player_id in self.players:
            if player_id != self.prover_id:
                player = self.players[player_id]
                consistency_value = self.pol.eval_poly(share_poly, player_id)
                if self.my_id == '1':
                    consistency_value = 3000
                url = "http://" + player + "/api/ceas/commit/" + str(self.commit_id) + "/consistency/"
                data = {"consistency_value": consistency_value,
                        "prover_id": self.prover_id,
                        "sender_id": self.my_id,
                        "commit_id": self.commit_id}
                r = requests.post(url, data)
        self.check_con_value(None, None)

    # 3. check consistency values and broadcast disputes
    # and check the degree of the polynomium. TODO check polynomium and ask why it is done in this step
    def check_con_value(self, con_val, sender_id):
        disputes = []
        status = "success"
        if con_val is not None:
            self.con_vals[sender_id] = con_val
        if None not in self.con_vals.values() and 'share_poly' in globals():
            rest_url = "/api/ceas/commit/" + str(self.commit_id) + "/dispute/"
            for player_id in self.con_vals:
                if len(share_poly) < self.degree + 1:
                    print("p_i sent me a share of too low degree")
                if float(self.con_vals[player_id]) != float(self.pol.eval_poly(share_poly, int(player_id))):
                    disputes.append(player_id)
                    status = "dispute"
            data = {"status": status,   # todo status is not used
                "sender_id": self.my_id,
                "disputes": json.dumps(disputes),
                "prover_id": self.prover_id,
                "commit_id": self.commit_id}
            self.broadcast(rest_url, data, "post")

    # 4. For each dispute reported in the previous step, P i broadcasts the correct value of β k,j
    def handle_dispute(self, status, sender_id, disputes):
        self.disputes[sender_id] = disputes
        if None not in self.disputes.values() and self.my_id == self.prover_id and self.dispute_flag:
            con_vals = {p_id: {} for p_id in range(1, self.player_count + 1) if p_id != int(self.prover_id)}
            for p_id, dispute_list in self.disputes.items():
                for d_id in dispute_list:
                    share = self.pol.eval_poly(shares[p_id], d_id)
                    con_vals[p_id][d_id] = share
                    con_vals[d_id][p_id] = share
            rest_url = "/api/ceas/commit/" + str(self.commit_id) + "/consistency/"
            data = {"consistency_values": json.dumps(con_vals),
                    "sender_id": self.my_id,
                    "prover_id": self.prover_id,
                    "commit_id": self.commit_id}
            self.broadcast(rest_url, data, "put")
            self.dispute_flag = False

    # 5. If any P k finds a disagreement between what P i has broadcast and what he received
    # privately from P i , he knows P i is corrupt and broadcasts (accuse, k).
    # TODO check message came from prover
    # TODO check that we got expected con_vals
    def check_new_con_value(self, con_vals):
        should_accuse = False
        my_con_vals = con_vals[self.my_id]
        for d_id, value in my_con_vals.items():
            if self.my_id == '1':
                value = 3000
            if float(value) != self.pol.eval_poly(share_poly, int(d_id)):
                should_accuse = True
                break
        self.accusations_con[int(self.my_id)] = "accuse" if should_accuse else "success"
        rest_url = "/api/ceas/commit/" + str(self.commit_id) + "/accusation/"
        data = {"accusation": self.accusations_con[int(self.my_id)],
                "sender_id": self.my_id,
                "prover_id": self.prover_id,
                "commit_id": self.commit_id}
        self.broadcast(rest_url, data, "post")
        self.handle_con_accusation(None, None)

    # 6. For any accusation from P k in the previous step, P i broadcasts f k (X). TODO if person tries to accuse multiple times
    def handle_con_accusation(self, accusation, sender_id):
        if accusation is not None:
            self.accusations_con[sender_id] = accusation
        if None not in self.accusations_con.values() and self.my_id == self.prover_id:
            acc_shares = {acc_id : shares[acc_id].tolist() for acc_id, acc in self.accusations_con.items() if acc == "accuse"}
            rest_url = "/api/ceas/commit/"
            data = {"shares": json.dumps(acc_shares),
                    "sender_id": self.my_id,
                    "prover_id": self.my_id,
                    "commit_id": self.commit_id}
            self.broadcast(rest_url, data, "put")

    # 7. If any P k finds a new disagreement between what P i has now broadcast and what he
    # received privately from P i , he knows P i is corrupt and broadcasts (accuse, k).
    # TODO check that we got expected shares
    def check_share(self, shares):
        accusation = "success"
        for share_id, share in shares.items():
            con_val1 = self.pol.eval_poly(share_poly, int(share_id))
            con_val2 = self.pol.eval_poly(np.array(share), int(self.my_id))
            if con_val1 != con_val2 :
                accusation = "accuse"
                break
        self.accusations_share[int(self.my_id)] = accusation
        rest_url = "/api/ceas/commit/" + str(self.commit_id) + "/accusation/"
        data = {"accusation": accusation,
                "sender_id": self.my_id,
                "prover_id": self.prover_id,
                "commit_id": self.commit_id}
        self.broadcast(rest_url, data, "put")
        self.handle_share_accusation(None, None)

    # 8. If the information broadcast by P i is not consistent, or if more than t players have
    # accused P i , players output fail.
    # Otherwise, players who accused P i and had a new polynomial f k (X) broadcast will
    # accept it as their polynomial. All others keep the polynoshare_polymial they received in the first
    # step. Now each P k outputs success and stores (cid, i, β k = f k (0)). In addition P i
    # stores the polynomial g a (X) = f a (X, 0).
    def handle_share_accusation(self, accusation, sender_id):
        if accusation is not None:
            self.accusations_share[sender_id] = accusation
        if None not in self.accusations_share.values():
            accuse_count = Counter(self.accusations_share.values())["accuse"]
            if accuse_count <= self.degree:
                print("success")
                if self.my_id == self.prover_id:
                    return (self.commit_id, self.prover_id, "random")
                else:
                    return (self.commit_id, self.prover_id, share_poly)
            else:
                print("fail on commitment:", self.commit_id)
        return None, None, None

    def broadcast(self, rest_url, data, request_type):
        for player_id in self.players:
            player = self.players[player_id]
            url = "http://" + player + rest_url
            if request_type == "post":
                r = requests.post(url, data)
            elif request_type == "put":
                r = requests.put(url, data)
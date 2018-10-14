from app.api.polynomials import Polynomials
import requests, json, config
import numpy as np

class Open:
    def __init__(self):
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.shares = {}

    def request(self, data, type):
        king = "127.0.0.1:5001"
        url = "http://" + king + "/api/ceps_speed/protocolOpen/share/"
        data = {"shares": json.dumps(np.array(data).tolist()), "type": type}
        r = requests.post(url, data)
        #print("got request of type", type)

    def handle_request(self, data, type):
        if type in self.shares.keys():
            array = self.shares[type]
            array.append(data)
        else:
            self.shares[type] = [data]
        #print("HAHHAHAHAHA", type,  self.shares[type])
        received_all = len(self.shares[type]) == config.player_count
        if received_all:
            #print("GOOTOTOTOTOTOTOTOTOTOTOTO ALLALALALLALALALALAALAL",  type, self.shares[type])

            rec = None
            if type == "D":
                x = self.shares[type]
                shares = [[x[i][j] for i in range(0, len(x))] for j in range(0, len(x[0]))]
                rec = [self.pol.lagrange_interpolate(shares[x])[1] for x in range(0, len(x[0]))]
            elif type == "alpha_beta":
                aplha = [self.shares[type][x][0] for x in range(len(self.shares[type]))]
                beta = [self.shares[type][x][1] for x in range(len(self.shares[type]))]
                rec_aplha = self.pol.lagrange_interpolate(aplha)[1]
                rec_beta = self.pol.lagrange_interpolate(beta)[1]
                rec = [rec_aplha, rec_beta]
                del self.shares["alpha_beta"]
            elif type == "output":
                print("HAHHAHAHAHA", type,  self.shares[type])
                rec = self.pol.lagrange_interpolate(self.shares[type])[1]
                del self.shares["output"]

            else:
                rec = self.pol.lagrange_interpolate(self.shares[type])[1]
            for player_id, player in config.all_players.items():
                url = "http://" + player + "/api/ceps_speed/protocolOpen/reconstruction/"
                data = {"rec": json.dumps(rec), "type": type}
                requests.post(url, data)
from app.api.polynomials import Polynomials
import random, math
import numpy as np
import config, json, requests

class Ceps_Speed:
    def __init__(self, circuit):
        self.circuit = circuit[0]
        self.input_gates = circuit[1]
        self.mult_gates = circuit[2]
        self.n = config.player_count
        self.t = int(math.ceil((self.n - 1) / 2))
        self.l = self.n-self.t
        self.protocol_open = Open()
        self.pr = ProtocolRandom(self.l, "pre") # TODO Cleanup types
        self.pdr = ProtocolDoubleRandom(self.l, "pre")
        self.protocol_triples = ProtocolTriples(self.l, self.protocol_open, "pre")
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.a_open = None
        self.b_open = None
        self.c_open = None

    def run(self, my_value):
        self.preprocessing()

    def preprocessing(self):
        i = len(self.input_gates)
        m = len(self.mult_gates)
        pdr_count = int(m / (self.l)) + 1
        pr_count = pdr_count * 2
        print("number of input gates", i)
        print("number of protocol random should run (input)", int(i / 2 + 1))

        print("number of mult gates", m)
        print("number of protocol random should run", pr_count)
        print("number of protocol double random should run", pdr_count)
        print("number of random protocols produce (l)", self.l)
        print("number of players (n)", self.n)

        pr_shares = self.pr.generate_random_shares(i)

        pr_shares = self.pr.generate_random_shares(pr_count)
        pdr_shares_r, pdr_shares_R = self.pdr.generate_random_shares(pdr_count)

        #print("pr", pr_shares)
        #print("pdr_r", pdr_shares_r)
        #print("pdr_R", pdr_shares_R)

        self.deal_rand_shares(pr_shares, pdr_shares_r, pdr_shares_R)

    def deal_rand_shares(self, pr_shares, pdr_shares_r, pdr_shares_R):
        for player_id, player in config.all_players.items():
            pr_share_r = pr_shares[player_id - 1]
            pdr_share_r = pdr_shares_r[player_id - 1]
            pdr_share_R = pdr_shares_R[player_id - 1]
            url = "http://" + player + "/api/ceps_speed/random_shares/"
            data = {"pr_share": json.dumps(pr_share_r.tolist()),
                    "pdr_share_r": json.dumps(pdr_share_r.tolist()),
                    "pdr_share_R": json.dumps(pdr_share_R.tolist())}
            requests.post(url, data)

    def compute_preprossing_randomness(self, pr_share, pdr_share_r, pdr_share_R):
        protocol_random_shares = self.pr.calculate_r(pr_share)
        protocol_double_random_shares = self.pdr.calculate_r(pdr_share_r, pdr_share_R)
        #print("single", protocol_random_shares)
        #print("double", protocol_double_random_shares)

        if protocol_random_shares is not None:
            #print(protocol_random_shares)
            #print(protocol_double_random_shares[0])
            #print(protocol_double_random_shares[1])
            self.protocol_triples.run(protocol_random_shares, protocol_double_random_shares[0], protocol_double_random_shares[1])

    def open_request(self, data, type):
        self.protocol_open.request(data, type)

    def handle_protocol_open_request(self, data, type):
        self.protocol_open.handle_request(data, type)

    def handle_protocol_open_answer(self, data, type):
        if type == "D":
            a, b, c = self.protocol_triples.calculate_c(data)
            self.preproccess_circuit(a, b, c)
        elif type == "A":
            self.a_open = data
        elif type == "B":
            self.b_open = data
        elif type == "C":
            self.c_open = data
        else:
            print(type, data)
        if self.a_open is not None and self.b_open is not None and self.c_open is not None:
            for x in range(len(self.a_open)):
                print("triples", self.a_open[x] * self.b_open[x] % self.prime, "==", self.c_open[x])

    def preproccess_circuit(self, a, b, c):
        self.protocol_open.request(a, "A")
        self.protocol_open.request(b, "B")
        self.protocol_open.request(c, "C")


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

    def handle_request(self, data, type):
        if type in self.shares.keys():
            array = self.shares[type]
            array.append(data)
        else:
            self.shares[type] = [data]
        received_all = len(self.shares[type]) == config.player_count
        if received_all:
            x = self.shares[type]
            shares = [[x[i][j] for i in range(0, len(x))] for j in range(0, len(x[0]))]
            rec = [self.pol.lagrange_interpolate(shares[x])[1] for x in range(0, len(x[0]))]
            for player_id, player in config.all_players.items():
                url = "http://" + player + "/api/ceps_speed/protocolOpen/reconstruction/"
                data = {"rec": json.dumps(rec), "type": type}
                r = requests.post(url, data)

class ProtocolTriples:
    def __init__(self, l, open, type):
        self.l = l
        self.open = open
        self.type = type
        self.n = config.player_count
        self.t = int((self.n - 1) / 2)
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.a = None
        self.b = None
        self.D = []

    def run(self, r_2m, rm, R):
        m = len(rm)
        a, b = np.split(np.transpose(r_2m), 2)
        self.a = np.concatenate(a, axis=0)
        self.b = np.concatenate(b, axis=0)
        #print("a", self.a)
        #print("b", self.b)
        R = np.concatenate(R, axis=0)
        self.rm = np.concatenate(rm, axis=0)
        D = [(self.a[x] * self.b[x] + R[x]) % self.prime for x in range(len(R))]
        #print("D", D)
        self.open.request( D, "D")

    def calculate_c(self, D_open):
        c = [(D_open[x] - self.rm[x]) % self.prime for x in range(len(D_open))]
        #print("c",c)
        return self.a, self.b, c

class ProtocolDoubleRandom:
    def __init__(self, l, type):
        self.l = l
        self.type = type
        self.n = config.player_count
        self.t = int((self.n - 1) / 2)
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.shares_t = []
        self.shares_2t = []

    def generate_random_shares(self, count):
        poly_t = np.transpose([[random.SystemRandom().randint(1, self.prime) for i in range(self.t + 1)] for j in range(count)])
        poly_2t = np.transpose([[random.SystemRandom().randint(1, self.prime) for i in range(2 * self.t + 1)] for j in range(count)])
        s = random.SystemRandom().randint(1, self.prime)
        poly_t[0] = s
        poly_2t[0] = s
        M_t = self.pol.van(self.n, self.t + 1)
        M_2t = self.pol.van(self.n, 2 * self.t + 1)
        shares_t = np.dot(M_t, poly_t) % self.prime
        shares_2t = np.dot(M_2t, poly_2t) % self.prime
        return shares_t, shares_2t

    def calculate_r(self, share_t, share_2t):
        self.shares_t.append(share_t)
        self.shares_2t.append(share_2t)
        received_all = len(self.shares_t) == self.n
        if received_all:
            #print("protocol random r shares after dealing", self.shares_t)
            #print("protocol random R shares after dealing", self.shares_2t)

            M = self.pol.van(self.n, self.l)
            r = np.dot(np.transpose(M), self.shares_t)
            R = np.dot(np.transpose(M), self.shares_2t)
            return [r, R]
        return None

class ProtocolRandom:
    def __init__(self, l, type):
        self.l = l
        self.type = type
        self.n = config.player_count
        self.t = int((self.n - 1) / 2)
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.shares = []

    def generate_random_shares(self, count):
        poly = np.transpose([[random.SystemRandom().randint(1, self.prime) for i in range(self.t+1)] for j in range(count)])
        M = self.pol.van(self.n, self.t + 1)
        shares = np.dot(M, poly) % self.prime
        return shares

    def calculate_r(self, share):
        self.shares.append(share)
        received_all = len(self.shares) == self.n
        if received_all:
            #print("protocol random shares after dealing", self.shares)
            M = self.pol.van(self.n, self.l)
            r = np.dot(np.transpose(M), self.shares)
            #print("r0", r, self.l)
            return r
        return None



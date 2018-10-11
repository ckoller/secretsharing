from app.api.polynomials import Polynomials
import random, math
import numpy as np
import config, json, requests
from app.client.routes import Client

class Ceps_Speed:
    def __init__(self, circuit):
        self.circuit = circuit[0]
        self.input_gates = circuit[1]
        self.cur_gid = 0
        self.preprocessing = Preprocessing(circuit)
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.my_value = []
        self.output = []
        self.open = Open()
        self.preprocessed = False

    def set_new_circuit(self, circuit):
        self.circuit = circuit[0]
        self.input_gates = circuit[1]
        self.cur_gid = 0
        self.preprocessing = Preprocessing(circuit)
        self.pol = Polynomials()
        self.prime = self.pol.get_prime()
        self.my_values = []
        self.open = Open()

    def run(self, my_values):
        self.my_values = my_values
        self.preprocessing.run()

    def set_preprossing_circuit(self, circuit):
        self.circuit = circuit
        self.preprocessed = True
        self.share_my_input_value()


    def share_my_input_value(self):
        if self.received_all_input_shares():
            #print("**************************share_my_input_value EVAL****************************")
            self.evaluate_circuit()
        counter = 0
        for gate in self.circuit:
            if gate.type == 'input' and gate.wires_in[0] == int(config.id):
                d = self.my_values[counter] + gate.r_open
                counter = counter + 1
                for player_id, player in config.all_players.items():
                    url = "http://" + player + "/api/ceps_speed/input_d_shares/"
                    data = {"d": d, "gid": gate.id}
                    requests.post(url, data)


    def received_all_input_shares(self):
        for gate in self.circuit:
            if gate.type == 'input' and gate.output_value is None:
                return False
            if not self.preprocessed:
                return False
        return True

    def handle_input_share(self, d, gate_id):
        gate = self.circuit[gate_id]
        gate.output_value = d - gate.r
        if self.received_all_input_shares():
            #print("**************************handle_input_share****************************")

            self.evaluate_circuit()

    def evaluate_circuit(self):
        for gate_id in range(self.cur_gid, len(self.circuit)):
            gate = self.circuit[gate_id]
            print("**************************", gate.type, gate.id, "****************************")

            if gate.type == 'input':
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'add':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                gate.output_value = val_in_l + val_in_r
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'scalar_mult':
                val_in = self.circuit[gate.wires_in[0]].output_value
                scalar = gate.scalar
                gate.output_value = val_in * scalar
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'mult':
                val_in_l = self.circuit[gate.wires_in[0]].output_value
                val_in_r = self.circuit[gate.wires_in[1]].output_value
                alpha = val_in_l + gate.a
                beta = val_in_r + gate.b

                self.open.request([alpha, beta], "alpha_beta")
                break
            elif gate.type == 'output':
                prev_gate = self.circuit[self.cur_gid - 1]
                gate.output_value = prev_gate.output_value
                self.cur_gid = self.cur_gid + 1
                result = gate.output_value
                Client().get_response(self.output, self.circuit, None)
                self.open.request(result, "output")
                break

    def handle_protocol_open_answer(self, answer, type):
        if type == "output":
            ("**************************", "output answer", "****************************")

            self.output.append(answer)
            if self.received_all_outputs():
                Client().get_response(self.output, self.circuit, None)
                print("done")
            else:
                self.cur_gid = self.cur_gid + 1
                self.evaluate_circuit()
        elif type == "alpha_beta":
            gate = self.circuit[self.cur_gid]
            alpha_open = answer[0]
            beta_open = answer[1]
            #("**************************", gate.c, "****************************")
            x = (alpha_open*beta_open - alpha_open*gate.b - beta_open*gate.a + gate.c)
            gate.output_value = x
            self.cur_gid = self.cur_gid + 1
            #print("**************************handle_protocol_open_answer****************************")
            self.evaluate_circuit()

    def received_all_outputs(self):
        for gate in self.circuit:
            if gate.type == "output":
                if gate.output_value == None:
                    return False
        return True

class Preprocessing:
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
        self.input_shares = {}

    def run(self):
        i = len(self.input_gates)
        m = len(self.mult_gates)
        protocol_double_random_count = int(m / (self.l)) + 1
        protocol_random_count = (protocol_double_random_count * 2) + int(i / 2) + 1
        #print("number of input gates", i, "so it need protocol random to run", int(i / 2) + 1)
        #print("number of mult gates", m, "so it need protocol random to run", 2*protocol_double_random_count)
        #print("number of protocol random should run", protocol_random_count)
        #print("number of protocol double random should run", protocol_double_random_count)
        #print("number of random protocols produce (l)", self.l)
        #print("number of players (n)", self.n)
        pr_shares = self.pr.generate_random_shares(protocol_random_count)
        pdr_shares_r, pdr_shares_R = self.pdr.generate_random_shares(protocol_double_random_count)


        #print("pr\n", pr_shares)
        #print("pdr_r\n", pdr_shares_r)
        #print("pdr_R\n", pdr_shares_R)

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
        #print("single\n", protocol_random_shares)
        #print("double\n", protocol_double_random_shares)

        if protocol_random_shares is not None:
            i = len(self.input_gates)
            m = len(self.input_gates)

            i_runs = int(i / 2) + 1

            #print("i_runs", i_runs)
            #print("2m_runs", m*2)
            input, mult = np.hsplit(protocol_random_shares, [i_runs]) #l x i_runs, l x 2m_runs
            #print("input random shares", input)
            #print("mult random shares", mult)
            self.add_random_input_values_to_circuit(input)
            #print(protocol_random_shares)
            #print(protocol_double_random_shares[0])
            #print(protocol_double_random_shares[1])
            self.protocol_triples.run(mult, protocol_double_random_shares[0], protocol_double_random_shares[1])

    def add_random_input_values_to_circuit(self, input_random_shares):
        shares = np.concatenate(input_random_shares).tolist()
        for gate in self.input_gates:
            r = shares.pop()
            gate.r = r
            player_id = gate.wires_in[0]
            player = config.all_players[player_id]
            url = "http://" + player + "/api/ceps_speed/input_shares/"
            data = {"r": r, "gid": gate.id}
            requests.post(url, data)


    def handle_random_input_shares(self, r, gate_id):
        if gate_id in self.input_shares:
            shares = self.input_shares[gate_id]
            shares.append(r)
            received_all = len(shares) == config.player_count
            if received_all:
                gate = self.circuit[gate_id]
                gate.r_open = self.pol.lagrange_interpolate(shares)[1]
        else:
            self.input_shares[gate_id] = [r]


    def handle_protocol_open_answer(self, data, type):
        if type == "D":
            a, b, c = self.protocol_triples.calculate_c(data)
            self.add_triples_to_circuit(a, b, c)
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

    def add_triples_to_circuit(self, a, b, c):
        print("a", a)
        print("b", b)
        print("c", c)
        counter = 0
        for id in self.mult_gates:
            gate = self.circuit[id]
            gate.a = a[counter]
            gate.b = b[counter]
            gate.c = c[counter]
            counter = counter + 1
        config.ceps_speed.set_preprossing_circuit(self.circuit)

        #self.protocol_open.request(a, "A")
        #self.protocol_open.request(b, "B")
        #self.protocol_open.request(c, "C")


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


def print_circuit_v2(circuit):
    for gate in circuit:
        print("id", gate.id)
        print("type", gate.type)
        print("wires_in", gate.wires_in)
        print("wires_out", gate.wires_out)
        print("shares", gate.shares)
        print("output_value", gate.output_value)
        print("a", gate.a)
        print("b", gate.b)
        print("c", gate.c)
        print("r", gate.r)
        print("r_open", gate.r_open)

        print("")
    print("\n\n")
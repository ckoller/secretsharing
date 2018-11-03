from app.api.ceps_speed.open import Open

class BooleanEvaluationStrategy:
    def __init__(self, client):
        self.client = client
        self.cur_gid = 0
        self.output = []
        self.open = Open()

    def evaluate_circuit(self, circuit):
        for gate_id in range(self.cur_gid, len(circuit)):
            gate = circuit[gate_id]
            print("**************************", gate.type, gate.id, "****************************")

            if gate.type == 'input':
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'inv':
                val_in = circuit[gate.wires_in[0]].output_value
                gate.output_value = 1 - val_in
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'and' or gate.type == 'xor':
                val_in_l = circuit[gate.wires_in[0]].output_value
                val_in_r = circuit[gate.wires_in[1]].output_value
                alpha = val_in_l + gate.a
                beta = val_in_r + gate.b
                self.open.request([alpha, beta], "alpha_beta")
                break
            elif gate.type == 'output':
                prev_gate = circuit[self.cur_gid - 1]
                gate.output_value = prev_gate.output_value
                self.cur_gid = self.cur_gid + 1
                result = gate.output_value
                #Client().get_response(self.output, self.circuit, None)
                self.open.request(result, "output")
                break

    def handle_protocol_open_answer(self, answer, type, circuit):
        if type == "output":
            #("**************************", "output answer", "****************************")

            self.output.append(answer)
            if self.received_all_outputs(circuit):
                self.client.get_response(self.output, circuit, None)
                print("done")
            else:
                self.cur_gid = self.cur_gid + 1
                self.evaluate_circuit(circuit)
        elif type == "and":
            gate = circuit[self.cur_gid]
            alpha_open = answer[0]
            beta_open = answer[1]
            #("**************************", gate.c, "****************************")
            x = (alpha_open*beta_open - alpha_open*gate.b - beta_open*gate.a + gate.c)
            gate.output_value = x
            self.cur_gid = self.cur_gid + 1
            #print("**************************handle_protocol_open_answer****************************")
            self.evaluate_circuit(circuit)

    def received_all_outputs(self, circuit):
        for gate in circuit:
            if gate.type == "output":
                if gate.output_value == None:
                    return False
        return True


class ArithmeticEvaluationStrategy:
    def __init__(self, client):
        self.client = client
        self.cur_gid = 0
        self.output = []
        self.open = Open()

    def evaluate_circuit(self, circuit):
        for gate_id in range(self.cur_gid, len(circuit)):
            gate = circuit[gate_id]
            print("**************************", gate.type, gate.id, "****************************")

            if gate.type == 'input':
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'add':
                val_in_l = circuit[gate.wires_in[0]].output_value
                val_in_r = circuit[gate.wires_in[1]].output_value
                gate.output_value = val_in_l + val_in_r
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'scalar_mult':
                val_in = circuit[gate.wires_in[0]].output_value
                scalar = gate.scalar
                gate.output_value = val_in * scalar
                self.cur_gid = self.cur_gid + 1
            elif gate.type == 'mult':
                val_in_l = circuit[gate.wires_in[0]].output_value
                val_in_r = circuit[gate.wires_in[1]].output_value
                alpha = val_in_l + gate.a
                beta = val_in_r + gate.b
                self.open.request([alpha, beta], "alpha_beta")
                break
            elif gate.type == 'output':
                prev_gate = circuit[self.cur_gid - 1]
                gate.output_value = prev_gate.output_value
                self.cur_gid = self.cur_gid + 1
                result = gate.output_value
                #Client().get_response(self.output, self.circuit, None)
                self.open.request(result, "output")
                break

    def handle_protocol_open_answer(self, answer, type, circuit):
        if type == "output":
            #("**************************", "output answer", "****************************")

            self.output.append(answer)
            if self.received_all_outputs(circuit):
                self.client.get_response(self.output, circuit, None)
                print("done")
            else:
                self.cur_gid = self.cur_gid + 1
                self.evaluate_circuit(circuit)
        elif type == "alpha_beta":
            gate = circuit[self.cur_gid]
            alpha_open = answer[0]
            beta_open = answer[1]
            #("**************************", gate.c, "****************************")
            x = (alpha_open*beta_open - alpha_open*gate.b - beta_open*gate.a + gate.c)
            gate.output_value = x
            self.cur_gid = self.cur_gid + 1
            #print("**************************handle_protocol_open_answer****************************")
            self.evaluate_circuit(circuit)

    def received_all_outputs(self, circuit):
        for gate in circuit:
            if gate.type == "output":
                if gate.output_value == None:
                    return False
        return True

from app.api.ceps_speed.preprocessing import Preprocessing
import time

class Ceps_Speed:
    def __init__(self, circuit, sharingStrategy, evaluationStrategy):
        self.sharingStrategy = sharingStrategy
        self.evaluationStrategy = evaluationStrategy
        self.circuit = circuit["circuit"]
        self.preprocessing = Preprocessing(circuit, sharingStrategy)
        self.preprocessed = False
        self.my_input_values = []
        self.start = None
        self.pre_time = None


    def setup(self, circuit, my_input_values):
        self.evaluationStrategy.reset()
        self.my_input_values = my_input_values
        self.circuit = circuit["circuit"]
        self.preprocessing = Preprocessing(circuit, self.sharingStrategy)
        self.preprocessed = False
        self.start = None
        self.pre_time = None

    def run(self):
        if self.start is None:
            self.start = time.time()
        self.preprocessing.run()

    def set_preprossing_circuit(self, circuit):
        self.circuit = circuit
        self.preprocessed = True
        if self.pre_time is None:
            self.pre_time = time.time() - self.start
        self.share_my_input_value()

    def share_my_input_value(self):
        if self.received_all_input_shares():
            self.evaluate_circuit()
        self.sharingStrategy.share_my_input_value(self.circuit, self.my_input_values)


    def received_all_input_shares(self):
        return self.sharingStrategy.received_all_input_shares(self.circuit, self.preprocessed)

    def handle_input_share(self, d, gate_id):
        self.sharingStrategy.handle_input_share(d, gate_id, self.circuit)
        if self.received_all_input_shares():
            self.evaluate_circuit()

    def evaluate_circuit(self):

        self.evaluationStrategy.evaluate_circuit(self.circuit)

    def handle_protocol_open_answer(self, answer, type):
        self.evaluationStrategy.handle_protocol_open_answer(answer, type, self.circuit)
        if self.evaluationStrategy.is_done:
            self.protocol_done()

    def received_all_outputs(self):
        return self.evaluationStrategy.received_all_outputs(self.circuit)

    def protocol_done(self):
        print("done")
        total_time = time.time() - self.start
        print("W/O Pre:", total_time - self.pre_time)
        print("Total Time:", total_time)
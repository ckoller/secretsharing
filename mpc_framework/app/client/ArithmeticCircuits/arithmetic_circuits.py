from app.client.circuit import ArithmeticCircuitCreator

# Arithmetic circuit are created with the gates: add, mult and scalar_mult.
# The gates can take gates as inputs.
# c.input(3), means that we create and input gate with the id 3.

class ArithmeticCircuits:

    def add_1_mult_2_3(self):
        # fx.   8+8*8
        c = ArithmeticCircuitCreator()
        c.add(c.mult(c.input(1),c.input(2)), c.input(3))
        circuit = c.get_circuit()
        return circuit

    def mult_add_5_people_where_one_person_has_multiple_inputs(self):
        # fx.    8*8+(8+8+8)*8)
        c = ArithmeticCircuitCreator()
        c.add(c.mult(c.input(5), c.input(3)), c.mult(c.add(c.add(c.input(3), c.input(5)), c.input(1)), c.input(1)))
        circuit = c.get_circuit()
        return circuit

    def add_mult_scalarmult_where_some_player_has_no_input(self):
        # fx.   (8*8 + 8*8)*2)*2  = 256
        c = ArithmeticCircuitCreator()
        c.scalar_mult(c.add(c.mult(c.input(7), c.input(1)), c.mult(c.input(8), c.input(4))), scalar=2)

    def add_mult_scalarmult_with_multiple_outputs(self):
        c = ArithmeticCircuitCreator()
        c.mult(c.scalar_mult(c.add(c.mult(c.input(2), c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(1))
        c.output()
        c.mult(c.scalar_mult(c.add(c.mult(c.input(2), c.input(1)), c.mult(c.input(3), c.input(4))), scalar=2), c.input(1))
        circuit = c.get_circuit()


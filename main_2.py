import random as rand
import matplotlib.pyplot as plt
import qiskit

my_list = rand.sample(range(0, 10), 10)
print(my_list)


# oracle
def the_oracle(input):
    winner = 7
    if input == winner:
        return True
    else:
        return False


for index, trial_number in enumerate(my_list):
    if the_oracle(trial_number) is True:
        print(f'winner found at index {index}')
        print(f'{index + 1} call to the Oracle used')
        break

# Built-in modules
import math

# Imports from Qiskit
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, MCMT, ZGate
from qiskit.visualization import plot_distribution

# Imports from Qiskit Runtime
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session

# Add your token below
service = QiskitRuntimeService(channel="ibm_quantum")

def grover_oracle(marked_states):
    """Build a Grover oracle for multiple marked states

    Here we assume all input marked states have the same number of bits

    Parameters:
        marked_states (str or list): Marked states of oracle

    Returns:
        QuantumCircuit: Quantum circuit representing Grover oracle
    """
    if not isinstance(marked_states, list):
        marked_states = [marked_states]
    # Compute the number of qubits in circuit
    num_qubits = len(marked_states[0])

    qc = QuantumCircuit(num_qubits)
    # Mark each target state in the input list
    for target in marked_states:
        # Flip target bit-string to match Qiskit bit-ordering
        rev_target = target[::-1]
        # Find the indices of all the '0' elements in bit-string
        zero_inds = [ind for ind in range(num_qubits) if rev_target.startswith("0", ind)]
        # Add a multi-controlled Z-gate with pre- and post-applied X-gates (open-controls)
        # where the target bit-string has a '0' entry
        qc.x(zero_inds)
        qc.compose(MCMT(ZGate(), num_qubits - 1, 1), inplace=True)
        qc.x(zero_inds)
    return qc


marked_states = ["011", "100"]

oracle = grover_oracle(marked_states)
oracle.draw("mpl")

grover_op = GroverOperator(oracle)
grover_op.decompose().draw("mpl")

optimal_num_iterations = math.floor(
    math.pi / 4 * math.sqrt(2**grover_op.num_qubits / len(marked_states))
)
qc = QuantumCircuit(grover_op.num_qubits)
# Create even superposition of all basis states
qc.h(range(grover_op.num_qubits))
# Apply Grover operator the optimal number of times
qc.compose(grover_op.power(optimal_num_iterations), inplace=True)
# Measure all qubits
qc.measure_all()
qc.draw("mpl")

# Select the simulator with the fewest number of jobs in the queue
backend_simulator = service.least_busy(simulator=True, operational=True)
print(backend_simulator.name)

# Initialize your session
sim_session = Session(backend=backend_simulator)
sim_sampler = Sampler(session=sim_session)

sim_dist = sim_sampler.run(qc, shots=int(1e4)).result().quasi_dists[0]

plot_distribution(sim_dist.binary_probabilities())
plt.show()

sim_session.close()
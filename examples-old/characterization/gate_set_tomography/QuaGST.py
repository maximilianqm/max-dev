import matplotlib.pyplot as plt
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import generate_qua_script
import time
import numpy as np
from qm.qua import *
from encode_circuits import *


class QuaGST:
    def __init__(
        self,
        file: str,
        model,
        basic_gates_macros: dict,
        pre_circuit=None,
        post_circuit=None,
        N_shots: int = 1000,
        config: dict = None,
        quantum_machines_manager: QuantumMachinesManager = None,
        **execute_kwargs,
    ):
        """
        A class to generate and execute GST using Qua
        @param file: A path to a text file of circuits generated by pyGSTi
        @param model: pyGSTi model
        @param basic_gates_macros: dictionary mapping the gates to their macros. Keys are gate names without "G"
        @param pre_circuit: macro to execute before each circuit
        @param post_circuit: macro to execute after each circuit
        @param N_shots: number of short per circuit
        @param config: configuration for the quantum machine
        @param quantum_machines_manager: QuantumMachinesManager object
        @param execute_kwargs: QuantumMachine execution arguments
        """
        self.file = file
        self.model = model
        self._get_circuit_list()
        self.basic_gates_macros = basic_gates_macros
        self._get_base_sequence_macros()
        self.pre_circuit = pre_circuit
        self.post_circuit = post_circuit
        self.config = config
        self.qmm = quantum_machines_manager
        self.N_shots = N_shots
        self.execute_kwargs = execute_kwargs
        self.results = []
        self.last_job = None
        self.qua_script = []

    def _get_circuit_list(self):
        """
        Read the txt file and encode the circuit list
        @return: Encoded circuit list
        """
        with open(file=self.file, mode="r") as f:
            circuits = f.readlines()
            self.circuit_list = encode_circuits(circuits, self.model)

    def _get_base_sequence_macros(self):
        """
        Generate gate sequence list and corresponding macros
        @return:
        """
        (
            self.base_gate_sequence,
            self.base_sequence_macros,
        ) = base_gate_sequence_and_macros(self.model, self.basic_gates_macros)

    def _qua_circuit(self, encoded_circuit: list):
        """
        Generate qua code from an encoded circuit
        @param encoded_circuit: list of 4 numbers
        @return:
        """
        _n_ = declare(int)
        # prep fiducials
        with switch_(encoded_circuit[0]):
            for i, m in enumerate(self.base_sequence_macros):
                with case_(i):
                    m()
        # germ
        with switch_(encoded_circuit[2]):
            for i, m in enumerate(self.base_sequence_macros):
                with case_(i):
                    with for_(_n_, 0, _n_ < encoded_circuit[3], _n_ + 1):
                        m()
        # meas fiducials
        with switch_(encoded_circuit[1]):
            for i, m in enumerate(self.base_sequence_macros):
                with case_(i):
                    m()

    def _load_circuit_using_IO(self, qm, job):
        """
        Encode a circuit using IO variables
        @param qm: QuantumMahcine
        @param job: QmJob
        @return:
        """
        for circuit in self.circuit_list:
            for gate in range(0, len(circuit), 2):
                while not (job.is_paused()):
                    time.sleep(0.01)
                qm.set_io1_value(circuit[gate])
                qm.set_io2_value(circuit[gate + 1])
                job.resume()

    def gst_qua_IO(self, circuits: list, out_stream):
        """
        Loop over and execute the given circuits
        @param circuits: List of encoded circuits to execute
        @param out_stream: The output stream for the results
        @return:
        """
        _g_ = declare(int)
        _n_shots_ = declare(int)
        _n_circuits_ = declare(int)

        with for_(_n_circuits_, 0, _n_circuits_ < len(circuits), _n_circuits_ + 1):
            circuit = declare(int, size=len(self.circuit_list[0]))
            with for_(_g_, 0, _g_ < circuit.length(), _g_ + 2):
                """
                Get circuit from IO variables
                """
                pause()
                assign(circuit[_g_], IO1)
                assign(circuit[_g_ + 1], IO2)

            with for_(_n_shots_, 0, _n_shots_ < self.N_shots, _n_shots_ + 1):
                if self.pre_circuit:
                    self.pre_circuit()
                self._qua_circuit(circuit)
                if self.post_circuit:
                    self.post_circuit(out_stream)

    def gst_qua(self, circuits: list, out_stream):
        """
        Loop over and execute the given circuits
        @param circuits: List of encoded circuits to execute
        @param out_stream: The output stream for the results
        @return:
        """
        _n_shots_ = declare(int)
        circuit = [declare(int) for _ in range(len(self.circuit_list[0]))]
        with for_each_(circuit, circuits):
            with for_(_n_shots_, 0, _n_shots_ < self.N_shots, _n_shots_ + 1):
                if self.pre_circuit:
                    self.pre_circuit()
                self._qua_circuit(circuit)
                if self.post_circuit:
                    self.post_circuit(out_stream)

    def get_qua_program(self, gst_body, circuits: list):
        """
        Generated qua program with stream processing
        @param gst_body: qua code for executing the GST
        @param circuits: list of circuits
        @return:
        """
        with program() as gst_prog:
            out_stream = declare_stream()

            gst_body(circuits, out_stream)

            with stream_processing():
                out_stream.buffer(len(circuits), self.N_shots).save("counts")

        return gst_prog

    def run_IO(self, n_circuits: int = None):
        """
        Run the GST using IO variables
        @param n_circuits: number of circuits to run
        @return:
        """
        qm = self.qmm.open_qm(self.config)
        qua_prog = self.get_qua_program(self.gst_qua_IO, self.circuit_list[:n_circuits])
        self.qua_script = [generate_qua_script(qua_prog, self.config)]
        job = qm.execute(
            qua_prog,
            **self.execute_kwargs,
        )

        self._load_circuit_using_IO(qm, job)

        job.result_handles.wait_for_all_values()

        self.results = job.result_handles.counts.fetch_all()

    def run(self, n_circuits: int = None, plot_simulated_samples_con=None):
        """
        Run GST
        @param n_circuits: max number of circuits per program
        @return:
        """
        qm = self.qmm.open_qm(self.config)
        if n_circuits is None:
            n_circuits = len(self.circuit_list)
        for i in range(len(self.circuit_list) // n_circuits + 1):
            circuits = self.circuit_list[i * n_circuits : (i + 1) * n_circuits]
            if circuits:
                qua_prog = self.get_qua_program(self.gst_qua, np.array(circuits).T.tolist())
                self.qua_script.append(generate_qua_script(qua_prog, self.config))
                job = qm.execute(
                    qua_prog,
                    **self.execute_kwargs,
                )
                job.result_handles.wait_for_all_values()
                if plot_simulated_samples_con:
                    plt.figure()
                    job.get_simulated_samples().__getattribute__(plot_simulated_samples_con).plot()
                    plt.show()
                self.last_job = job
                self.results.append(job.result_handles.counts.fetch_all())

    def get_results(self):
        pass

    def save_results(self):
        pass

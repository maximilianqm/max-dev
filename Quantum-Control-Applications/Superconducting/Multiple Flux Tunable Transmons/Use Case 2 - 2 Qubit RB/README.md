# Two-Qubit Randomized Benchmarking

_Authors: tbd

*Important note: The code in this folder was used for running the experiment on a*
*specifically tailored setup and software environment. When adapting it to your setup, make sure to adjust the relevant functions and parameters.*
*Do not hesitate to contact your QM Customer Success Specialist!*

## Introduction
Two-Qubit Randomized Benchmarking describes a protocol that allows to experimentally quantify the performance of a quantum processor by applying sequences of randomly sampled Clifford gates and measuring the average error rate. Due to its universality it has been implemented in various qubit platforms such as trapped-ions [1], NMR [2], spin [3] and superconducting qubits [4].

[1] Knill et al (2008 Phys. Rev. A 77 012307)
[2] C A Ryan et al 2009 New J. Phys. 11 013034
[3] X. Xue et al Phys. Rev. X 9, 021011
[4] A. D. Córcoles et al Phys. Rev. A 87, 030301(R)

## Experimental Setup
The use-case in this example is tailored for a superconducting quantum processor using flux-tunable transmon qubits, where we focus on a subset of two qubits that are capacitively coupled to each other. Single qubit operations are controlled by sending microwave pulses through a xy-line that is capacitively coupled to the individual qubits. The two-qubit gate is implemented by a controlled-Z (CZ) gate utilizing the fast-flux lines to rapidly change the qubit frequencies and the capacitive coupling between both qubits. Part of the optimization protocol for tuning up a CZ gate can be found in the use-case Two-Qubit Gate Optimization.

## Prerequisites
- Calibrated Single Qubit Gates?
- Calibrated CZ Gate
- Calibrated Measurement Protocol for State Discrimination

## Implementation in QUA
The following procedure implements Two-Qubit Randomized Benchmarking with the described setup and the TwoQubitRb class. The decomposition of the two-qubit unitaries into CZ and single qubit gates is given in Ref. [1]. The circuit generation and randomization is done prior to the execution using tableaux calculation, also to find the inverse circuit.
Now it uses input stream to execute randomized circuit - future should be randomization done on FPGA - something we can benchmark
The class itself is generic for 2 QB RB and can be implemented for different architectures by replacing the native single and two-qubit gates using the generator functions.

[1] Barends, R. et al. Nature 508, 500–503 (2014)

### The TwoQubitRB Class
```python
rb = TwoQubitRb(config, single_qubit_gate_generator, two_qubit_gate_generators, prep_func, measure_func, verify_generation=True)
```

- **TwoQubitRb**: The class for generating the configuration and running two-qubit randomized benchmarking experiments with the OPX
- **config**: dict – Standard configuration “config” containing the relevant experimental details (e.g. what analog outputs are connected to the xy drive, z flux line, etc.).
- **single_qubit_gate_generator**: A callable used to generate a generic (baked) single qubit gate using a signature similar to phasedXZ
- **two_qubit_gate_generators**: Mapping two qubit gate names to callables used to generate the (baked) gates (needs at least one two-qubit gate). Can contain all two-qubit gates implemented by the user.
- **prep_func**: Callable used to reset the qubits to the |00> state. This function does not use the baking object, and is a proper QUA code macro (e.g. wait() statement or active reset protocol).
- **measure_func**: A callable used to measure the qubits. This function does not use the baking object, and is a proper QUA code macro. Returns a tuple containing the measured values of the two qubits as QUA expressions. The expression must evaluate to a Boolean value. False means |0>, True means |1>. The most significant bit (MSB) is the first qubit. 
verify_generation: bool = False

### Run the 2 QB RB 
The experiment is run by calling the run method of the previously generated program rb.

```python
qmm = QuantumMachinesManager('127.0.0.1',8080)
res = rb.run(qmm, circuit_depths=[1, 2, 3, 4, 5], num_circuits_per_depth=50, num_shots_per_circuit=1000)
```

For running the experiment the user has to specify the following arguments:
- **qmm**: The quantum machine manager instance, on which the 2-Qubit-RB will be executed on.
- **circuit_depths**: Number of consecutive clifford gates (layers) per sequence (not including the inverse, more info on depth: https://qiskit.org/documentation/apidoc/circuit.html).
- **num_circuits_per_depth**: The amount of different circuit randomizations (combination of Cliffords) in each sequence. 
- **num_shots_per_circuit**: The number of repetitions of the same circuit of a depth, e.g. used for averaging.

### Gate Definition
Gate generation is performed using the Baking class. This class adds to QUA the ability to generate arbitrary waveforms ("baked waveforms") using syntax similar to QUA. 
#### single_qubit_gate_generator
```python
def bake_phased_xz(baker: Baking, q, x, z, a):
    element = f"qubit{q}_xy"
    baker.frame_rotation_2pi(-a, element)
    baker.play("x$drag", element, amp=x)
    baker.frame_rotation_2pi(a + z, element)
```
single_qubit_gate_generator: A callable used to generate a single qubit gate using a signature similar to `phasedXZ`.
Callable arguments:  
- **baking**: The baking object. 
- **qubit**: The qubit number. 
- **x**: The x rotation exponent. 
- **z**: The z rotation exponent. 
- **a**: the axis phase exponent. 
 
#### two_qubit_gate_generators
```python
qubit1_frame_update = 0.23  # example, should be taken from QPU parameters
qubit2_frame_update = 0.12  # example, should be taken from QPU parameters
def bake_cz(baker: Baking, q1, q2):
    q1_xy_element = f"qubit{q1}_xy"
    q2_xy_element = f"qubit{q2}_xy"
    q2_z_element = f"qubit{q2}_z"
   
    baker.play("cz_qubit1_qubit0$rect", q2_z_element)
    baker.align()
    baker.frame_rotation_2pi(qubit1_frame_update, q2_xy_element)
    baker.frame_rotation_2pi(qubit2_frame_update, q1_xy_element)
    baker.align()
```
Mapping one or more two qubit gate names to callables used to generate those gates.
Callable arguments: 
- **baking**: The baking object. 
- **qubit1**: The first qubit number. 
- **qubit2**: The second qubit number. 

### State Preparation
```python
def prep():
    wait(10000)  # thermal preparation
    align()
```
This example of the state preparation simply uses a thermal reset using the QUA wait() command. It is executed between sequences to ensure that the initial state of the qubit pair is |00>. More advanced preparation protocols (e.g. active reset) can be implemented in this macro.


### Measurement

```python
def meas():
    rr0_name = f"qubit0_rr"
    rr1_name = f"qubit1_rr"
    Iq0 = declare(fixed)
    Qq0 = declare(fixed)


    Iq1 = declare(fixed)
    Qq1 = declare(fixed)
   
    measure("readout$rect$rotation", rr0_name, None,
            dual_demod.full("w1", "out1", "w2", "out2", Iq0),
            dual_demod.full("w3", "out1", "w1", "out2", Qq0)
            )
    measure("readout$rect$rotation", rr1_name, None,
            dual_demod.full("w1", "out1", "w2", "out2", Iq1),
            dual_demod.full("w3", "out1", "w1", "out2", Qq1)
            )

    return Iq0 > 0, Iq1 > 0  # example, should be taken from QPU parameters
```    
**measure_func**: A callable used to measure the qubits. This function does not use the baking object, and is a proper QUA code macro. 
Returns a tuple containing the measured values of the two qubits as Qua expressions. The expression must evaluate to a Boolean value. False means |0>, True means |1>. The MSB is the first qubit. 

### Results
Plot fidelity as function of depth and plot histograms for each depth
































The goal of this use-case is threefold:
1. Implement Cryoscope [[1](#1), [2](#2)] to measure the step response of the flux line
2. Design suitable IIR and FIR filters to correct for distortion occurring along the flux line
3. Perform two qubit SWAP spectroscopy without and with pre-distortion filters to characterize the corrections.



## 1. Experimental set-up and required calibrations

<img align="right" src="setup.PNG" alt="drawing" width="400"/>

### 1.1 Experimental set-up
The chip contains 5 2D-transmons, where some of them have nearest-neighbor connectivity, 
with flux tunable lines.

The experimental setup specific to this experiment consists of two flux tunable transmons (with a SQUID loop as nonlinear inductor and a flux line next to it) coupled to readout resonators located on a common transmission line.
The general scheme is represented on the figure on the right.

The qubits are controlled with IQ signals generated by the OPX and up-converted with an external local oscillator using calibrated IQ mixers.

The readout resonators are pumped with an intermediate frequency generated by the OPX and up-converted with another external local oscillator using an IQ mixer.
The transmitted signal is measured by the OPX after down-conversion with an IQ mixer and the local oscillator signal.

The flux lines are controlled by two additional analog outputs of the OPX.

In principle, the program detailed below can be easily modified if a different set-up is to be used.

### 1.2 Calibration steps prior to Cryoscope and two-qubit SWAP spectroscopy

Before running Cryoscope, several calibration steps are required.

* The first calibration to run is the 2D readout resonator spectroscopy (flux amplitude and readout frequency). This spectroscopy will show the resonator frequency as a function of flux biasing, the qubit flux insensitive point (qubit frequency independent of flux bias), the qubit zero-frequency point, and the avoided crossing when the qubit and resonator have the same frequency. For Cryoscope, we want to set the flux line to the qubit flux insensitive point and bias it around $\phi_0/4$ during the sequence.   
* The second important quantity to calibrate is the $\pi/2$ pulse. This can be done using a simple Rabi sequence where both the pulse amplitude and frequency are scanned while the flux bias is set to the qubit flux insensitive point found previously.
* (optional) If the qubit pulses are relatively short (< 100ns), then the use of optimal DRAG waveforms can enhance the fidelity of the gates [[3]](#3). 
* The last calibration to perform is the qubit detuning versus flux bias. This will be used to validate the qubit flux insensitive point and the avoided level crossing, as well as the Cryoscope measurement. The sequence can be found in the [Cryoscope use-case](#2).

## 2. [The configuration](configuration.py)

### 2.1 The elements
The configuration consists of 3 elements:
* `qubit0` and `qubit1` send control pulses to each transmon
* `resonator0` and `resonator1` send pump pulses and measures the transmitted signal for each qubit
* `flux_line0` and `flux_line1` send control pulses and DC voltage to the flux line of each qubit


### 2.2 The operations, pulse and waveforms
The qubits elements `qubit0` and `qubit1` have several operations defined that correspond to X/2, Y/2, X and Y gates.

Since a $\pi$-pulse is 100ns long for `qubit1`, it uses a simple cosine envelop.
On the other hand, since a $\pi$-pulse is 16ns long for `qubit0`, an optimized cosine DRAG waveform [[3]](#3) is used to generate its gates.


The `resonator` has just one readout operation defined as a constant amplitude pulse

The flux line elements `flux_line0` and `flux_line1` have a single biasing operation consisting of a square pulse added on top of a DC offset set to the flux soft spot.

## 3. The QUA program and data processing
The QUA program consists of three distinct parts:
1. Measuring the flux line step response by implementing cryoscope.
2. From this step response, derive the IIR and FIR filters to compensate for the distorted flux pulse.
3. Characterize the corrections by implementing a two qubit SWAP spectroscopy from which the CZ gate can be calibrated.

### 3.1 [Cryoscope](cryoscope.py)

 The idea of the method is to measure the step response of the flux line using the qubit phase measured in a Ramsey-like experiment [[1]](#1). 
 The possibly distorted response can then be pre-corrected by designing suitable IIR and FIR filters.

This experiment and implementation in QUA has already been documented in the following [use-case](#2).
The main difference here is that a constant amplitude flux pulse has been used to measure the step response of the flux line.


### 3.2 [IIR and FIR filter implementation](cryoscope.py)

The method used to design the filters is to fit the flux step response with one or several exponential decay functions 
and use analytical formulas to derive the corresponding FIR and IIR taps. 
This exponential behaviour is characteristic of the effect of a bias-T on the flux line.

These functions can be found in [filter_functions.py](filter_functions.py) and their usage is shown in the snippet below.

```python
import scipy.optimize
from filter_functions import expdecay, filter_calc
## Fit step response with exponential
[A_exp, tau_exp], _ = scipy.optimize.curve_fit(expdecay, xplot, step_response)
print(f"A: {A_exp}\ntau: {tau_exp}")

## Derive IIR and FIR corrections
fir, iir = filter_calc(exponential=[(A, tau)])
print(f"FIR: {fir}\nIIR: {iir}")
```
Once the filter parameters have been found, the configuration needs to be updated accordingly.
An example is shown on the snippet below 
and more details about the implementation of FIR and IIR filters in QUA can be found [here](https://qm-docs.qualang.io/guides/output_filter#id1).
```python
"controllers": {
    "con1": {
        "analog_outputs": {
            1: {"offset": -0.0102 * 1}, # q0 I
            2: {"offset": 0.0316 * 1},  # q0 Q
            3: {"offset": 0.0},  # q1 I
            4: {"offset": 0.0},  # q1 Q
            5: {"offset": 0.0},  # resonators I
            6: {"offset": 0.0},  # resonators Q
            7: {"offset": offset7, "filter": {"feedforward": fir, "feedback": iir}},   # qo flux line
            8: {"offset": offset8, "filter": {"feedforward": fir1, "feedback": iir1}}, # q1 flux line
        },
    },
},
```
The figure below shows the results of the filter implementation.
The top-left figure represents the step response of the flux line and the corresponding exponential fit.

The top-right figure shows the experimental data in blue together with the ideal response (green) and the theoretical response without (orange) and with (red) filters calculated from Scipy.
The calculated taps are also displayed.

The bottom-left plot is the normalized flux pulse without and with filter and the bottom-right figure is a zoom with the $\pm$ 1% region.

![results](Pulse_response.png)


### 3.3 [Two qubit SWAP spectroscopy](CZ02_11.py)

In order to characterize the quality of the corrections, a two qubit SWAP spectroscopy is implemented.
It consists of four steps:
1. Prepare the qubits in the ground state.
2. Excite the two qubits by applying an X gate to both, in order to put the system in the |11> state.
3. Apply a flux pulse to qubit 1 with varying amplitude and duration. The goal of this pulse is to tune |11> to resonance with |02> similarly to the implementation of a CZ gate.
4. Measure the state of qubit 0 using single-shot readout.

The corresponding QUA code is shown in the snippet below.

```python
# Outer loop for averaging
with for_(n, 0, n < n_avg, n + 1):
    # Flux pulse amplitude scan
    with for_(*from_array(a, amps)):
        # FLux pulse duration scan
        with for_(segment, 0, segment <= const_flux_len, segment + 1):
            # Cooldown to have the qubit in the ground state
            wait(cooldown_time)
            # CZ 02-11 protocol
            # Play pi on both qubits
            play("x180", "qubit0")
            play("x180", "qubit1")
            # global align
            align()
            # Wait some additional time to be sure that the pulses don't overlap
            wait(20)
            # Play flux pulse with 1ns resolution
            with switch_(segment):
                for j in range(0, const_flux_len + 1):
                    with case_(j):
                        square_pulse_segments[j].run(amp_array=[("flux_line1", a)])
            # global align
            align()
            # Wait some additional time to be sure that the pulses don't overlap
            wait(20)
            # q0 state readout
            measure(
                "readout",
                "resonator0",
                None,
                dual_demod.full("rotated_cos", "out1", "rotated_sin", "out2", I),
                dual_demod.full("rotated_minus_sin", "out1", "rotated_cos", "out2", Q),
            )
            save(I, I_st)
            save(Q, Q_st)
            # State discrimination
            assign(state, I > ge_threshold)
            save(state, state_st)
```
The state of qubit 0 is displayed below as a function of the flux pulse amplitude and duration without and with filters.

|   Chevron without filter    |      Chevron with filters       |
|:---------------------------:|:-------------------------------:|
| ![results](CZ_nofilter.png) | ![results](CZ_with_filter.png)  |

As explained in [[1]](#1), the finite rise time of the flux pulse without filter is responsible for the bending of the fringes toward larger amplitudes for short pulses and the asymmetric pattern visible on the left picture.

The absence of these two features on the right picture shows the validity of the filter implementation based on Cryoscope.
## References

<a id="1">[1]</a> M. A. Rol1,  L. Ciorciaro1, F. K. Malinowski1, B. M. Tarasinski1, R. E. Sagastizabal1, C. C. Bultink1, Y. Salathe, N. Haandbaek, J. Sedivy, and L. DiCarlo1. Time-domain characterization and correction of on-chip distortion of control pulses in a quantum processor. Appl. Phys. Lett. 116, 054001 (2020). https://doi.org/10.1063/1.5133894

<a id="2">[2]</a> [Cryoscope with QUA use-case.](https://github.com/qua-platform/qua-libs/tree/main/Quantum-Control-Applications/Superconducting/Single%20Flux%20Tunable%20Transmon/Use%20Case%201%20-%20Paraoanu%20Lab%20-%20Cryoscope#cryoscope)

<a id="3">[3]</a> [DRAG pulse optimization with QUA use-case.](https://github.com/qua-platform/qua-libs/tree/main/Quantum-Control-Applications/Superconducting/Single%20Flux%20Tunable%20Transmon/Use%20Case%202%20-%20DRAG%20coefficient%20calibration)

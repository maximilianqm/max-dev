---
id: index
title: State tomography
sidebar_label: State tomography
slug: ./
---

This program showcases the possibility to use a QUA program and the OPX to perform a single qubit state tomography experiment.

# Introduction
Quantum state tomography is the attempt to discover the quantum-mechanical state of a physical system, or more precisely, of a finite set of systems prepared by the same process. The experimenter acquires a set of measurements of different non-commuting observables and tries to estimate what the density matrix of the systems must have been before the measurements were made, with the goal of being able to predict the statistics of future measurements generated by the same process. In this sense, quantum state tomography characterizes a state preparation process that is assumed to be stable over time.

Source : Schmied, Roman. ”Quantum state tomography of a single qubit: comparison of methods.” Journal of Modern Optics 63.18 (2016): 1744-1758. https://arxiv.org/abs/1407.4759

# Theoretical reminder
The state of quantum bit can be written with the following density matrix : 
$$\hat{\rho}=\frac{1}{2}(\mathbb{1}+x\hat{\sigma}_x+y\hat{\sigma}_y+z\hat{\sigma}_z)=\frac{1}{2}( \mathbb{1}+\bold{r.\hat{\sigma}})$$
with $$\bold{r}$$ being called the Bloch vector and is such that $$||\bold{r}||\leq 1$$. Here $$\hat{\sigma}$$ is a vector with components ($$\hat{\sigma}_x,\hat{\sigma}_y,\hat{\sigma}_z)$$

We also define $$\hat{\sigma}_{\bold{n}}=\bold{n}.\hat{\sigma}$$ and recall that  $$\langle \hat{\sigma}_{\bold{n}}\rangle=$$ Tr($$\hat{\rho}\hat{\sigma}_{\bold{n}})=\bold{n.r}$$.
This implies that we have that $$\langle\hat{\sigma}_x\rangle=x$$, $$\langle\hat{\sigma}_y\rangle=y$$ and $$\langle\hat{\sigma}_z\rangle=z$$.

The idea behind qubit state tomography is to find a way to recover the Bloch vector. 
There exist a bunch of methods to do so, we present here two of them : direct inversion and Bayesian mean estimate.
# Direct inversion method

The direct inversion method is the simplest one to derive, and this is because its main hypothesis is the assumption of the equality between the quantum mechanical average introduced above and the statistical empirical mean deduced from actual sampling.
Recalling that from an arbitrary qubit state $$|\psi\rangle=\alpha|0\rangle+\beta|1\rangle$$, we have that $$\langle\hat{\sigma}_z\rangle=|\alpha|^2-|\beta|^2$$. Based on the hypothesis above, it is therefore enough to measure the state $$|\psi\rangle$$ in the computational basis $$N$$ times ($$N$$ being sufficiently large to build relying statistics) and to estimate the quantum average of the operator by computing : 
$$\langle\langle\hat{\sigma}_z\rangle\rangle=\frac{N_{|0\rangle}-N_{|1\rangle}}{N}$$ with $$N_{|0\rangle}$$ and $$N_{|1\rangle}$$ being the number of sampled $$0$$ and $$1$$ states respectively.

For the Pauli-Y and Pauli-X operators, one can proceed in a similar manner by applying an additional unitary transformation on the qubit state before measuring it and computing their expectation values like the Pauli-Z.
We have that : 
$$\langle\hat{\sigma}_x\rangle=\langle\psi|\hat{\sigma}_x|\psi\rangle=\langle\psi|H\hat{\sigma}_zH|\psi\rangle\equiv\langle\psi'|\hat{\sigma}_z|\psi'\rangle$$,
with $$H=\frac{1}{\sqrt{2}}\begin{pmatrix}1 & 1\\ 1 & -1\end{pmatrix}$$ being the Hadamard gate, and $$|\psi'\rangle\equiv H|\psi\rangle$$.
A similar reasoning can be done with $$\hat{\sigma}_y$$ by replacing the Hadamard transformation above by the operator $$SH$$, with $$S=\sqrt{\hat{\sigma}_z}=\begin{pmatrix}1 & 0\\ 0 & i\end{pmatrix}=\begin{pmatrix}1 & 0\\ 0 & e^{i\pi/2}\end{pmatrix}$$.

Once we have proceeded to these measurements, we can therefore reconstruct the Bloch vector using the result of the previous part.
Finally we have :
$$\bold{r}=(\frac{N_{|0\rangle_x}-N_{|1\rangle_x}}{N_x},\frac{N_{|0\rangle_y}-N_{|1\rangle_y}}{N_y},\frac{N_{|0\rangle_z}-N_{|1\rangle_z}}{N_z})$$.
 The advantage of this method is undeniably its simplicity. However, one main drawback is the fact that due to statistical noise related to sampling, it is sometimes possible to have reconstructed Bloch vectors which are not physically valid for the density matrix to be corresponding to a valid quantum state.

# Bayesian mean estimation
This method provides an alternative to the problem related to the physicality of the reconstructed density matrix raised by the direct inversion process.
The idea here is to construct a likelihood function which is interpreted as a density in the state space (i.e the Bloch sphere), and use it to calculate a weighted mean state. The Bayesian mean estimate of the Bloch vector can be written as :
$$\bold{r}_{BME}=\frac{\displaystyle\int_{BS}\bold{r}\mathcal{L}(\bold{r})d^3\bold{r}}{\displaystyle\int_{BS}\mathcal{L}(\bold{r})d^3\bold{r}}$$

Given a set of experimental measurements ($$N_{|0\rangle_x},N_{|1\rangle_x},N_{|0\rangle_y},N_{|1\rangle_y},N_{|0\rangle_z},N_{|1\rangle_z}$$), Bayes' theorem tell us that the likelihood that a certain density matrix $$\hat{\rho}=\frac{1}{2}( \mathbb{1}+\bold{r.\hat{\sigma}})$$ was related to the generation of this data is : 
$$\mathcal{L}(\hat{\rho}|N_{|0\rangle_x},N_{|1\rangle_x},N_{|0\rangle_y},N_{|1\rangle_y},N_{|0\rangle_z},N_{|1\rangle_z})\propto \mathcal{C}(\hat{\rho})\times\mathcal{P}(N_{|0\rangle_x},N_{|1\rangle_x},N_{|0\rangle_y},N_{|1\rangle_y},N_{|0\rangle_z},N_{|1\rangle_z}|\hat{\rho})$$

where $$\mathcal{C}(\hat{\rho})$$ is a prior density in the space of density matrices, vanishing whenever $$||\bold{r}||>1$$. In this example, we consider a uniform distribution.
The probability distribution $$\mathcal{P}$$ is simply the probability of obtaining the experimental data conditioned on having an initial density matrix $$\hat{\rho}$$. One can convince himself pretty easily that this distribution is a product of three binomial schemes (one for each axis) with parameters ($$N_{\alpha},\frac{1+\alpha}{2})$$, with $$\alpha=x,y,z$$. 
More specifically we have :
$$\mathcal{P}(N_{|0\rangle_x},N_{|1\rangle_x},N_{|0\rangle_y},N_{|1\rangle_y},N_{|0\rangle_z},N_{|1\rangle_z}|\hat{\rho})={N_x\choose N_{|0\rangle x}}(\frac{1+x}{2})^{N_{|0\rangle x}}(\frac{1-x}{2})^{N_{|1\rangle x}}
\times{N_y\choose N_{|0\rangle y}}(\frac{1+y}{2})^{N_{|0\rangle y}}(\frac{1-y}{2})^{N_{|1\rangle y}}\times{N_z\choose N_{|0\rangle z}}(\frac{1+z}{2})^{N_{|0\rangle z}}(\frac{1-z}{2})^{N_{|1\rangle z}}$$
with $$N_\alpha=N_{|0\rangle \alpha}+N_{|1\rangle \alpha}$$.

The calculation of the integral for obtaining the Bloch vector can then be done numerically by using, for example Monte Carlo integration (https://en.wikipedia.org/wiki/Monte_Carlo_integration).



# The QUA program
### The configuration file

The configuration file is architectured around the following items :

- controllers :
We define the outputs and inputs of the OPX device, which will be of use for the experiment. In this case, we have two analog outputs for the qubit, and two others for its coupled readout resonator. We add an analog input which is the channel where will be sampled out the analog results of the readout operation.
- elements :
This defines the set of essential components of the quantum system interacting with the OPX. In this case, the two elements are the qubit and the coupled readout resonator. 
Here are specified the main characteristics of the element, such as its resonant frequency, its associated operations (i.e the operations the OPX can apply on the element).
- pulses : 
A description of the doable pulses introduced in the elements. Here is provided a description of the default pulse duration (length parameter), the associated waveform (which can be taken from an arbitrary array), the type of operation (e.g control or measurement)
- waveforms : 
Specification of the pulse shape based on pre-built arrays (either by the user in case the shape is arbitrary, or constant pulse otherwise)
- Integration weights :
Describe the demodulation process of the data 


## The QUA program
Around the program are shown few built-in Python functions acting as macros commands for QUA. Those functions are meant to allow flexibility in the definition of the pulse implementation of the state we want to prepare (there might be a need to add pulses types in the configuration file), and the way to implement the Hadamard gate, which can be hardware dependent. There is also a post processing function named state_estimation where the determination of obtaining the 0 or 1 state should be defined according to the value of the point obtained in the IQ plane by the demodulation process.
The program itself consists in doing 3 times (one for each axis of the Bloch sphere) the same scheme within a QUA for_ loop (indicating the number of samples we want to get for each direction):
- Generate the arbitrary state calling the "Arbitrary_state_generation" function
- Proceed to necessary unitary transformations depending on the axis chosen and perform the measurement
- Save results in the stream variables defined in the beginning of the program
- use a wait command to let the state reset to the $$|0\rangle$$ state for repeating the same experiment (we assume we know the relaxation time $$T_1$$)

```python
with for_(j, 0, j < N_shots, j + 1):
         # Generate an arbitrary quantum state, e.g fully superposed state |+>=(|0>+|1>)/sqrt(2)
         Arbitrary_state_generation("qubit")
         # Begin tomography_process
         # Start with Pauli-Z expectation value determination : getting statistics of state measurement is enough to calculate it
         measure("meas_pulse", "RR", None, ("integW1", Iz), ("integW2", Qz))
         save(Iz, stream_Iz)  # Save the results
         save(Qz, stream_Qz)
         state_saving(Iz, Qz, Z, stream_Z)
         wait(t1, "qubit")  # Wait for relaxation of the qubit after the collapse of the wavefunction in case of collapsing into |1> state

         # Repeat sequence for X axis
         # Generate an arbitrary quantum state, e.g fully superposed state |+>=(|0>+|1>)/sqrt(2)
         Arbitrary_state_generation("qubit")
         # Begin tomography_process
         # Determine here Pauli X-expectation value, which corresponds to applying a Hadamard gate before measurement (unitary transformation)
         Hadamard("qubit")
         measure("meas_pulse", "RR", "samples", ("integW1", Ix), ("integW2", Qx))
         save(Ix, stream_Ix)  # Save the results
         save(Qx, stream_Qx)
         state_saving(Ix, Qx, X, stream_X)
         wait(t1, "qubit")  # Wait for relaxation of the qubit after the collapse of the wavefunction in case of collapsing into |1> state
         # Could also do active reset

         # Repeat for Y axis
         # Generate an arbitrary quantum state, e.g fully superposed state |+>=(|0>+|1>)/sqrt(2)
         Arbitrary_state_generation("qubit")
         # Begin tomography_process
         # Determine here Pauli Y-expectation value, which corresponds to applying a Hadamard gate then S-gate before measurement (unitary transformation)
         Hadamard("qubit")
         frame_rotation(np.pi / 2, "qubit")  # S-gate
         measure("meas_pulse", "RR", "samples", ("integW1", Iy), ("integW2", Qy))
         save(Iy, stream_Iy)  # Save the results
         save(Qy, stream_Qy)
         state_saving(Iy, Qy, Y, stream_Y)
         wait(t1, "qubit")  # Wait for relaxation of the qubit after the collapse of the wavefunction in case of collapsing into |1> state
```
Once this is done, the program is simulated using the LoopbackInterface and the retrieval of the data is possible.
We then use the state discrimination function to decide what measurement we obtained based on the IQ values obtained.
Finally, we reconstruct the Bloch vector using the two methods presented above.

The function "is_physical()" simply returns a Boolean checking if the Bloch vector reconstructed yields a valid quantum state or not.


## Script


[download script](Qubit_state_tomography.py)

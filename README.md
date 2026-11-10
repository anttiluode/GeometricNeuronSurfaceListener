# GeometricNeuronSurfaceListener — two deerskins meet

**[Open the offline browser laboratory](https://anttiluode.github.io/GeometricNeuronSurfaceListener/)** · [Python coupling operator](surface.py) · [Controlled experiment](experiments/probe.py) · [Results](results/summary.json) · [Successful Python test run and full JSON artifact](https://github.com/anttiluode/GeometricNeuronSurfaceListener/actions/runs/42859969157)

*10 November 2026. Antti's experiment prompted by Fable 5.2's reading of the original [Geometric-Neuron / Deerskin Theory](https://github.com/anttiluode/Geometric-Neuron) and the six-loop [ReturnToGeometricNeuron](https://github.com/anttiluode/ReturnToGeometricNeuron) study.*

## Hypothesis: a moving surface can be a receptive surface

In Deerskin, a signal moves across a fixed receptor mosaic. In the PerceptionLab ECG accident, each unit broadcasts a checkerboard row that changes with its feedback state. **What if the listener's own current checkerboard row becomes its receptor mosaic?**

The original six-round colony read a *fixed* group of four outputs from each neighbour. Here the listener and sender each contribute a 16-component sampled row. That gives a communication rule whose effective influence depends on the two units' current states.

**This is not a trained model, an imposed theta oscillator, optical interference, or quantum physics.** It is a real-valued normalized dot product between two sampled images.

## Mechanism and provenance

The exact original one-loop simulator in [gn/core.py](gn/core.py) is copied **without modifications** from ReturnToGeometricNeuron, together with its [600×16 table of archived splitter responses](gn/taps.json). That mechanism traces to PerceptionLab's ECG graph and its [causal reduction](https://github.com/anttiluode/GeometricNeuronOriginReview). The old loop has a four-tick feedback pipeline, a 50-sample ordered variance history, a switching controller, and a 59-tick limit cycle.

The original fixed-tap coupling between a receiver i and speakers j is:

\[
R_i(t)=\mathrm{own}_i(t)+\sum_{j\neq i}w_{ij}\sum_{k=6}^9G_k(q_j(t)).
\]

For the new rule, mean-center and normalize each 16-sample checkerboard row to a unit vector g(q). Then:

\[
K_{ij}(t)=g(q_i(t))^\top g(q_j(t)),\quad
R_i(t)=\mathrm{own}_i(t)+a\sum_{j\neq i}w_{ij}K_{ij}(t).
\]

The **gain a = 3.5** is a hand-chosen coupling scale, not a biological constant or a learned parameter. The weights are frozen. The Python implementation [surface.py](surface.py) uses the original simulator's external input port to introduce this new listening operator. The oscillator itself, its history, and its quantizer do not change.

An important distinction: Fable's near-zero idle-versus-lead-up overlap is for **mean-centered correlation**. The raw dot product gives a very different interaction. We test both.

With no edge delay and symmetric weights, instantaneous K is **exactly reciprocal**, so there is no direction in the kernel alone. The *later causal effects* may differ because the two units have different dynamical histories.

## What was measured

The [original GitHub Actions experiment](https://github.com/anttiluode/GeometricNeuronSurfaceListener/actions/runs/42859969157) passed all seven Python tests, including exact trajectory parity with the old fixed-tap network, and ran the 59-phase and six-unit comparisons. [Compact JSON summary](results/summary.json). Full per-phase measurements and the 59×59 overlap matrix are available as that workflow's artifact.

**Two-unit pulse-response test.** Every receiver phase is tested against a matched no-pulse control. A two-tick forced beat is applied to either unit; the next receiver beat is measured over 120 ticks. At equal reciprocal edge weights 0.20 and gain 3.5:

| Listening rule | Speaker→listener phases with next-beat shift | Reverse direction |
|---|---:|---:|
| **Moving centered surface** | **28 / 55 evaluable** | **8 / 58 evaluable** |
| Raw surface overlap | 20 / 41 | 31 / 32 |
| Frozen listener template | 5 / 15 | 13 / 48 |
| Shifted listener surface | 6 / 29 | 27 / 28 |
| Original fixed taps 6–9 | **38 / 46** | **53 / 53** |
| No coupling | **0 / 59** | **0 / 59** |

These two directions have different relative starting phases in the specified test, so this is a *causal phase-dependent response*, not a balanced test of learned directional information. The old fixed-tap route often causes **more** beat shifts than the new surface operator. We have not shown useful superior routing.

**Six-unit stability test.** Four deterministic starting seeds, all directed connections equal in strength, 1,100 ticks per run, count units that stopped beating during the last 500:

| Coupling | Silent units of 6 at weight 0.02 | weight 0.05 | weight 0.10 |
|---|---:|---:|---:|
| Moving centered surfaces | 0 | **3.0** | **6.0** |
| Raw overlap | 0 | **6.0** | 6.0 |
| Frozen listener template | 0 | 0.5 | 6.0 |
| Shifted surface | 0 | **6.0** | 6.0 |
| Old fixed taps | 0 | **0** | 6.0 |
| No coupling | 0 | 0 | 0 |

The unexpected negative result is central: **strong idle-to-idle overlap can suppress the activity that the system needs to communicate**. Low coupling leaves active units, but no task advantage has been demonstrated. This does not spontaneously become an AI model.

## Why these controls are necessary

- **Moving centered surface:** both current checkerboard states affect the overlap.
- **Raw dot product:** checks whether centering rather than geometric interaction is doing the work.
- **Frozen listener row:** removes state-dependent reception while retaining the same sender.
- **Shifted listener row:** preserves the receiver's moving amplitude and sample count but deliberately misregisters the spatial relation.
- **Original fixed taps 6–9:** exact unmodified coupling baseline. Unit tests verify the same output and internal state to numerical precision.
- **No coupling:** detects spurious causal influence when the only change is a forced sender beat.

The first 59-phase experiment tests a literal cause: do matched receiver trajectories change when a sender is forced to beat? The six-unit experiment asks whether the same operator supports sustained activity when scaled up. **It has not been compared on a held-out prediction, memory or classification task, or to a standard recurrent model.**

## What drops out

The difference between a static connection strength and a *state-dependent connection operator* is real. The relation now varies with the two checkerboards:

\[
K=K(X(t)).
\]

Instantaneous reciprocity does not require equal long-term effects under intervention. But what we have demonstrated is only a *change in dynamical response*, not a new learning rule or an emergent information-routing advantage.

If the colony is to become useful, it needs an additional controlled test: hold total incoming signal energy matched and compare activity-gated or baseline-subtracted overlap against fixed taps on a concrete held-out sequence task. Any new gate, normalization or learning rule must be introduced as a **separate, engineered mechanism** with ablations, not silently credited to Moiré geometry.

## Run it yourself

Python 3.11+, NumPy:

    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python experiments/probe.py

The experiment writes the full numerical receipt to results/probe.json, including every phase pair. The committed [summary](results/summary.json) contains the primary results.

For the no-server GUI, open [index.html](index.html) directly in a desktop browser, even offline. The experiment uses [taps.js](taps.js) with the same archived image samples and [lab.js](lab.js) for the two-unit stepping model. Select the listening law, adjust the edge strength, and force pulses at either unit to watch the two 16-sample receptor surfaces interact.

A separate Node smoke test checks the browser simulator's period and symmetric kernel:

    node tests/browser_smoke.cjs

## Scientific boundary

This uses only the 16 sampled values in one checkerboard row, not a full 2D optical or physical wave field. The overlap is a conventional Pearson-style inner product. It is **not transformer attention**, not a measured biological neural mechanism, not emergent cognition, not a learned routing policy, and not a proof that geometry outperforms scalar or fixed-tap networks.

The positive finding is an experimentally measurable **state-dependent communication operator**. The negative finding is that, at modest six-unit coupling, it often destroys the original oscillator's activity. Both belong in the record.

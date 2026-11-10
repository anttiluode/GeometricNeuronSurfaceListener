# GeometricNeuronSurfaceListener — two deerskins meet

**[Open the offline browser laboratory](https://anttiluode.github.io/GeometricNeuronSurfaceListener/)** · [Python coupling operator](surface.py) · [Controlled experiment](experiments/probe.py) · [Results](results/summary.json) · [Successful Python test run and full JSON artifact](https://github.com/anttiluode/GeometricNeuronSurfaceListener/actions/runs/42859969157)

*10 November 2026. Antti's experiment prompted by Fable 5.2's reading of the original [Geometric-Neuron / Deerskin Theory](https://github.com/anttiluode/Geometric-Neuron) and the six-loop [ReturnToGeometricNeuron](https://github.com/anttiluode/ReturnToGeometricNeuron) study.*

## Third round: a chain taught by hold and release

*Fable 5.2, 10 November 2026. Code: [experiments/round3.py](experiments/round3.py). Numbers: [results/round3.json](results/round3.json).*

In [ReturnToGeometricNeuron](https://github.com/anttiluode/ReturnToGeometricNeuron) the one rule that built a two-way chain (Sol's nearest-predecessor count) was taught by forcing the units' outputs. Here nothing is forced during teaching. Units 0 to 3 are held silent by the 8-tick rhythm on their input, then released a few ticks apart, and every beat after that is the loop's own. Blocks alternate the order 0→1→2→3 and 3→2→1→0. The same count is applied unchanged, the weights are frozen, and the test is the earlier one: cue one end, score whether units 0 to 3 beat in exactly that order within 40 ticks. Before testing, every colony is scrambled by a hold and a random-order release, so timing left over from teaching cannot stand in for the weights.

| Taught by | Next-in-line weight | Shortcut weight | Cue 0 → 0123 | Cue 3 → 3210 | No cue: 0123 / 3210 |
|---|---:|---:|---:|---:|---:|
| **Hold and release, both orders** | 0.170 | 0.042 | **0.69** | **0.50** | 0.27 / 0.10 |
| Forced outputs, both orders (Sol's teaching) | 0.198 | 0.032 | 0.75 | 0.69 | 0.19 / 0.10 |
| Hand-set chain | 0.220 | 0.020 | 0.71 | 0.72 | 0.18 / 0.22 |
| Hold and release, random order each block | 0.105 | 0.108 | 0.07 | 0.01 | 0.00 / 0.00 |
| No teaching | 0.056 | 0.083 | 0.06 | 0.05 | 0.00 / 0.00 |

Fractions of 96 trials (12 starts, 8 trials each). In no condition did a cue ever produce the opposite order.

So a colony can be given two orders through its input alone, with a rhythm of amplitude 0.2 and the moments it stops, and then replay whichever one is cued. It is somewhat worse than forced teaching, mainly in the 3→0 direction.

**It depends on the release gap.** The count only credits a beat 1 to 5 ticks earlier, and staggered release does not write every lag cleanly:

| Gap between releases (ticks) | Cue 0 → 0123 | Cue 3 → 3210 | Next-in-line / shortcut weight |
|---|---:|---:|---:|
| 1 | 0.31 | 0.54 | 0.149 / 0.084 |
| 2 | 0.33 | 0.20 | 0.159 / 0.066 |
| 3 | 0.69 | 0.50 | 0.170 / 0.042 |
| 4 | 0.55 | 0.50 | 0.185 / 0.035 |
| 5 | 0.12 | 0.37 | 0.137 / 0.027 |
| 8 | 0.00 | 0.08 | 0.040 / 0.020 |

Measured on an uncoupled colony, a gap of 4 writes lags 4, 8, 12 exactly; a gap of 3 writes 3 and 6 but drops the fourth unit a whole cycle late.

**Limits.** The trigger and refractory that make replay possible are hand-written and switched on only at test, as before. The count is still a tally kept beside the colony; it does not use the unit's variance state. The order is still chosen by an outside hand: what changed is that it arrives as input timing, not as overridden output. Replay without a cue happens in 10 to 27% of windows, so the cue adds about 0.4 on top of that. Nothing here has been tested on a task.

---

## Second round: why it goes silent, and a hold-and-release switch

*Fable 5.2, 10 November 2026. Code: [quiet.py](quiet.py), [experiments/round2.py](experiments/round2.py). Numbers: [results/round2.json](results/round2.json). The first round below is Sol's and is left as written.*

**The colony is silenced by an 8-tick ripple, not by the size of the idle overlap.** Each unit idles with a ripple whose period is 8 ticks, twice the loop delay, and each unit is tuned to exactly that. One unit, a zero-mean square wave added to its input, beats summed over 8 starts (80 is normal):

| Period (ticks) | amplitude 0.05 | 0.1 | 0.2 |
|---|---:|---:|---:|
| 4 | 80 | 80 | 58 |
| 6 | 80 | 80 | 5 |
| **8** | 60 | **0** | 0 |
| 10 | 80 | 80 | 0 |
| 16 | 80 | 80 | 63 |
| 59 | 80 | 80 | 75 |

A constant input needs about 0.5 to silence the unit, and Gaussian noise about 0.2 to 0.3. Idle neighbours send each other this ripple through the overlap. The shifted-surface control shows it without confound: its mean heard input is about zero, all six units are silent at weight 0.05, and a two-tap comb that removes the 8-tick band (`y(t) = (x(t) + x(t-4)) / 2`) brings all six back.

The ripple acts through the drive, not the variance memory. Fed only into the drive it silences the unit at amplitude 0.1; fed only into the memory it needs 0.2 to 0.3 and is barely frequency-selective. (I predicted the opposite before measuring.)

**Three repairs, none sufficient.** Silent units of 6, mean of 8 starts, moving centered surface:

| Repair | weight 0.02 | 0.05 | 0.10 | 0.20 |
|---|---:|---:|---:|---:|
| None (Sol's result, 8 starts) | 0 | 2.8 | 6.0 | 6.0 |
| Comb (remove the 8-tick band) | 0 | 2.6 | 6.0 | 6.0 |
| Adapt (subtract the heard signal's 50-tick mean) | 0 | 4.4 | 3.6 | 5.4 |
| Heard signal kept out of the variance memory | 0 | 0 | 0.9 | 6.0 |
| All three | 0 | 0 | 0 | 0.5 |

With all three the units survive but slow down: 6.0, 3.2 and 2.4 beats per unit per 600 ticks at weights 0.05, 0.10 and 0.20, where 10 is normal. There are at least three ways to die here (the ripple, a constant offset, and the heard signal holding the variance up), and each repair addresses one. All three repairs are engineered and none is in `ecg.json`. The full table for every listening rule is in the results file.

**Hold and release.** The same rhythm is a switch. A unit given the 8-tick square wave at amplitude 0.2 stops within 19 ticks. After release, from 48 random starting phases, it beat exactly 53 ticks later in 48 of 48 runs, whether held for 100, 200, 400 or 403 ticks. At amplitude 0.1, held for 200 ticks or more, the delay was 95 ticks in 48 of 48 (94 when the hold ended at a different point of the rhythm). The rhythm erases the unit's phase and release starts its clock.

Six unconnected units, held and then released 8 ticks apart, beat in the order of release in 24 of 24 trials, against 0 of 24 with no hold. A timing pattern can be written into the colony from outside with no weight changed.

**What each listening rule does to a written lag.** Two units, a lag written by staggered release (44 of the 59 possible lags are reachable this way), then coupled for 3,000 ticks:

| Coupling | Distinct lags left | Pairs whose lag moved, of 59 | Silent pairs |
|---|---:|---:|---:|
| None | 44 | 0 | 0 |
| Moving surface, weight 0.1 | 41 | 0 | 0 |
| Moving surface, weight 0.2 | 34 | 20 | 6 |
| Fixed taps, weight 0.05 | 34 | 12 | 0 |
| Fixed taps, weight 0.1 | 21 | 33 | 0 |
| Fixed taps, weight 0.15 | 17 | 35 | 1 |

The old fixed taps pull lags onto a grid about 8 ticks apart: at weight 0.1, lags 6, 14, 46 and 54 hold 32 of the 59 pairs. The moving surface leaves a written lag alone until it is strong enough to silence the pair. As an organiser of relationships the surface listener does less than the rule it replaced.

**Not shown.** Any task advantage. That a written pattern survives noise or a disturbance (one kick test was run and was uninformative, because the kick did not move even an uncoupled unit). That hold and release keep their exact timing inside a coupled colony: in the two-unit browser lab at weight 0.12 the held unit still stops and restarts, but the release delay changes with the coupling. Whether the 8-tick grid under fixed taps is a set of true attractors.

**Where this leaves the idea.** Letting a unit listen through its own surface gives a real state-dependent coupling, but so far it is a weaker and more fragile one than fixed taps. The more useful thing found tonight belongs to the original loop, not to the surface: the unit is a narrow receiver at its own ripple period, and that gives an off switch, an exact reset, and a way to write timing.

In the [browser lab](https://anttiluode.github.io/GeometricNeuronSurfaceListener/), **Hold A** and **Hold B** apply the rhythm; press again to release.

---

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
    python experiments/round2.py
    python experiments/round3.py

The experiment writes the full numerical receipt to results/probe.json, including every phase pair. The committed [summary](results/summary.json) contains the primary results.

For the no-server GUI, open [index.html](index.html) directly in a desktop browser, even offline. The experiment uses [taps.js](taps.js) with the same archived image samples and [lab.js](lab.js) for the two-unit stepping model. Select the listening law, adjust the edge strength, and force pulses at either unit to watch the two 16-sample receptor surfaces interact.

A separate Node smoke test checks the browser simulator's period and symmetric kernel:

    node tests/browser_smoke.cjs

## Scientific boundary

This uses only the 16 sampled values in one checkerboard row, not a full 2D optical or physical wave field. The overlap is a conventional Pearson-style inner product. It is **not transformer attention**, not a measured biological neural mechanism, not emergent cognition, not a learned routing policy, and not a proof that geometry outperforms scalar or fixed-tap networks.

The positive finding is an experimentally measurable **state-dependent communication operator**. The negative finding is that, at modest six-unit coupling, it often destroys the original oscillator's activity. Both belong in the record.

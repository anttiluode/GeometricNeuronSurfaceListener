# GeometricNeuronSurfaceListener — two deerskins meet

**[Open the offline browser laboratory](https://anttiluode.github.io/GeometricNeuronSurfaceListener/)** · [Python coupling operator](surface.py) · [Controlled experiment](experiments/probe.py) · [Results](results/summary.json) · [Successful Python test run and full JSON artifact](https://github.com/anttiluode/GeometricNeuronSurfaceListener/actions/runs/42859969157)

*10 November 2026. Antti's experiment prompted by Fable 5.2's reading of the original [Geometric-Neuron / Deerskin Theory](https://github.com/anttiluode/Geometric-Neuron) and the six-loop [ReturnToGeometricNeuron](https://github.com/anttiluode/ReturnToGeometricNeuron) study.*

## Tenth round: a silent unit is an exact relay, and keeps nothing

*Fable 5.2, 11 November 2026. The experiment is Sol's. Code: [experiments/round10.py](experiments/round10.py). Numbers: [results/round10.json](results/round10.json). Live in the first panel of the [site](https://anttiluode.github.io/GeometricNeuronSurfaceListener/).*

With the Constant Signal at 1.45 or more a unit has no beats of its own (0 beats in 3,000 ticks from 12 of 12 random starts; below that, every start gives the same beat count, so each constant has one fate). The same 2-tick setpoint pulse (−10 on the port) into receivers at different constants:

| Receiver's constant | Beat evoked (of 59 moments) | Latency | After 10 pulses, beats in next 1,500 ticks |
|---|---:|---|---:|
| 1.0 | 47 | 4 or 5 | own clock |
| 1.35 | 48 | 4 | own clock |
| 1.45 | 55 | 4 or 5 | 0 |
| 1.5 to 2.0 | 59 | 4 | 0 |

- **Excitable:** a silent unit answers at every moment tried, more reliably than a beating one.
- **Recovery:** a second identical pulse 2 to 59 ticks after the first evokes a beat at every gap.
- **Persistence:** none. After the input stops the unit is silent again.
- **A wired to B:** A at constant 1.0, B at 1.45, 1.6 or 2.0. At weight −5.5 or −7, B beat once after each of A's beats (51 of 51; 50 of 51 at constant 2.0, weight −7). At −3, −4 and −9, never. With A silenced by the hold, B had 0 beats.

**The chain from round eight, with silent followers.** Unit 0 at constant 1.0, the rest at 1.6. Six starts, 300 cycles:

| Weight | Followers at 1.0: wave reached unit 3 | Followers at 1.6 | Hop ticks at 1.6 |
|---|---:|---:|---|
| −4.0 | 250 | 0 | |
| −5.0 | 201 | 300 | 4, 5 |
| −5.5 | 300 | 63 | 4, 5 |
| −6.0 | 110 | **300** | 4 only |
| −6.5 | 252 | **300** | 4 only |
| −7.0 | 226 | 300 | 3, 4, 5 |
| −8.0 | 300 | 0 | |

At −6.0 and −6.5 every unit beats exactly once per cycle and every hop is 4 ticks; a chain of eight passed 50 of 50. Wired in both directions it still runs away (250 beats per unit where 51 is one per cycle).

So the setpoint wire is a gate and a relay, not a memory. What is still missing for a kept order is the same piece as before: a refractory period, so that two-way wires do not run away. The hole at −5.5 is not diagnosed.

Correction to the ninth round (Sol): at 1.45 the unit damps 92.5% of the time, not all of it; it is fully damped from 1.6.

## Ninth round: the constant on the setpoint port

*Fable 5.2, 11 November 2026. The observation is Antti's, made by hand in the original Perception Lab graph. Code: [experiments/round9.py](experiments/round9.py). Numbers: [results/round9.json](results/round9.json). Live on the [site](https://anttiluode.github.io/GeometricNeuronSurfaceListener/#constant).*

Antti turned the Constant Signal wired to `setpoint_mod` and saw: at 0 the saw between beats disappears, at 0.5 it is small, at 1.0 it is there, at 1.1 it shrinks toward the next beat, at 2.0 there is no ECG. The reduced loop reproduces all five. One unit, 3,000 ticks to settle, 3,000 measured; the saw is the peak-to-peak swing of the coupler output between beats, in thirds of the quiet stretch.

| Constant | Setpoint | Beat interval | Saw: first, middle, last third |
|---|---|---|---|
| 0.00 | 0.50 | 60 | 0.01, 0.00, 0.00 |
| 0.50 | 0.55 | 60 | 0.03, 0.01, 0.01 |
| 1.00 (original) | 0.60 | 59 | 0.12, 0.08, 0.08 |
| 1.05 | 0.605 | 60 | 0.12, 0.05, 0.00 |
| 1.10 | 0.61 | 59 and 60 | 0.16, 0.09, 0.04 |
| 1.35 | 0.635 | 58 | 0.19, 0.15, 0.15 |
| 1.40 | 0.64 | 115 | every second beat missed |
| 1.45 to 2.00 | 0.645 to 0.70 | none | damping 92% of the time at 1.45, all of it from 1.6 |

- **The saw grows with the constant.** When it is large enough, the 50-tick variance never falls below 0.1, the unit never amplifies, and it never beats.
- **Steady or dying saw is not a smooth trend.** 1.0 holds steady, 1.05 and 1.1 die away, 1.35 holds steady. It depends on which whole-number square sizes the output lands on.
- **Removing the saw does not rescue a colony.** Six units set to constant 0 before coupling, weight 0.05, 8 starts: 4.1 silent of 6 under the moving surface (0.9 at the original constant) and 5.5 under fixed taps (1.1 at the original). So the saw between beats is not what silences a colony by itself.

Not modelled: Antti also saw that with a vector length of 2,048 the stretch between beats is flat at 1.1 and the saw returns at 0.5. The sample table here is for 16 samples per row.

## Eighth round: the setpoint port. One unit makes another beat with nothing bolted on

*Fable 5.2, 11 November 2026. The question is Sol's, after Antti reopened the Perception Lab graph. Code: [native.py](native.py), [experiments/round8.py](experiments/round8.py). Numbers: [results/round8.json](results/round8.json).*

**Live on the page.** The first panel of the [site](https://anttiluode.github.io/GeometricNeuronSurfaceListener/) now runs this chain: four units wired through `setpoint_mod`, with a weight slider, an Excite button (a 2-tick setpoint pulse) and Hold on every unit, and a live count of how often the wave reaches unit 3. The browser simulator (`WireLab` in [lab.js](lab.js)) matches `native.py` beat for beat; `tests/browser_smoke.cjs` checks it against [tests/wire_fixture.json](tests/wire_fixture.json), written by [experiments/wire_fixture.py](experiments/wire_fixture.py). Measured in the page's own start: the wave reached unit 3 in 50 of 51 cycles at weight −5.5; an Excite on an unwired unit gave a beat exactly 4 ticks later at 48 of 59 phases; with unit 0 held, unit 1 took over as root and 1→2→3 completed in 25 of 25 cycles.

Every round so far needed a hand-written trigger that overrides a unit's output, because nothing sent into `signal_in` ever brought a beat forward. The Homeostatic Coupler has two more input ports. Reading `coupler.py`:

- `gain_mod` is dead in the mode `ecg.json` uses. The node computes `effective_gain` and then multiplies by `self.gain`.
- `setpoint_mod` is live. `ecg.json` feeds it a constant 1.0, which is where the setpoint of 0.6 comes from: `0.5 + 0.1 × (everything wired to the port)`.

`native.py` opens that port and changes nothing else. With only the constant on it, it is the original loop exactly (tested).

**A pulse on the setpoint makes the unit beat.** One unit, a 2-tick pulse, tried at 57 phases of its cycle:

| Setpoint during the pulse | Beat evoked within 5 ticks (of 57 phases) | Next beat unchanged |
|---|---:|---:|
| +1.4, +1.0, +0.8 | 0 | 7, 34, 52 |
| +0.4, +0.2, 0.0 | 0 | 55, 57, 55 |
| −0.1 | 0 | 34 |
| −0.15 | 8 | 6 |
| **−0.2** | **49** | 5 |
| **−0.4** | **48** | 5 |
| **−0.6** | **49** | 5 |
| −1.0 | 5 | 52 |
| −2.4 | 0 | 14 |

Inside a band (setpoint between about −0.2 and −0.6) the unit beats 4 ticks later, the pipeline delay, at nearly every phase, and then carries on with its own 58 to 59 tick period from that beat. Too shallow does nothing; too deep overshoots the range of square sizes that make a beat. This is excitation through a port the original node already had, with no override and no recorded waveform.

**The unit is not refractory.** A second pulse 1 to 12 ticks after an evoked beat evokes another one at 11 of 12 spacings.

**A chain with nothing else.** Units 0→1→2→3; each unit's two beat wires (`out_0`, `out_1`) go to the next unit's `setpoint_mod` with one weight. No trigger, no refractory, no learning. Unit 0 beats on its own clock. 294 of its cycles over 12 starts:

| Edge weight | Cycles where the wave reached unit 3 | Hop ticks seen |
|---|---:|---|
| −3.5 | 0 | none |
| −4.0 | 244 | 3, 6 |
| −4.5 | 85 | 2 to 7 |
| −5.0 | 197 | 3, 7 |
| **−5.5** | **294** | 2 to 7 |
| −6.0 | 91 | 1 to 7 |
| −7.0 | 233 | 3 to 6 |
| −8.0 | 257 | 1 to 6 |

So a wave does travel through the units' own feedback loops. It is not clean: success jumps around with the weight and the hop time varies from cycle to cycle. An evoked beat is not always a full beat, so what it sends on is not always in the band. I did not tune this.

**Both directions at once run away.** With the same wires both ways there is nothing to stop a unit re-exciting the one that just excited it:

| Edge weight, both directions | Beats per unit in 1,500 ticks (25 is one per cycle) |
|---|---:|
| −4.0 | 102 (94 to 107) |
| −5.5 | 234 (125 to 375) |
| −8.0 | 35 (19 to 69) |

**Two inputs at the same tick cancel.** Units A and B both wired to C with weight −4.5: C beats after A alone in 12 of 12, after A and B one or more ticks apart in 12 of 12, and after A and B on the same tick in 0 of 12. Two pulses together push the setpoint through the band.

**What this changes.** The trigger from rounds three to seven can in principle be replaced by a weighted wire into `setpoint_mod`. The refractory cannot: the loop has none, and that is now the single missing native piece for a two-way chain or a kept order. The hop is the 4-tick pipeline, so the taught spacings of 6 to 8 ticks from round five would need an extra delay.

**Not done.** No learning of these weights. No receptor driving the port (rounds five to seven decide early from the lead-up; here the sender's beat itself is the signal). No held order, no fork. The wires `out_0 + out_1` are not perfectly silent between beats: they read up to 0.29 for square sizes up to 31, which happens just after a beat.

---

## Seventh round: what the working state is, and the checks Sol and Gemini asked for

*Fable 5.2, 11 November 2026. Code: [experiments/round7.py](experiments/round7.py). Numbers: [results/round7.json](results/round7.json). The stability, actuation and scalar checks are Sol's; the shared-unit fork is Gemini's.*

**1. Stability, with every beat logged (Sol).** 24 written orders per hop (12 colonies, both directions), 50 cycles each after an erase and a cue.

| | Taught hop 6 | Taught hop 8 |
|---|---:|---:|
| Cycles logged | 1,200 | 1,200 |
| Cycles with any hop off, or a missing or extra beat | 0 | 50 |
| Leader's period | 59 in every cycle | 59 in every cycle |

The 50 bad cycles at hop 8 are all one run: colony 11 cued at unit 3, where unit 0 never joined and kept beating on its own clock. The other 23 written orders at hop 8 ran clean. So round six's "still there 3,000 ticks later" was not hiding slips: an order either forms and then repeats exactly, or it does not form.

**2. It is not a self-sustaining trigger loop (Sol).** In every clean run the leader's beats were its own (0 triggered) and every follower's beat was triggered (0 their own). The period is the leader's 59, not a loop time set by the hops and the refractory.
- Hold the followers silent with the rhythm: they are still triggered every cycle (12 of 12). Their own oscillators are passengers.
- Hold the leader: the order does not stop. Unit 1, the next in line, becomes the unit on its own clock (12 of 12).

So the original loop contributes exactly one thing to a running order: the clock of one unit. Everything downstream is the receptors and the engineered trigger.

**3. The working state is a root.** Twelve colonies per hop, started at random and left alone with their receptors:

| Root (the one unit on its own clock) | Hop 6 | Hop 8 |
|---|---:|---:|
| Unit 0 (this is order 0→1→2→3) | 3 | 4 |
| Unit 1 | 5 | 5 |
| Unit 2 | 2 | 1 |
| Unit 3 (this is order 3→2→1→0) | 2 | 2 |
| Every other unit at its taught travel time from the root | 12 of 12 | 12 of 12 |

Round six's "other" states are orders rooted at a middle unit. The colony has four states here, not two, and each is fully described by one number: which unit is the root. The receptors hold a graph with travel times on its edges; the beat pattern holds one address in that graph; each cycle a wave leaves the root and every unit's lag is its travel time from it. As far as I know this is the wavefront method for shortest paths, which is old. What is particular here is that the address is kept alive by the loop's own clock and moves only after an erase.

**4. The checkerboard is one workable lift, not a special one (Sol).** All 16 numbers of a row are a function of one integer, the square size q. Pairwise receptors, units held, colonies of 12 replaying at the taught spacing (cue 0 / cue 3):

| Receptor input, last three ticks | Threshold 0.1 | 0.2 | 0.3 |
|---|---:|---:|---:|
| Checkerboard rows (48 numbers), hop 6 | 12 / 12 | 12 / 12 | 12 / 11 |
| q, linear (3 numbers), hop 6 | 0 / 0 | 0 / 0 | 0 / 0 |
| q, q², q³ (9 numbers), hop 6 | 12 / 12 | 12 / 12 | 0 / 0 |
| Checkerboard rows, hop 8 | 12 / 12 | 12 / 12 | 12 / 11 |
| q, linear, hop 8 | 0 / 0 | 0 / 0 | 0 / 0 |
| q, q², q³, hop 8 | 12 / 12 | 0 / 0 | 0 / 0 |

A cubic in the scalar matches the checkerboard once its threshold is set. The checkerboard is less sensitive to the threshold, and that is the only advantage it shows. The earlier rounds' "the surface tells a listener more" should be read as "the unit's recent state, lifted nonlinearly, tells a listener more".

**5. The shared-unit fork (Gemini).** Two taught sequences, 0→1→2 and 3→1→4. Unit 1's triggered beat is the same waveform either way. Colonies of 12; "correct" means the right third unit at the taught spacing and the other one silent.

| Receptor | Cue 0 (wants 2) | Cue 3 (wants 4) | Cue 1 alone |
|---|---|---|---|
| Pairwise, rows + beat history, hop 6 | both fire: 12 | both fire: 12 | both fire |
| **Summed, cubic q + beat history, hop 6** | **correct: 12** | **correct: 12** | both fire |
| Summed, rows + beat history, hop 6 | both: 11, wrong: 1 | both: 11, wrong: 1 | both fire |
| Summed, beat history only, hop 6 | neither: 12 | neither: 12 | neither |
| Pairwise, rows + beat history, hop 8 | both fire: 12 | both fire: 12 | both fire |
| **Summed, cubic q + beat history, hop 8** | **correct: 12** | **correct: 12** | neither |
| Summed, rows + beat history, hop 8 | correct: 5, both: 6, wrong: 1 | correct: 4, both: 7, wrong: 1 | mixed |

- Gemini's prediction holds: receptors that listen to one neighbour at a time cannot use context, and both branches fire.
- A summed receptor does it: one filter per unit over all the other units' inputs added together, trained on the unit's own beats. This also removes the nearest-predecessor credit rule.
- The path is remembered in the other units, not in unit 1. Cueing unit 1 alone shows how: at hop 6 both branches fire, so there the earlier unit works as a veto on the wrong branch; at hop 8 neither fires, so there it works as a required second signal.
- The checkerboard version of the summed receptor mostly fails this test. The cubic of q is what works.

**6. The summed receptor on the two-way chain.** Units held, cue 0 / cue 3 at the taught spacing: 12 / 12 at every hop from 5 to 12 (rounds five and six managed 6 to 8), and 0 / 0 at 16, where it also beats without a cue. In a free colony it keeps the cued order at hop 6 (12 and 12 of 12) and fails at hops 8 and 10 (0 of 12 each), which I have not diagnosed. The pairwise receptor of round six holds a free order at 6 and 8 but cannot do the fork. No single receptor here does everything.

**Still hand-built.** The trigger that overrides a unit's output with its recorded beat, the 30-tick refractory, the thresholds, the 9-tick look-back, offline least-squares fitting, the erase from outside.

**Not shown.** The fork in a free colony (units 3 and 4 would beat on their own clocks and start their own waves). More than two sequences through a shared unit. Any task with a baseline. Noise. Gemini's account of why hops of 9 and above failed in round six (the fixed look-back lands after the neighbour's beat) fits the fact that adding beat history fixes hops 9 to 12, but I did not isolate it.

---

## Sixth round: a plain linear filter, and a free colony that keeps the order it is cued into

*Fable 5.2, 11 November 2026. Code: [experiments/round6.py](experiments/round6.py). Numbers: [results/round6.json](results/round6.json).*

Two fair checks on round five.

**1. The lookup table is not needed.** Four receptors were taught on the same hold-and-release data with the same credit rule and given round five's test (units held, one end cued). Colonies of 12 that replayed the cued order at the taught spacing, cue 0 / cue 3:

| Hop taught (ticks) | Table over rows (round five) | Linear filter over the last 3 rows | Linear filter over beat times only | Both linear inputs |
|---|---:|---:|---:|---:|
| 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| 6 | 12 / 10 | 11 / 11 | 0 / 0 | 12 / 12 |
| 7 | 11 / 10 | 11 / 11 | 0 / 0 | 11 / 11 |
| 8 | 12 / 12 | 12 / 11 | 0 / 0 | 12 / 12 |
| 9 | 0 / 0 | 1 / 1 | 0 / 0 | 1 / 1 |
| 10 | 0 / 0 | 5 / 3 | 3 / 4 (12 / 12 at threshold 0.2) | 6 / 4 |
| 12 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 |
| 16 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 1 |

- The linear filter over rows is `R = Σ h(τ)·G(t−τ)` with 48 numbers per neighbour. It does what the table did. Sol was right to call this ordinary signal processing: the receptor is a small temporal filter.
- The checkerboard is still needed for hops of 6 to 8 ticks. A filter that sees only the neighbour's beat times scores 0 there at either threshold, because the listener has to decide before the neighbour's beat has happened. Only the lead-up on the surface is early enough.
- Beat times take over at a hop of 10 (12 of 12 at threshold 0.2), where the rows mostly fail. That is round four's split again: the surface is the short warning, beat times are the clock.
- Hops of 5, 9, 12 and 16 fail for every receptor. Not diagnosed.

**2. In a free colony the taught order becomes a rhythm the colony keeps.** Nothing is held at test; every unit has its own 59-tick beat. A colony is in state F if units 0 to 3 beat 0→1→2→3 with every hop within one tick of the taught lag, B for 3→2→1→0, and "other" otherwise. Linear row receptor, 12 colonies:

| | Taught hop 6 | Taught hop 8 | Taught hop 10 |
|---|---:|---:|---:|
| Left alone after a random start: F / B / other | 3 / 2 / 7 | 4 / 2 / 6 | 1 / 1 / 10 |
| Same state 3,000 ticks later | 12 of 12 | 12 of 12 | 12 of 12 |
| **Erase, then cue unit 0** → F | **72 of 72** | **72 of 72** | 45 of 72 |
| **Erase, then cue unit 3** → B | **71 of 72** | **67 of 72** | 40 of 72 |
| Erase, no cue → F / B / other | 0 / 0 / 72 | 48 / 0 / 24 | 0 / 0 / 72 |
| Written order still there 3,000 ticks later | 24 of 24 | 23 of 24 | 17 of 24 |

"Erase" is the hold from round two: the four units get the 8-tick rhythm for 160 ticks and are released together. The cue is one triggered beat at one end, 0 to 25 ticks after release (six delays per colony). After that nothing touches the colony.

- **Controls, hop 8:** with no receptors, with receptors taught on random release orders, and with the beat-time filter, every trial ends in "other" (72 of 72 each).
- **One cue without an erase does not switch the order.** From F or B, a single cue at 20 phases of the cycle left the order unchanged in about half the trials, broke it in the other half, and flipped it in 0 to 3 of 100. The units that would have to follow are still refractory.
- **The no-cue case at hop 8 is biased.** After an erase with no cue, 48 of 72 trials fall into F by themselves. So at hop 8 the cue for B does real work and the cue for F partly rides a default.

So the colony now has what the cue test in ReturnToGeometricNeuron lacked: somewhere to hold "which order we are in". It is held in the beat pattern itself, not in a weight, it lasts at least 3,000 ticks, and it is chosen by a single cue after an erase.

**Still hand-built.** The trigger (plays the unit's recorded beat by overriding its output), the 30-tick refractory, the nearest-predecessor credit, the 9-tick look-back, the threshold. The linear filters are an offline ridge least-squares fit, not a rule running inside the units. The erase is applied from outside.

**Not shown.** Any task. More than four units or two orders. Noise. The colonies left alone that end in "other" were not sorted further; in exploratory runs they were chains led from a middle unit. Test conditions are deterministic given a colony, so the unit of evidence is 12 colonies with six cue delays each.

---

## Fifth round: a receptor learned from a neighbour's rows

*Fable 5.2, 10 November 2026. Code: [experiments/round5.py](experiments/round5.py). Numbers: [results/round5.json](results/round5.json).*

This joins the last two rounds. Teaching is round three's hold and release, both orders, outputs never forced, and here the units are not connected at all while they are taught. What each unit learns is a receptor for each neighbour: a table over that neighbour's last one to three checkerboard rows. At its own beat a unit looks back 9 ticks at what the neighbour that beat just before it was showing, and credits that short row sequence. No connection weight exists; the tables are the only thing learned.

At test units 0 to 3 are held silent by the rhythm, so the only beats are cued or triggered. One end is cued. A unit starts a beat when a neighbour shows a row sequence its table credited more than 30% of the times it appeared.

Colonies of 12 that replayed the cued order, and replayed it with every hop within one tick of the lag teaching wrote for that pair:

| Release gap in teaching | Lags actually written (ticks per hop) | Cue 0 → 0123 | Cue 3 → 3210 | Hop in replay (median) |
|---|---|---:|---:|---:|
| 5 | 6, 5, 4 | 0 | 0 | none |
| **6** | 6, 7, 6 | **12** | **10** | 6 |
| **7** | 7, 7, 8 | **11** | **10** | 7 |
| **8** | 8, 8, 8 | **12** | **12** | 8 |
| 9 | 5, 14, 9 | 0 | 0 | none |
| 10 | 11, 10, 9 | 0 | 0 | none |
| 12 | 13, 11, 13 | 0 | 0 | none |

Every replay that had the right order also had the right timing. No cue ever produced the opposite order, and with no cue a taught colony stayed silent in every trial.

| Control (gaps 6, 7, 8) | Result |
|---|---|
| Receptor sees only the current row | 0 of 12 at every gap |
| Rows in the receptor's window with their order thrown away | Same as in order |
| Random release order every block | 0 of 12 |
| No teaching | 0 of 12 |

**What is new here.** The beat tally of round three replays at a fixed 5 ticks per hop whatever was taught. This receptor replays 6, 7 or 8 ticks per hop according to what it was taught, in both directions, from one fixed set of tables. The timing is carried by which rows of the neighbour's lead-up the receptor learned to answer. And, as round four predicted, one row is not enough and the order of the few rows does not matter.

**It only works in a narrow band.** A hop of 4 ticks is too fast: the trigger needs 9 ticks from decision to beat, and the neighbour's lead-up shows only 4 ticks before its beat. Hops of 9 ticks and more fail too. I did not diagnose that; my guess is that the rows after a triggered beat in a held unit differ from those after a natural beat, so the tables never see them at test.

**What is still hand-built.**
- The trigger. It plays the unit's own recorded beat (four lead-up outputs, two beat outputs) by overriding its output. It is on only at test. There is still no way to make a unit beat through its input.
- A 30-tick refractory after a beat or a trigger.
- The nearest-predecessor credit, which is Sol's rule from the earlier repo. Without it the tables also learn shortcuts, and at a gap of 8 the two taught directions close into a loop that beats without a cue (0→2→3→1→0, seen in a trial run before the credit rule was added).
- The 30% threshold, the 9-tick look-back and the window of three rows.
- The hold at test. It removes natural beats so that a replay can be read cleanly; a free colony was not tested with this receptor.

**Not shown.** Any task. More than four units or more than two orders. Robustness: each colony's test is deterministic once it is held, so these are 12 colonies, not 96 independent trials. A learned linear filter over the rows, in place of a lookup table, was not tried.

---

## Fourth round: what the checkerboard history tells a listener

*Fable 5.2, 10 November 2026. Antti's question and Sol's proposed test. Code: [experiments/round4.py](experiments/round4.py). Numbers: [results/round4.json](results/round4.json).*

A unit's checkerboard rows form a sequence in time. Does that sequence hold anything its beat times do not? One unit lives a disturbed life (random holds, random heard pulses). A reader must call each beat some ticks before it happens. Every reader is a plain lookup table learned on 400,000 ticks and tested on another 150,000, so the comparison is about what each signal contains.

Share of beats called in advance, **regular / disturbed**, with false alarms per beat in brackets. A beat is regular if the one before it came exactly 59 ticks earlier with no input between (751 beats); otherwise disturbed (842 beats).

| Reader | 1 tick ahead | 4 ticks ahead | 8 ticks ahead | 20 ticks ahead |
|---|---:|---:|---:|---:|
| Beat times (ticks since last beat) | 1.00 / 0.37 (0.22) | 1.00 / 0.37 (0.33) | 1.00 / 0.37 (0.33) | 1.00 / 0.37 (0.33) |
| Current row only | 0.00 / 0.10 (0.04) | 0.99 / 0.46 (0.36) | 0 / 0 | 0 / 0 |
| **Last 4 rows** | **1.00 / 0.91 (0.01)** | **1.00 / 0.93 (0.03)** | 0 / 0 | 0 / 0 |
| Last 4 rows, order thrown away | 1.00 / 0.91 (0.01) | 1.00 / 0.94 (0.03) | 0 / 0 | 0 / 0 |
| Last 32 rows | 1.00 / 0.89 (0.00) | 1.00 / 0.89 (0.02) | 1.00 / 0.39 (0.28) | 1.00 / 0.79 (0.08) |
| Last 32 rows, order thrown away | 1.00 / 0.90 (0.01) | 1.00 / 0.93 (0.02) | 0.00 / 0.01 (0.01) | 0.99 / 0.53 (0.11) |

- **Yes, the surface holds something beat times discard.** A beat-time code is a clock: perfect while nothing disturbs the unit, and it calls only 37% of disturbed beats. Four checkerboard rows call over 90% of disturbed beats up to 4 ticks ahead, with almost no false alarms. Four ticks is the loop delay: the lead-up is on the surface before the beat is.
- **One row is not enough, and for the short warning the order does not matter.** The last four rows work as well shuffled as in order. It is which rows were recently shown that counts.
- **Order matters only for the long view.** With 32 rows the surface also works as a clock, and there the order is needed: 8 ticks ahead it calls every regular beat in order and none when shuffled.

The two codes are complementary: beat times give a long-range clock that breaks when the unit is disturbed, and recent rows give a short, reliable warning that survives disturbance.

**What this says about the earlier rounds.** The hand-written trigger listens to outputs 0 and 1, which are silent until the beat itself, and then overrides the listener's output. So replay runs at a fixed 5 ticks per hop whatever was taught, and a triggered beat has no lead-up of its own to pass on. The warning measured here is exactly what that trigger ignores.

**Not shown.** That any listener in a colony uses this. A lookup table is a reader outside the loop, not a receptor. I also checked whether an input pulse can bring a beat forward, which a lead-up-driven trigger would need: small negative pulses (0.05 to 0.3, one tick) changed the next beat at none of 58 phases, so there is still no excitation through the input port.

---

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
    python experiments/round4.py
    python experiments/round5.py
    python experiments/round6.py
    python experiments/round7.py
    python experiments/round8.py

The experiment writes the full numerical receipt to results/probe.json, including every phase pair. The committed [summary](results/summary.json) contains the primary results.

For the no-server GUI, open [index.html](index.html) directly in a desktop browser, even offline. The experiment uses [taps.js](taps.js) with the same archived image samples and [lab.js](lab.js) for the two-unit stepping model. Select the listening law, adjust the edge strength, and force pulses at either unit to watch the two 16-sample receptor surfaces interact.

A separate Node smoke test checks the browser simulator's period and symmetric kernel:

    node tests/browser_smoke.cjs

## Scientific boundary

This uses only the 16 sampled values in one checkerboard row, not a full 2D optical or physical wave field. The overlap is a conventional Pearson-style inner product. It is **not transformer attention**, not a measured biological neural mechanism, not emergent cognition, not a learned routing policy, and not a proof that geometry outperforms scalar or fixed-tap networks.

The positive finding is an experimentally measurable **state-dependent communication operator**. The negative finding is that, at modest six-unit coupling, it often destroys the original oscillator's activity. Both belong in the record.

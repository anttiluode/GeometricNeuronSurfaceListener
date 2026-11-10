"""No-learning surface-listener intervention test.

Fixed before outcomes:
* exact original one-unit loop (period should remain 59);
* K is equal-time *centered normalized* 16-sample surface overlap;
* raw dot, fixed row, shifted row, old fixed taps, and null are controls;
* W_01=W_10=0.20, gain 3.5 (except fixed taps uses old true units);
* 59 receiver phases; speaker held at a common stable reference phase;
* one two-tick BEAT=-0.28 forced *speaker* output vs identical sham;
* strict receiver beat-shift and activity response over 120 ticks;
* six-unit no-learning coupling sweep with equal weights for stability.

The coupling is symmetric instantaneously when W is symmetric and no lag is
used. A difference in outgoing *causal effect* can arise from internal history;
it is not automatically trained, useful, or cognitive directionality.

Run: python experiments/probe.py
Writes: results/probe.json
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gn.core import Colony, G, QMIN
from surface import MODES, SurfaceColony, aligned_two_unit_state, overlap_matrix

PHASES = 59
HORIZON = 120
WEIGHT = 0.20
GAIN = 3.5
BEAT = -0.28
MODES = ("surface", "raw", "fixed", "shifted", "fixed_taps", "null")


def single_cycle():
    c = Colony(1)
    for _ in range(1300):
        c.step()
    # Record all phases. c is on the established 59-tick cycle.
    states = [copy.deepcopy(c)]
    for _ in range(PHASES - 1):
        c.step()
        states.append(copy.deepcopy(c))
    qs = [int(st.q[0]) for st in states]
    return states, qs


def pulse_probe(base, mode, pulse_index):
    w = np.array([[0, WEIGHT], [WEIGHT, 0]], dtype=float)
    pulse = SurfaceColony(2, W=w, mode=mode, gain=GAIN, base=base)
    sham = SurfaceColony(2, W=w, mode=mode, gain=GAIN, base=base)
    y_pulse = []
    y_sham = []
    r_pulse = []
    r_sham = []
    for k in range(HORIZON):
        force = None
        if k < 2:
            force = np.array([np.nan, np.nan])
            force[pulse_index] = BEAT
        y_pulse.append(pulse.step(force=force).copy())
        y_sham.append(sham.step().copy())
        r_pulse.append(pulse.core.R.copy())
        r_sham.append(sham.core.R.copy())
    a, b = np.array(y_pulse), np.array(y_sham)
    receiver = 1 - pulse_index
    # Only score onsets after the four-tick feedback transit.
    def next_beat(y):
        m = y[8:, receiver] > 3
        onsets = m & ~np.concatenate([[False], m[:-1]])
        return int(np.flatnonzero(onsets)[0] + 8) if onsets.any() else None

    t1, t0 = next_beat(a), next_beat(b)
    return {
        "next_beat_shift": (t1-t0 if t1 is not None and t0 is not None else None),
        "receiver_changed": bool(np.max(np.abs(a[:, receiver]-b[:, receiver])) > 1e-8),
        "receiver_read_l1": float(np.sum(np.abs(
            np.array(r_pulse)[:40, receiver] - np.array(r_sham)[:40, receiver]))),
        "pulse_next_beat": t1, "sham_next_beat": t0,
    }


def functional_phase_probe(states):
    out = {}
    speaker_fixed = states[0]
    for mode in MODES:
        rows = []
        for p in range(PHASES):
            # At p=0 both units have the SAME phase; at p>0 only listener
            # phase differs. Both pulse directions are tested, matched.
            base = aligned_two_unit_state(states[p], speaker_fixed)
            into_listener = pulse_probe(base, mode, pulse_index=1)
            into_speaker = pulse_probe(base, mode, pulse_index=0)
            rows.append({"receiver_phase": p,
                         "speaker_to_listener": into_listener,
                         "listener_to_speaker": into_speaker})
        a = [r["speaker_to_listener"] for r in rows]
        b = [r["listener_to_speaker"] for r in rows]
        def summary(side):
            d = [x["next_beat_shift"] for x in side if x["next_beat_shift"] is not None]
            return {
                "observed_beat_shifts_n": len(d),
                "nonzero_beat_shift_n": sum(x!=0 for x in d),
                "mean_abs_beat_shift": float(np.mean(np.abs(d))) if d else None,
                "mean_receiver_read_l1_first40": float(np.mean(
                    [x["receiver_read_l1"] for x in side])),
                "affected_read_n": sum(x["receiver_read_l1"] > 1e-8 for x in side),
                "affected_output_n": sum(x["receiver_changed"] for x in side),
            }
        out[mode] = {"speaker_to_listener": summary(a),
                     "listener_to_speaker": summary(b), "phases": rows}
        print("phase", mode, json.dumps({
            "speaker_to_listener": out[mode]["speaker_to_listener"],
            "listener_to_speaker": out[mode]["listener_to_speaker"]}), flush=True)
    return out


def category_table(states):
    # Use periods of the actual original loop, not hand-selected q values.
    traces = []
    c = copy.deepcopy(states[0])
    for _ in range(PHASES):
        own = c.step()[0]
        traces.append({"q": int(c.q[0]), "own": float(own)})
    # Classify beat by observed own>3, lead-up by q=78..84 blind zone.
    # These bins only label descriptive plots, not experimental decisions.
    states_seen = {}
    for item in traces:
        key = ("beat" if item["own"] > 3 else
               "leadup" if 75 <= item["q"] <= 88 else "idle")
        states_seen.setdefault(key, []).append(item["q"])
    sampled = {k: list(dict.fromkeys(v)) for k,v in states_seen.items()}
    table = {}
    for a, qs_a in sampled.items():
        table[a] = {}
        for b, qs_b in sampled.items():
            vals = []
            for q1 in qs_a:
                for q2 in qs_b:
                    g = np.stack([G[q1-QMIN], G[q2-QMIN]])
                    vals.append(float(overlap_matrix(g, "surface")[0,1]))
            table[a][b] = {"min": min(vals), "max": max(vals),
                           "mean": float(np.mean(vals)), "pairs":len(vals)}
    return sampled, table


def six_unit_check():
    modes = ("surface", "raw", "fixed", "shifted", "fixed_taps", "null")
    out = {}
    for w in (0.02, 0.05, 0.10, 0.20):
        key = str(w)
        out[key] = {}
        for mode in modes:
            stats = []
            for seed in range(4):
                n = 6
                weights = np.full((n,n), w)
                np.fill_diagonal(weights,0)
                cc = SurfaceColony(n, W=weights, mode=mode, gain=GAIN,
                                   rng=np.random.default_rng(seed))
                prev = np.zeros(n, dtype=bool)
                events = np.zeros((500,n), dtype=bool)
                for t in range(1100):
                    own = cc.step()
                    loud = own > 3
                    onset = loud & ~prev
                    prev = loud
                    if t>=600:
                        events[t-600]=onset
                nbeat = events.sum(axis=0)
                pairs = [(i,j) for i in range(n) for j in range(i+1,n)]
                exact_pairs = sum(np.array_equal(events[:,i],events[:,j])
                                  for i,j in pairs)
                stats.append({"events_per_unit_mean":float(np.mean(nbeat)),
                              "silent_units":int(np.sum(nbeat==0)),
                              "identical_pair_fraction":exact_pairs/len(pairs),
                              "total_beats":int(nbeat.sum())})
            out[key][mode]={
                k:float(np.mean([s[k] for s in stats])) for k in stats[0]
            }
        print("six-unit",key,json.dumps(out[key]),flush=True)
    return out


def main():
    states, qs = single_cycle()
    categories, table = category_table(states)
    # Equal-time symmetric K, analytic test against moving/frozen receiver.
    cycle_rows = np.stack([G[int(st.q[0])-QMIN] for st in states])
    K = overlap_matrix(cycle_rows, "surface")
    off = K[~np.eye(PHASES, dtype=bool)]
    analytical = {
        "cycle_q": qs, "orbit_unique_q": sorted(set(qs)),
        "surface_mean_offdiagonal": float(np.mean(off)),
        "surface_min_offdiagonal": float(np.min(off)),
        "surface_max_offdiagonal": float(np.max(off)),
        "surface_symmetry_max_error": float(np.max(np.abs(K-K.T))),
        "surface_dynamic_range": float(np.ptp(off)),
        "categories": categories, "category_correlation": table,
        "surface_K_59x59": K.tolist()
    }
    data={"design":{
        "model":"Exact GN original loop unchanged; neighbour input through ext",
        "no_learning":True,"phase_count":PHASES,"pulse_output":BEAT,
        "pulse_ticks":2,"pulse_trials_per_mode":PHASES,"horizon":HORIZON,
        "two_unit_symmetric_weight":WEIGHT,"gain_except_fixed_taps":GAIN,
        "controls":list(MODES),
        "warning":"Centered Pearson geometry is a choice. Raw dot is also tested. A shared phase overlap is not learned attention or proof of useful routing."
        }, "analytic":analytical,
        "causal_phase_pulses":functional_phase_probe(states),
        "six_unit":six_unit_check()}
    path=ROOT/"results/probe.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+"\n")
    print("WROTE",path,flush=True)
    print("SUMMARY",json.dumps({
        "analytical":{k:v for k,v in analytical.items() if k not in
                      ("surface_K_59x59","cycle_q","categories","category_correlation")},
        "causal_phase_pulses":{mode:{
            k:v for k,v in metrics.items() if k!="phases"
        } for mode,metrics in data["causal_phase_pulses"].items()},
        "six_unit":data["six_unit"]
    }),flush=True)


if __name__=="__main__":
    main()

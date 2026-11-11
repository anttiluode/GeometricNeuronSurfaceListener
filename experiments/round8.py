"""Eighth round (Fable 5.2): the setpoint port. Can one unit make another beat with no
trigger, no output override and no recorded waveform?

Sol's suggestion, after Antti reopened the Perception Lab graph: the Homeostatic Coupler has
ports the seven rounds never used. Reading coupler.py: `gain_mod` is dead in edge_of_chaos
mode (effective_gain is computed and never used). `setpoint_mod` is live; ecg.json feeds it a
constant 1.0, which is where the 0.6 setpoint comes from. native.py opens that port.

  pulse     one unit, a 2-tick pulse on setpoint_mod at every phase of its cycle
  chain     0->1->2->3, each unit's two beat wires (out_0, out_1) wired to the next unit's
            setpoint_mod with one weight. Nothing else: no trigger, no refractory, no learning
  two_way   the same wires in both directions
  together  two units wired to a third; they beat alone, together, or a few ticks apart

Run: python experiments/round8.py        Writes: results/round8.json
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from native import SetpointColony  # noqa: E402

SEEDS = 12


def phase_states():
    c = SetpointColony(1)
    for _ in range(1300):
        c.step()
    prev = False
    while True:
        loud = c.step()[0] > 3
        if loud and not prev:
            break
        prev = loud
    out = []
    for _ in range(59):
        out.append(copy.deepcopy(c))
        c.step()
    return out


def beats_after(state, m, dur, ticks=200):
    c = copy.deepcopy(state)
    prev, out = True, []
    for k in range(ticks):
        loud = c.step(sp_ext=np.array([float(m)]) if k < dur else None)[0] > 3
        if loud and not prev:
            out.append(k)
        prev = loud
    return out


def pulse():
    st = phase_states()
    base = [beats_after(s, 0, 0) for s in st]
    res = {}
    for m in (-30, -16, -12, -10, -8, -7.5, -7, -6, -4, -2, 2, 4, 8):
        evoked = same = 0
        nxt = []
        for p in range(2, 59):
            b = beats_after(st[p], m, 2)
            if b and b[0] < base[p][0] and b[0] <= 5:
                evoked += 1
                if len(b) > 1:
                    nxt.append(b[1] - b[0])
            elif b and b[0] == base[p][0]:
                same += 1
        res[str(m)] = {"setpoint_during_pulse": round(0.6 + 0.1 * m, 2), "phases": 57,
                       "beat_evoked_within_5_ticks": evoked, "next_beat_unchanged": same,
                       "ticks_to_following_beat": sorted(set(nxt))}
        print("pulse", m, res[str(m)], flush=True)
    # is the unit refractory after an evoked beat?
    again = {}
    for d in range(1, 13):
        c = copy.deepcopy(st[30])
        prev, ev = True, []
        for k in range(60):
            on = k < 2 or 4 + d <= k < 6 + d
            loud = c.step(sp_ext=np.array([-10.0]) if on else None)[0] > 3
            if loud and not prev:
                ev.append(k)
            prev = loud
        again[str(d)] = len(ev) >= 2
    res["second_pulse_d_ticks_after_evoked_beat_evokes_again"] = again
    return res


def run_chain(v, seed, ticks=3000):
    n = len(v)
    c = SetpointColony(n, v=v, rng=np.random.default_rng(seed))
    prev = np.zeros(n, bool)
    ev = [[] for _ in range(n)]
    for t in range(ticks):
        loud = c.step() > 3
        for u in np.flatnonzero(loud & ~prev):
            ev[u].append(t)
        prev = loud
    return ev


def chain_v(wt, two_way=False, n=4):
    v = np.zeros((n, n))
    for i in range(n - 1):
        v[i + 1, i] = wt
        if two_way:
            v[i, i + 1] = wt
    return v


def chain():
    res = {}
    for wt in (-3, -3.5, -4, -4.5, -5, -5.5, -6, -7, -8):
        full = cyc = 0
        hops, rate = {}, []
        for s in range(SEEDS):
            ev = run_chain(chain_v(wt), s)
            root = [t for t in ev[0] if t >= 1500]
            rate.append(np.mean([sum(t >= 1500 for t in e) for e in ev[1:]]) / max(len(root), 1))
            for t in root[:-1]:
                cyc += 1
                at = [t]
                for u in (1, 2, 3):
                    x = [y for y in ev[u] if at[-1] < y <= at[-1] + 8]
                    if not x:
                        break
                    at.append(x[0])
                if len(at) == 4:
                    full += 1
                    for h in np.diff(at):
                        hops[int(h)] = hops.get(int(h), 0) + 1
        res[str(wt)] = {"root_cycles": cyc, "cycles_where_the_wave_reached_unit_3": full,
                        "hop_ticks_seen": dict(sorted(hops.items())),
                        "follower_beats_per_root_beat": float(np.mean(rate))}
        print("chain", wt, res[str(wt)], flush=True)
    return res


def two_way():
    res = {}
    for wt in (-4, -5.5, -8):
        rates = []
        for s in range(SEEDS):
            ev = run_chain(chain_v(wt, True), s)
            rates.append(np.mean([sum(t >= 1500 for t in e) for e in ev]))
        res[str(wt)] = {"beats_per_unit_in_1500_ticks_mean": float(np.mean(rates)),
                        "min": float(np.min(rates)), "max": float(np.max(rates)),
                        "one_per_cycle_would_be": 25}
        print("two_way", wt, res[str(wt)], flush=True)
    return res


def together():
    res = {}
    v = np.array([[0, 0, 0], [0, 0, 0], [-4.5, -4.5, 0.0]])
    for lag in (None, 0, 1, 2, 3, 5, 10):
        hit = 0
        for s in range(SEEDS):
            c = SetpointColony(3, v=v, rng=np.random.default_rng(s))
            for _ in range(300):
                c.step()
            prev = np.zeros(3, bool)
            beat = False
            for k in range(40):
                f = np.full(3, np.nan)
                if k in (0, 1):
                    f[0] = -0.28                       # stimulate A (and B) to beat
                if lag is not None and k in (lag, lag + 1):
                    f[1] = -0.28
                hold = np.full(3, 0.2 * (1 if c.t % 8 < 4 else -1))
                loud = c.step(force=f, ext=hold) > 3
                beat |= bool((loud & ~prev)[2])
                prev = loud
            hit += beat
        res["A alone" if lag is None else f"B {lag} ticks after A"] = hit
        print("together", lag, hit, flush=True)
    return res


def main():
    out = {"spec": {"seeds": SEEDS, "beat_wires": "out_0 + out_1 of the sender",
                    "setpoint": "0.5 + 0.1 * (1.0 + weighted beat wires)"},
           "pulse": pulse(), "chain": chain(), "two_way": two_way(),
           "third_unit_beats_of_12": together()}
    (ROOT / "results/round8.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round8.json")


if __name__ == "__main__":
    main()

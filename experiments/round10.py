"""Tenth round (Fable 5.2): a receiver that does not beat by itself. Sol's experiment.

Round nine: with the Constant Signal at 1.45 or more a unit has no large beats. Round eight:
a neighbour can drive setpoint_mod. So: is a silent unit B excitable, does it recover, and
does anything persist once the input stops? No mechanism is added; this is native.py.

  starts      does B at a fixed constant have one fate or several? 12 random starts each
  pulse       the SAME 2-tick setpoint pulse into B at different constants (the control that
              separates the receiver's susceptibility from the sender's waveform)
  recovery    a second identical pulse d ticks after the first
  persist     a train of 10 pulses 59 ticks apart, then nothing for 1,500 ticks
  wire        A (constant 1.0, beating by itself) wired to B's setpoint port; then A is
              silenced with the 8-tick hold and B is watched for 1,500 ticks

Run: python experiments/round10.py        Writes: results/round10.json
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

CS = (1.0, 1.2, 1.35, 1.45, 1.5, 1.6, 1.8, 2.0)


def settled(c, seed=None, ticks=3000):
    col = SetpointColony(1, rng=None if seed is None else np.random.default_rng(seed))
    for _ in range(ticks):
        col.step(sp_ext=np.array([c - 1.0]))
    return col


def beats(col, c, ticks, pulses=(), m=-10.0):
    """Beat ticks of a one-unit colony; pulses = start ticks of 2-tick setpoint pulses."""
    prev, out = True, []
    for k in range(ticks):
        on = any(p <= k < p + 2 for p in pulses)
        loud = col.step(sp_ext=np.array([c - 1.0 + (m if on else 0.0)]))[0] > 3
        if loud and not prev:
            out.append(k)
        prev = loud
    return out


def starts():
    res = {}
    for c in (1.3, 1.35, 1.4, 1.45, 1.5, 1.6, 2.0):
        n = [len(beats(settled(c, s), c, 3000)) for s in range(12)]
        res[str(c)] = {"beats_in_3000_ticks_per_start": n}
        print("starts", c, n, flush=True)
    return res


def pulse():
    res = {}
    for c in CS:
        base = settled(c)
        row = {}
        for m in (-4.0, -6.0, -8.0, -10.0, -12.0, -16.0):
            ev, lat = 0, []
            for ph in range(59):
                col = copy.deepcopy(base)
                beats(col, c, ph)
                ref = beats(copy.deepcopy(col), c, 12)
                b = beats(col, c, 12, pulses=(0,), m=m)
                if b and not ref:                      # a beat that would not have happened
                    ev += 1
                    lat.append(b[0])
            row[str(m)] = {"evoked_of_59": ev, "latency_ticks": sorted(set(lat))}
        res[str(c)] = row
        print("pulse", c, {k: v["evoked_of_59"] for k, v in row.items()}, flush=True)
    return res


def recovery(m=-10.0):
    res = {}
    for c in (1.0, 1.45, 1.6, 2.0):
        base = settled(c)
        beats(base, c, 30)
        row = {}
        for d in (2, 4, 6, 8, 10, 12, 16, 20, 30, 40, 59):
            col = copy.deepcopy(base)
            b = beats(col, c, d + 12, pulses=(0, d), m=m)
            row[str(d)] = int(sum(1 for x in b if x >= d))      # beats after the second pulse
        res[str(c)] = {"beats_within_12_ticks_of_second_pulse_by_gap": row}
        print("recovery", c, row, flush=True)
    return res


def persist(m=-10.0):
    res = {}
    for c in (1.45, 1.5, 1.6, 1.8, 2.0):
        col = settled(c)
        train = tuple(100 + 59 * k for k in range(10))
        during = beats(col, c, 100 + 590, pulses=train, m=m)
        after = beats(col, c, 1500)
        res[str(c)] = {"beats_during_10_pulses": len(during), "beats_in_1500_ticks_after": len(after),
                       "last_beat_after_train_end_tick": after[-1] if after else None}
        print("persist", c, res[str(c)], flush=True)
    return res


def wire():
    res = {}
    for cb in (1.45, 1.6, 2.0):
        for w in (-3.0, -4.0, -5.5, -7.0, -9.0):
            col = SetpointColony(2, v=[[0, 0], [w, 0]])
            sp = np.array([0.0, cb - 1.0])
            for _ in range(1500):
                col.step(sp_ext=sp)
            prev, ev = np.ones(2, bool), [[], []]
            for k in range(3000):
                loud = col.step(sp_ext=sp) > 3
                for u in np.flatnonzero(loud & ~prev):
                    ev[u].append(k)
                prev = loud
            follow = sum(any(a < b <= a + 8 for b in ev[1]) for a in ev[0])
            after = [[], []]
            for k in range(1700):                                # silence A with the 8-tick hold
                hold = np.array([0.2 * (1 if col.t % 8 < 4 else -1), 0.0])
                loud = col.step(sp_ext=sp, ext=hold) > 3
                for u in np.flatnonzero(loud & ~prev):
                    after[u].append(k)
                prev = loud
            res[f"B constant {cb}, weight {w}"] = {
                "A_beats": len(ev[0]), "B_beats": len(ev[1]), "A_beats_followed_by_B_within_8": follow,
                "after_A_is_held__A_beats_after_tick_200": sum(k > 200 for k in after[0]),
                "after_A_is_held__B_beats_after_tick_200": sum(k > 200 for k in after[1])}
            print("wire", cb, w, res[f"B constant {cb}, weight {w}"], flush=True)
    return res


def chain_run(w, cf, n=4, two_way=False, seed=0, ticks=3000):
    v = np.zeros((n, n))
    for i in range(n - 1):
        v[i + 1, i] = w
        if two_way:
            v[i, i + 1] = w
    col = SetpointColony(n, v=v, rng=np.random.default_rng(seed))
    sp = np.full(n, cf - 1.0)
    sp[0] = 0.0                                             # unit 0 keeps the original constant
    prev, ev = np.ones(n, bool), [[] for _ in range(n)]
    for k in range(1500 + ticks):
        loud = col.step(sp_ext=sp) > 3
        if k >= 1500:
            for u in np.flatnonzero(loud & ~prev):
                ev[u].append(k)
        prev = loud
    full, hops = 0, {}
    for t in ev[0][:-1]:
        at = [t]
        for u in range(1, n):
            x = [y for y in ev[u] if at[-1] < y <= at[-1] + 8]
            if not x:
                break
            at.append(x[0])
        if len(at) == n:
            full += 1
            for h in np.diff(at):
                hops[int(h)] = hops.get(int(h), 0) + 1
    return full, len(ev[0]) - 1, [len(e) for e in ev], hops


def chain():
    """Round eight's chain again, with the followers set silent (constant 1.6)."""
    res = {}
    for cf in (1.0, 1.6):
        for w in (-4, -4.5, -5, -5.5, -6, -6.5, -7, -7.5, -8):
            r = [chain_run(w, cf, seed=s) for s in range(6)]
            hops = {}
            for x in r:
                for h, k in x[3].items():
                    hops[h] = hops.get(h, 0) + k
            res[f"followers {cf}, weight {w}"] = {
                "cycles": sum(x[1] for x in r), "wave_reached_unit_3": sum(x[0] for x in r),
                "beats_per_unit_first_start": r[0][2], "hop_ticks_seen": dict(sorted(hops.items()))}
            print("chain", cf, w, res[f"followers {cf}, weight {w}"], flush=True)
    for w in (-6, -6.5):
        r = chain_run(w, 1.6, n=8)
        res[f"8 units, followers 1.6, weight {w}"] = {"cycles": r[1], "wave_reached_unit_7": r[0], "beats_per_unit": r[2]}
        r = chain_run(w, 1.6, two_way=True)
        res[f"both directions, followers 1.6, weight {w}"] = {"beats_per_unit": r[2], "one_per_cycle_would_be": 51}
        print("chain extras", w, res[f"8 units, followers 1.6, weight {w}"], res[f"both directions, followers 1.6, weight {w}"], flush=True)
    return res


def main():
    out = {"starts": starts(), "pulse": pulse(), "recovery": recovery(), "persist": persist(), "wire": wire(), "chain": chain()}
    (ROOT / "results/round10.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round10.json")


if __name__ == "__main__":
    main()

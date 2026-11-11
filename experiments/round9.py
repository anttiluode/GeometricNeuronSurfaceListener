"""Ninth round (Fable 5.2): the constant on the setpoint port. Antti's observation in the
original Perception Lab graph, 11 November 2026: changing the Constant Signal wired to
setpoint_mod changes the "saw" between beats. 0 removes it, 0.5 shrinks it, 1.0 (ecg.json)
has it, 1.1 has one that shrinks toward the next beat, 2.0 has no ECG at all.

One unit, constant c on setpoint_mod, so setpoint S = 0.5 + 0.1 * c. 3,000 ticks to settle,
3,000 measured. The ripple is the peak-to-peak swing of the coupler output in the quiet
stretch between two beats (from 12 ticks after a beat to 12 before the next), in thirds.

Run: python experiments/round9.py        Writes: results/round9.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from native import SetpointColony  # noqa: E402


def measure(c, settle=3000, ticks=3000):
    col = SetpointColony(1)
    own, o, q, hot = [], [], [], []
    for t in range(settle + ticks):
        y = col.step(sp_ext=np.array([c - 1.0]))
        if t >= settle:
            own.append(y[0]); o.append(col.pipe[-1][0]); q.append(int(col.q[0])); hot.append(col.var[0] > 0.1)
    own, o, q = np.array(own), np.array(o), np.array(q)
    loud = own > 3
    b = np.flatnonzero(loud[1:] & ~loud[:-1]) + 1
    iv = np.diff(b)
    res = {"constant": float(c), "setpoint": round(float(0.5 + 0.1 * c), 4), "beats_in_3000_ticks": int(len(b)),
           "damping_fraction": round(float(np.mean(hot)), 3)}
    if len(iv):
        res["beat_intervals"] = sorted(set(int(x) for x in iv))
        thirds, sizes = [[], [], []], set()
        for a, e in zip(b[:-1], b[1:]):
            seg, qs = o[a + 12:e - 12], q[a + 12:e - 12]
            if len(seg) < 12:
                continue
            k = len(seg) // 3
            for j in range(3):
                thirds[j].append(float(np.ptp(seg[j * k:(j + 1) * k])))
            sizes |= set(qs.tolist())
        if thirds[0]:
            res["ripple_first_middle_last_third"] = [round(float(np.mean(x)), 3) for x in thirds]
            res["square_sizes_between_beats"] = sorted(sizes)
    else:
        res["output_range"] = [round(float(o.min()), 3), round(float(o.max()), 3)]
        res["square_sizes"] = sorted(set(q.tolist()))
    return res


class _C(SetpointColony):
    c = 1.0

    def step(self, ext=None, kick=None, force=None):
        return super().step(ext=ext, sp_ext=np.full(self.n, self.c - 1.0), force=force)


def colony_silent(mode, w, c, seed, n=6, ticks=1100):
    """Does removing the saw rescue the six-unit colony of the first round? Silent units of 6."""
    from surface import SurfaceColony
    base = _C(n, rng=np.random.default_rng(seed))
    base.c = c
    for _ in range(600):
        base.step()
    W = np.full((n, n), w)
    np.fill_diagonal(W, 0)
    col = SurfaceColony(n, W=W, mode=mode, base=base)
    own = np.array([col.step() for _ in range(ticks)])
    return int(sum(not (own[-500:, i] > 3).any() for i in range(n)))


def main():
    colony = {f"{mode}, constant {c}": {str(w): float(np.mean([colony_silent(mode, w, c, s) for s in range(8)]))
                                        for w in (0.02, 0.05, 0.10, 0.20)}
              for mode in ("surface", "fixed_taps") for c in (0.0, 0.5, 1.0)}
    print(colony, flush=True)
    rows = [measure(round(c, 2)) for c in np.arange(0, 2.0001, 0.05)]
    for r in rows:
        print(r, flush=True)
    (ROOT / "results/round9.json").write_text(json.dumps({"sweep": rows, "mean_silent_units_of_6_by_weight": colony}, indent=1) + "\n")
    print("WROTE results/round9.json")


if __name__ == "__main__":
    main()

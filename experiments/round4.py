"""Fourth round (Fable 5.2): does a unit's checkerboard history say more than its beat times?

Antti's question (the checkerboard patterns form sequences in time; do they become numbers a
listener can use?) and Sol's proposed test (beat history against surface history, with a
time-shuffled control), on the unchanged loop.

One unit lives a disturbed life: random holds with the 8-tick rhythm and random heard pulses.
A reader watches it and must call each beat L ticks before it happens. Readers are plain
lookup tables learned on one life (400,000 ticks) and tested on another (150,000 ticks), so
the comparison is about what each signal contains, not about how clever the reader is.

  beat       ticks since the unit's last beat (everything a beat-time code can know)
  surface T  the last T checkerboard rows, in order
  shuffled T the same T rows with their order thrown away (sorted)

A beat is 'regular' if the previous beat was exactly 59 ticks earlier with no input between,
otherwise 'disturbed'. A reader calls a beat if its table says more likely than not.

Run: python experiments/round4.py        Writes: results/round4.json
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gn.core import Colony, G, QMIN  # noqa: E402

TRAIN, TEST = 400_000, 150_000
LEADS = (1, 2, 4, 6, 8, 12, 20)


def sq(t):
    return 1.0 if (t % 8) < 4 else -1.0


def life(seed, ticks):
    rng = np.random.default_rng(seed)
    c = Colony(1, rng=np.random.default_rng(seed))
    q = np.zeros(ticks, int)
    on = np.zeros(ticks, bool)
    touched = np.zeros(ticks, bool)
    prev = False
    hold_until, next_hold = -1, int(rng.integers(150, 500))
    pulse_at, amp, left = int(rng.integers(50, 400)), 0.0, 0
    for t in range(ticks):
        x = 0.0
        if t == next_hold:
            hold_until = t + int(rng.integers(40, 300))
        if t < hold_until:
            x += 0.2 * sq(t)
        elif t >= next_hold:
            next_hold = t + int(rng.integers(150, 600))
        if t == pulse_at:
            amp, left = float(rng.choice([0.2, 0.5, 1.0])), 2
            pulse_at = t + int(rng.integers(60, 400))
        if left > 0:
            x += amp
            left -= 1
        touched[t] = x != 0
        loud = c.step(ext=np.array([x]))[0] > 3
        q[t] = c.q[0]
        on[t] = loud and not prev
        prev = loud
    return q, on, touched


def keys(sym, on, T, kind):
    n = len(sym)
    out = [None] * n
    if kind == "beat":
        last = 999
        for t in range(n):
            last = 0 if on[t] else min(last + 1, 400)
            out[t] = last
        return out
    for t in range(T - 1, n):
        w = sym[t - T + 1:t + 1]
        out[t] = tuple(w) if kind == "surface" else tuple(sorted(w))
    return out


def main():
    qa, oa, _ = life(1, TRAIN)
    qb, ob, tb_ = life(2, TEST)
    ids = {}
    sym = np.array([ids.setdefault(G[x - QMIN].tobytes(), len(ids))
                    for x in np.concatenate([qa, qb])])
    sa, sb = sym[:TRAIN], sym[TRAIN:]
    bt = np.flatnonzero(ob)
    reg = np.zeros(len(bt), bool)
    for i in range(1, len(bt)):
        reg[i] = (bt[i] - bt[i - 1] == 59) and not tb_[bt[i - 1]:bt[i]].any()
    out = {"train_ticks": TRAIN, "test_ticks": TEST, "distinct_rows": len(ids),
           "test_beats_regular": int(reg.sum()), "test_beats_disturbed": int((~reg).sum()),
           "leads": list(LEADS), "readers": {}}
    for kind, T in (("beat", 0), ("surface", 1), ("surface", 4), ("surface", 8),
                    ("surface", 16), ("surface", 32), ("shuffled", 4), ("shuffled", 8),
                    ("shuffled", 16), ("shuffled", 32)):
        ka, kb = keys(sa, oa, T, kind), keys(sb, ob, T, kind)
        rows = {}
        for L in LEADS:
            table = collections.defaultdict(lambda: [0, 0])
            for t in range(TRAIN - L):
                k = ka[t]
                if k is not None:
                    e = table[k]
                    e[0] += oa[t + L]
                    e[1] += 1
            pred = np.zeros(TEST, bool)
            for t in range(TEST - L):
                k = kb[t]
                if k is not None and k in table:
                    e = table[k]
                    pred[t + L] = e[0] * 2 > e[1]
            hit = pred[bt]
            rows[str(L)] = {"regular_called": float(hit[reg].mean()),
                            "disturbed_called": float(hit[~reg].mean()),
                            "false_alarms_per_beat": float((pred & ~ob).sum() / len(bt))}
        name = kind if kind == "beat" else f"{kind}_{T}"
        out["readers"][name] = rows
        print(name, " ".join(f"{v['regular_called']:.2f}/{v['disturbed_called']:.2f}/"
                             f"{v['false_alarms_per_beat']:.2f}" for v in rows.values()),
              flush=True)
    (ROOT / "results/round4.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round4.json")


if __name__ == "__main__":
    main()

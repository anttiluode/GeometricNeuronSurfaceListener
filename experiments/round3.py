"""Third round (Fable 5.2): teach a chain by hold and release, not by forcing beats.

In ReturnToGeometricNeuron the only rule that built a two-way chain (Sol's nearest-predecessor
count, round five) was taught by forcing the units' outputs. Here the outputs are never forced
during teaching. Units 0-3 are held silent by the small 8-tick rhythm on their input and then
let go a few ticks apart; every beat that follows is the loop's own. The same nearest-predecessor
count is applied, unchanged, and the weights are then frozen and tested with the same trigger,
refractory and cue score as rounds three to five of that repo (re-implemented below; gn/core.py
is identical in both repos).

Conditions
  release_AB       blocks alternate 0->1->2->3 and 3->2->1->0, written by staggered release
  forced_AB        Sol's round-five teaching: outputs forced by a pacing schedule (reference)
  release_random   same holds and releases, but a fresh random order every block (control)
  untaught         no teaching, the rule just watches a free colony (control)
  hand_set         adjacent edges 0.22, others 0.02 (the round-four ideal chain)

After teaching every colony is scrambled the same way (held, then released in a random order
13 ticks apart) so that timing left over from the last block cannot stand in for the weights.

Run: python experiments/round3.py        Writes: results/round3.json
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gn.core import Colony, G, QMIN  # noqa: E402

N = 6
OFF = ~np.eye(N, dtype=bool)
S2 = G[:, 0] + G[:, 1]
BEAT, THETA, SHORT = -0.28, 0.25, 10
SEEDS, TRIALS = 12, 8
HOLD, FREE, AMP = 160, 340, 0.2


def sq(t):
    return 1.0 if (t % 8) < 4 else -1.0


class Counter:
    """Sol's nearest-predecessor credit, unchanged: a beat credits the closest other beat
    that came 1 to 5 ticks before it."""

    def __init__(self):
        self.last = np.full(N, -999, dtype=int)
        self.before = np.zeros(N, bool)
        self.credits = np.zeros((N, N))
        self.posts = np.zeros(N)

    def watch(self, c):
        beating = c.own > 3.0
        onset = beating & ~self.before
        self.before = beating
        for dst in np.flatnonzero(onset):
            self.posts[dst] += 1
            age = c.t - self.last
            age[dst] = 999
            cand = np.where((age >= 1) & (age <= 5))[0]
            if len(cand):
                self.credits[dst, int(cand[np.argmin(age[cand])])] += 1
        self.last[onset] = c.t

    def weights(self):
        frac = self.credits / np.maximum(self.posts[:, None], 1)
        w = np.clip(0.02 + 0.4 * frac, 0.02, 0.35)
        np.fill_diagonal(w, 0)
        return w


def release_block(c, order, gap, counter=None, hold=HOLD, free=FREE):
    """Hold units 0-3 with the rhythm, release them in `order`, `gap` ticks apart, run free."""
    t0 = c.t
    until = {u: t0 + hold + r * gap for r, u in enumerate(order)}
    lags = []
    for _ in range(hold + 3 * gap + free):
        x = np.zeros(N)
        for u, tu in until.items():
            if c.t < tu:
                x[u] = AMP * sq(c.t)
        c.step(ext=x)
        if counter is not None:
            counter.watch(c)
    return lags


def pace(order, period=57, gap=3):
    def f(t):
        k = np.full(N, np.nan)
        ph = t % period
        for r, u in enumerate(order):
            if ph in (r * gap, r * gap + 1):
                k[u] = BEAT
        return k
    return f


def teach(kind, seed, gap=3):
    c = Colony(N, w=np.full((N, N), 0.02) * OFF, rng=np.random.default_rng(seed))
    rng = np.random.default_rng(500 + seed)
    k = Counter()
    for b in range(16):
        fwd = b % 2 == 0
        if kind == "release_AB":
            release_block(c, [0, 1, 2, 3] if fwd else [3, 2, 1, 0], gap, k)
        elif kind == "release_random":
            release_block(c, list(rng.permutation(4)), gap, k)
        elif kind == "forced_AB":
            f = pace([0, 1, 2, 3] if fwd else [3, 2, 1, 0])
            for _ in range(500):
                c.step(force=f(c.t))
                k.watch(c)
        else:
            for _ in range(500):
                c.step()
                k.watch(c)
    # the same scramble for every condition: leftover timing must not stand in for weights
    release_block(c, list(np.random.default_rng(900 + seed).permutation(4)), 13)
    for _ in range(600):
        c.step()
    return c, k.weights()


def hand_set():
    w = np.full((N, N), 0.02) * OFF
    for i in range(3):
        w[i, i + 1] = w[i + 1, i] = 0.22
    return w


def tick(c, force=None, trigger=True):
    if not hasattr(c, "last_own"):
        c.last_own = np.full(c.n, -999)
    if trigger:
        fire = ((c.w * S2[c.q - QMIN][None, :]).sum(axis=1) > THETA) & ((c.t - c.last_own) >= SHORT)
        trig = np.where(fire, BEAT, np.nan)
        force = trig if force is None else np.where(np.isnan(force), trig, force)
    own = c.step(force=force)
    c.last_own = np.where(own > 3, c.t, c.last_own)
    return own


def probe(c, cue, window=40):
    c = copy.deepcopy(c)
    f = np.full(N, np.nan)
    if cue is not None:
        f[cue] = BEAT
    own = np.array([tick(c, force=f if k < 2 else None) for k in range(300)])
    loud = own > 3
    on = loud & ~np.vstack([np.zeros((1, N), bool), loud[:-1]])
    return [int(np.argmax(on[:window, u])) if on[:window, u].any() else None for u in range(4)]


def exact(first, head):
    chain = [0, 1, 2, 3] if head == 0 else [3, 2, 1, 0]
    t = [first[u] for u in chain]
    return int(all(x is not None for x in t) and all(t[i + 1] > t[i] for i in range(3)))


def evaluate(base, w):
    c = copy.deepcopy(base)
    c.w = w.copy()
    for _ in range(600):
        tick(c)
    rows = []
    for _ in range(TRIALS):
        for _ in range(173):
            tick(c)
        a, b, z = probe(c, 0), probe(c, 3), probe(c, None)
        rows.append({"cue0_0123": exact(a, 0), "cue3_3210": exact(b, 3),
                     "cue0_wrong_3210": exact(a, 3), "cue3_wrong_0123": exact(b, 0),
                     "nocue_0123": exact(z, 0), "nocue_3210": exact(z, 3)})
    return rows


def written_lags(gap, seeds=12):
    """What staggered release actually writes: lags of units 1-3 behind unit 0, uncoupled."""
    out = []
    for s in range(seeds):
        c = Colony(N, rng=np.random.default_rng(s))
        release_block(c, [0, 1, 2, 3], gap, free=0)
        first = np.full(N, -1)
        prev = np.zeros(N, bool)
        for _ in range(200):
            loud = c.step() > 3
            on = loud & ~prev & (first < 0)
            first[on] = c.t
            prev = loud
        out.append(tuple(int(first[u] - first[0]) for u in (1, 2, 3)))
    return sorted(set(out))


def main():
    adj = [(i, j) for i in range(4) for j in range(4) if abs(i - j) == 1]
    far = [(i, j) for i in range(4) for j in range(4) if abs(i - j) > 1]
    out = {"spec": {"seeds": SEEDS, "trials_per_seed": TRIALS, "hold_ticks": HOLD,
                    "free_ticks_per_block": FREE, "rhythm_amplitude": AMP, "blocks": 16,
                    "trigger_threshold": THETA, "refractory_ticks": SHORT,
                    "note": "Trigger and refractory are hand-written and on only at test."},
           "written_lags_behind_unit0": {str(g): written_lags(g) for g in (1, 2, 3, 4, 5, 6, 8)},
           "conditions": {}}
    print("written", out["written_lags_behind_unit0"], flush=True)
    runs = [("release_AB", 3), ("forced_AB", 3), ("release_random", 3), ("untaught", 3),
            ("hand_set", 3), ("release_AB", 1), ("release_AB", 2), ("release_AB", 4),
            ("release_AB", 5), ("release_AB", 8)]
    for kind, gap in runs:
        rows, wa, wf = [], [], []
        for seed in range(SEEDS):
            base, w = teach("release_AB" if kind == "hand_set" else kind, seed, gap)
            if kind == "hand_set":
                w = hand_set()
            wa.append(np.mean([w[i, j] for i, j in adj]))
            wf.append(np.mean([w[i, j] for i, j in far]))
            rows += evaluate(base, w)
        res = {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}
        res.update(adjacent_weight=float(np.mean(wa)), shortcut_weight=float(np.mean(wf)),
                   n=len(rows))
        name = kind if gap == 3 else f"{kind}_gap{gap}"
        out["conditions"][name] = res
        print(name, json.dumps({k: round(v, 3) for k, v in res.items()}), flush=True)
    (ROOT / "results/round3.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round3.json")


if __name__ == "__main__":
    main()

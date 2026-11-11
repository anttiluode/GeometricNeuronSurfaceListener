"""Seventh round (Fable 5.2): the checks Sol and Gemini asked for, and what the colony's
working state actually is.

  stability   every beat of a written order logged for 3,000 ticks; cycles that deviate counted
  roots       which beats are the loop's own and which are triggered; every settled state
              named by its root (the one unit beating on its own clock)
  scalar      Sol's control: the 16 checkerboard numbers are a function of one integer q.
              Receptors over the last three q values (linear, cubic) against the 48 numbers
  fork        Gemini's test: 0->1->2 and 3->1->4 share unit 1, whose triggered beat is
              identical either way. Can anything choose the right continuation?

The receptors here are of two kinds.
  pairwise  round six: one filter per (listener, neighbour); the listener goes if ANY one
            neighbour's filter crosses threshold; trained with nearest-predecessor credit
  joint     one filter per listener over ALL other units' inputs added together; trained
            on the listener's own beats, so no credit rule is needed

Run: python experiments/round7.py        Writes: results/round7.json
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from gn.core import Colony, G, QMIN  # noqa: E402
import round5 as r5  # noqa: E402
from round5 import N, AMP, WAVE, LAT, REFR, sq  # noqa: E402

SEEDS = 12
ROWS_T, BEAT_K, RIDGE = 3, 24, 1e-3
DIM = {"rows": 16 * ROWS_T, "beats": BEAT_K, "q": ROWS_T, "qcubic": 3 * ROWS_T}


def lift(q, part):
    """q: [..., ROWS_T] recent square sizes, newest first -> that part's numbers."""
    x = q / 100.0
    if part == "rows":
        return G[q - QMIN].reshape(*q.shape[:-1], -1).astype(float)
    if part == "q":
        return x
    return np.concatenate([x, x ** 2, x ** 3], axis=-1)           # qcubic


def design(Q, ONS, src, feat):
    """Inputs a listener watching `src` would have had at every tick of teaching."""
    n = len(Q)
    parts = []
    for part in feat.split("+"):
        if part == "beats":
            b = ONS[:, src].astype(float)
            parts.append(np.stack([np.concatenate([np.zeros(d), b[:n - d]])
                                   for d in range(BEAT_K)], 1))
        else:
            q = np.stack([np.concatenate([np.full(d, Q[0, src]), Q[:n - d, src]])
                          for d in range(ROWS_T)], 1)
            parts.append(lift(q, part))
    return np.hstack(parts)


def fit(x, y):
    x = np.hstack([x, np.ones((len(x), 1))])
    return np.linalg.solve(x.T @ x + RIDGE * np.eye(x.shape[1]), x.T @ y)


def learn(Q, ONS, feat, mode, listeners, thr=0.3):
    n = len(Q) - LAT
    xs = [design(Q, ONS, s, feat)[:n] for s in range(N)]
    rec = {"feat": feat, "mode": mode, "thr": thr, "w": {}}
    if mode == "pairwise":
        credit = r5.nearest_predecessor(ONS)
        for d in listeners:
            for s in range(N):
                if s != d:
                    rec["w"][(d, s)] = fit(xs[s], (credit[LAT:, d] == s).astype(float))
    else:
        for d in listeners:
            x = np.hstack([xs[s] for s in range(N) if s != d])
            rec["w"][d] = fit(x, ONS[LAT:, d].astype(float))
    return rec


class Net:
    """A colony with frozen receptors, the waveform trigger and the refractory.
    `held` is the set of units currently given the 8-tick rhythm."""

    def __init__(self, colony, rec, held=()):
        self.c = copy.deepcopy(colony)
        self.rec, self.held = rec, set(held)
        self.q = [self.c.q.copy()] * ROWS_T
        self.beats = [np.zeros(N)] * BEAT_K
        self.wave_at = np.full(N, -1)
        self.last = np.full(N, -999)
        self.prev = np.zeros(N, bool)
        self.log = None                                    # set to [] to record (t, unit, kind)

    def inputs(self, src):
        parts = []
        for part in self.rec["feat"].split("+"):
            if part == "beats":
                parts.append(np.array([self.beats[-1 - d][src] for d in range(BEAT_K)]))
            else:
                parts.append(lift(np.array([self.q[-1 - d][src] for d in range(ROWS_T)]), part))
        return np.concatenate(parts)

    def go(self, dst, x):
        rec = self.rec
        if rec["mode"] == "pairwise":
            return any(float(np.append(x[s], 1.0) @ rec["w"][(dst, s)]) > rec["thr"]
                       for s in range(N) if s != dst)
        v = np.concatenate([x[s] for s in range(N) if s != dst] + [np.ones(1)])
        return float(v @ rec["w"][dst]) > rec["thr"]

    def tick(self, cue=None):
        c = self.c
        if self.rec is not None:
            x = None
            for dst in ({k if isinstance(k, int) else k[0] for k in self.rec["w"]}):
                if self.wave_at[dst] >= 0 or c.t - self.last[dst] < REFR:
                    continue
                if x is None:
                    x = [self.inputs(s) for s in range(N)]
                if self.go(dst, x):
                    self.wave_at[dst] = 0
                    self.last[dst] = c.t
        if cue is not None and self.wave_at[cue] < 0:
            self.wave_at[cue] = 0
            self.last[cue] = c.t
        force = np.full(N, np.nan)
        driven = self.wave_at >= 0
        for u in range(N):
            if self.wave_at[u] >= 0:
                force[u] = WAVE[self.wave_at[u]]
                self.wave_at[u] = self.wave_at[u] + 1 if self.wave_at[u] < len(WAVE) - 1 else -1
        ext = np.zeros(N)
        for u in self.held:
            ext[u] = AMP * sq(c.t)
        own = c.step(force=force, ext=ext)
        loud = own > 3
        onset = loud & ~self.prev
        self.prev = loud
        self.q = self.q[1:] + [c.q.copy()]
        self.beats = self.beats[1:] + [onset.astype(float)]
        if self.log is not None:
            for u in np.flatnonzero(onset):
                # a beat is 'triggered' if a trigger for this unit started in the last 12 ticks
                self.log.append((c.t, int(u), "triggered" if c.t - self.last[u] <= 12 else "own"))
        self.last = np.where(onset, c.t, self.last)
        return onset

    def run(self, ticks, cue=None):
        for k in range(ticks):
            self.tick(cue if k == 0 else None)
        return self


def teach(seed, gap, blocks, used, rounds=16, hold=160, free=340):
    """Hold-and-release teaching. In each block the units in its order are released `gap`
    ticks apart; the other `used` units stay held (silent) for the whole block."""
    c = Colony(N, w=np.zeros((N, N)), rng=np.random.default_rng(seed))
    Q, ONS = [], []
    prev = np.zeros(N, bool)

    def step(ext):
        nonlocal prev
        loud = c.step(ext=ext) > 3
        Q.append(c.q.copy())
        ONS.append(loud & ~prev)
        prev = loud
    for b in range(rounds):
        order = blocks[b % len(blocks)]
        while c.t % 8:
            step(None)
        t0 = c.t
        until = {u: t0 + hold + 3 * gap + free for u in used}
        until.update({u: t0 + hold + r * gap for r, u in enumerate(order)})
        for _ in range(hold + 3 * gap + free):
            step(np.array([AMP * sq(c.t) if u in until and c.t < until[u] else 0.0
                           for u in range(N)]))
    return c, np.array(Q), np.array(ONS)


def modal_lag(ONS, a, b):
    ta, tb = np.flatnonzero(ONS[:, a]), np.flatnonzero(ONS[:, b])
    d = [int(x - ta[ta < x][-1]) for x in tb if (ta < x).any()]
    d = [x for x in d if 1 <= x <= 29]
    return int(np.bincount(d).argmax()) if d else None


CHAIN = [[0, 1, 2, 3], [3, 2, 1, 0]]
FORK = [[0, 1, 2], [3, 1, 4]]


def first_beats(net, cue, units, window=70):
    n = copy.deepcopy(net)
    first = {u: None for u in units}
    for k in range(window):
        on = n.tick(cue if k == 0 else None)
        for u in units:
            if on[u] and first[u] is None:
                first[u] = k
    return first


def chain_ok(first, chain, want):
    t = [first[u] for u in chain]
    return int(None not in t and all(abs((t[i + 1] - t[i]) - want[i]) <= 1
                                     for i in range(len(want))))


def erase_cue(net, cue, delay=10, units=(0, 1, 2, 3), hold=160):
    n = copy.deepcopy(net)
    while n.c.t % 8:
        n.tick()
    n.held = set(units)
    n.run(hold)
    n.held = set()
    n.run(delay)
    n.tick(cue)
    return n


def roots(net, ticks=600):
    """Units whose beats are their own (not triggered), and each unit's last beat time."""
    n = copy.deepcopy(net)
    n.log = []
    n.run(ticks)
    kinds = {u: [0, 0] for u in range(4)}
    last = {}
    for t, u, kind in n.log:
        if u < 4:
            kinds[u][kind == "own"] += 1
            last[u] = t
    return [u for u in range(4) if kinds[u][1] > kinds[u][0]], last


def chain_lags(O):
    return ([modal_lag(O, a, b) for a, b in ((0, 1), (1, 2), (2, 3))],
            [modal_lag(O, a, b) for a, b in ((3, 2), (2, 1), (1, 0))])


def stability_and_roots(out):
    for gap in (6, 8):
        cyc = dev = 0
        periods, own_beats, trig_beats = set(), 0, 0
        root_tally, at_distance, single = {}, 0, 0
        new_root, followers_ok = {}, 0
        for seed in range(SEEDS):
            c, Q, O = teach(seed, gap, CHAIN, (0, 1, 2, 3))
            wf, wb = chain_lags(O)
            rec = learn(Q, O, "rows", "pairwise", range(4))
            c2 = copy.deepcopy(c)
            r5.release(c2, list(np.random.default_rng(70 + seed).permutation(4)), 13)
            net = Net(c2, rec).run(1500)
            # what a colony left alone settles into, named by its root
            own, last = roots(net)
            root_tally[str(own)] = root_tally.get(str(own), 0) + 1
            if len(own) == 1:
                single += 1
                R = own[0]
                pred = {R: 0}
                for u in range(R + 1, 4):
                    pred[u] = pred[u - 1] + wf[u - 1]
                for u in range(R - 1, -1, -1):
                    pred[u] = pred[u + 1] + wb[2 - u]
                at_distance += all(abs(((last[u] - last[R]) % 59) - pred[u]) <= 1 for u in range(4))
            # a written order, every beat logged for 3,000 ticks
            for cue, chain, want in ((0, [0, 1, 2, 3], wf), (3, [3, 2, 1, 0], wb)):
                n = erase_cue(net, cue).run(300)
                n.log = []
                n.run(3000)
                by = {u: [t for t, v, _ in n.log if v == u] for u in range(4)}
                for t, v, kind in n.log:
                    if v < 4:
                        own_beats += (kind == "own") and v != cue
                        trig_beats += (kind == "triggered") and v == cue
                lead = by[cue]
                periods |= set(np.diff(lead).tolist())
                for t in lead[:-1]:
                    cyc += 1
                    at = [t] + [next((x for x in by[u] if t < x < t + 59), None) for u in chain[1:]]
                    good = None not in at and [at[i + 1] - at[i] for i in range(3)] == want \
                        and all(sum(t <= x < t + 59 for x in by[u]) == 1 for u in range(4))
                    dev += not good
            # hold the root of a written order; hold the followers
            f = erase_cue(net, 0).run(600)
            a = copy.deepcopy(f)
            a.held = {0}
            a.run(900)
            key = str([u for u in roots(a)[0] if u != 0])
            new_root[key] = new_root.get(key, 0) + 1
            b = copy.deepcopy(f)
            b.held = {1, 2, 3}
            b.log = []
            b.run(600)
            followers_ok += all(sum(1 for t, v, k in b.log if v == u and k == "triggered") >= 9
                                for u in (1, 2, 3))
        out["stability"][f"gap{gap}"] = {
            "written_orders": 2 * SEEDS, "cycles_logged": cyc, "cycles_deviating": dev,
            "leader_periods_seen": sorted(int(p) for p in periods),
            "follower_beats_that_were_their_own": int(own_beats),
            "leader_beats_that_were_triggered": int(trig_beats)}
        out["roots"][f"gap{gap}"] = {
            "settled_states_by_root": root_tally, "single_root_states": single,
            "of_those_all_units_at_taught_distance_from_root": int(at_distance),
            "root_held_new_root": new_root,
            "followers_held_still_triggered_every_cycle_of_12": int(followers_ok)}
        print("stability", gap, out["stability"][f"gap{gap}"], flush=True)
        print("roots", gap, out["roots"][f"gap{gap}"], flush=True)


def scalar_control(out):
    for gap in (6, 8):
        data = [teach(s, gap, CHAIN, (0, 1, 2, 3)) for s in range(SEEDS)]
        for feat in ("rows", "q", "qcubic"):
            for thr in (0.1, 0.2, 0.3):
                a = b = quiet = 0
                for c, Q, O in data:
                    wf, wb = chain_lags(O)
                    net = Net(c, learn(Q, O, feat, "pairwise", range(4), thr), held=range(4)).run(413)
                    a += chain_ok(first_beats(net, 0, range(4)), [0, 1, 2, 3], wf)
                    b += chain_ok(first_beats(net, 3, range(4)), [3, 2, 1, 0], wb)
                    quiet += all(v is None for v in first_beats(net, None, range(4)).values())
                out["scalar"][f"{feat}_thr{thr}_gap{gap}"] = {
                    "cue0_of_12": a, "cue3_of_12": b, "silent_without_cue_of_12": quiet}
                print("scalar", feat, thr, gap, a, b, quiet, flush=True)


def fork(out):
    for gap in (6, 8):
        data = [teach(s, gap, FORK, (0, 1, 2, 3, 4)) for s in range(SEEDS)]
        for mode, feat, thr in (("pairwise", "rows+beats", 0.3), ("pairwise", "qcubic+beats", 0.2),
                                ("joint", "rows+beats", 0.3), ("joint", "beats", 0.3),
                                ("joint", "qcubic", 0.3), ("joint", "qcubic+beats", 0.3)):
            res = {0: {}, 3: {}, 1: {}}
            for c, Q, O in data:
                net = Net(c, learn(Q, O, feat, mode, range(5), thr), held=range(5)).run(413)
                for cue, right, wrong, l1, l2 in ((0, 2, 4, (0, 1), (1, 2)), (3, 4, 2, (3, 1), (1, 4))):
                    f = first_beats(net, cue, range(5))
                    mid = f[1] is not None and abs(f[1] - f[cue] - modal_lag(O, *l1)) <= 1
                    r_ok = mid and f[right] is not None \
                        and abs(f[right] - f[1] - modal_lag(O, *l2)) <= 1
                    w = f[wrong] is not None
                    k = "correct" if r_ok and not w else "both" if r_ok and w \
                        else "wrong_only" if w else "neither"
                    res[cue][k] = res[cue].get(k, 0) + 1
                f = first_beats(net, 1, range(5))
                k = "+".join(str(u) for u in (2, 4) if f[u] is not None) or "neither"
                res[1][k] = res[1].get(k, 0) + 1
            out["fork"][f"{mode}_{feat}_thr{thr}_gap{gap}"] = {
                "cue0_wants_2": res[0], "cue3_wants_4": res[3], "cue1_alone_who_follows": res[1]}
            print("fork", mode, feat, thr, gap, res, flush=True)


def best_receptor(out):
    """The joint cubic-q + beat-history receptor (no credit rule) on the two-way chain."""
    for gap in (5, 6, 7, 8, 9, 10, 12, 16):
        a = b = quiet = fa = fb = 0
        for seed in range(SEEDS):
            c, Q, O = teach(seed, gap, CHAIN, (0, 1, 2, 3))
            wf, wb = chain_lags(O)
            rec = learn(Q, O, "qcubic+beats", "joint", range(4))
            net = Net(c, rec, held=range(4)).run(413)
            a += chain_ok(first_beats(net, 0, range(4)), [0, 1, 2, 3], wf)
            b += chain_ok(first_beats(net, 3, range(4)), [3, 2, 1, 0], wb)
            quiet += all(v is None for v in first_beats(net, None, range(4)).values())
            if gap in (6, 8, 10):
                free = Net(c, rec).run(600)
                for cue, chain, want, tag in ((0, [0, 1, 2, 3], wf, "f"), (3, [3, 2, 1, 0], wb, "b")):
                    own, last = roots(erase_cue(free, cue).run(1500))
                    good = own == [cue] and len(last) == 4 and all(
                        abs(((last[chain[i + 1]] - last[chain[i]]) % 59) - want[i]) <= 1
                        for i in range(3))
                    fa, fb = fa + (good and tag == "f"), fb + (good and tag == "b")
        out["joint_qcubic_beats_chain"][f"gap{gap}"] = {
            "held_cue0_of_12": a, "held_cue3_of_12": b, "silent_without_cue_of_12": quiet,
            "free_erase_cue0_keeps_0123_of_12": int(fa) if gap in (6, 8, 10) else None,
            "free_erase_cue3_keeps_3210_of_12": int(fb) if gap in (6, 8, 10) else None}
        print("joint chain", gap, out["joint_qcubic_beats_chain"][f"gap{gap}"], flush=True)


def main():
    out = {"spec": {"seeds": SEEDS, "threshold_default": 0.3, "refractory": REFR, "latency": LAT,
                    "rows": ROWS_T, "beat_ticks": BEAT_K, "ridge": RIDGE},
           "stability": {}, "roots": {}, "scalar": {}, "fork": {}, "joint_qcubic_beats_chain": {}}
    stability_and_roots(out)
    scalar_control(out)
    fork(out)
    best_receptor(out)
    (ROOT / "results/round7.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round7.json")


if __name__ == "__main__":
    main()

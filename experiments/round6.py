"""Sixth round (Fable 5.2): the fair comparisons for round five.

1. Is the lookup table doing anything a plain linear filter cannot? Four receptors are taught
   on exactly the same hold-and-release data with the same nearest-predecessor credit:

     table        round five: a table over the neighbour's last 1-3 rows
     rows_linear  one linear filter over the neighbour's last 3 rows (3 x 16 numbers);
                  this is R = sum_tau h(tau) . G(t - tau)
     beat_linear  one linear filter over the neighbour's last 24 ticks of beat onsets;
                  an ordinary temporal filter that never sees the checkerboard
     both_linear  the two linear inputs together

   The linear filters are ridge least-squares fits to the same credit signal.

2. Does it survive a free colony? Round five tested with units 0-3 held silent. Here nothing
   is held at test, so every unit keeps its own 59-tick beat, and three things are measured:

     settle       what order the free colony falls into once the receptors are switched on
     single cue   whether one cue, at any phase of the cycle, changes that order
     erase+cue    hold the four units with the rhythm, release them together, cue one end
                  within 25 ticks, then leave the colony alone: which order does it keep

   A colony is in state F if units 0-3 beat 0->1->2->3 with every hop within one tick of the
   taught lag, B for 3->2->1->0 likewise, and 'other' for anything else.

Run: python experiments/round6.py        Writes: results/round6.json
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
import round5 as r5  # noqa: E402
from gn.core import G  # noqa: E402
from round5 import N, AMP, WAVE, LAT, REFR, THR, sq, row_ids  # noqa: E402

SEEDS, TRIALS, WINDOW = 12, 8, 80
ROWS_T, BEAT_K, RIDGE = 3, 24, 1e-3


_VEC: dict = {}


def row_vec(i):
    """The 16 numbers of the checkerboard row with id i (ids are handed out as rows appear)."""
    if i not in _VEC:
        for k, j in r5._ROW_ID.items():
            _VEC.setdefault(j, np.frombuffer(k, dtype=G.dtype).astype(float))
    return _VEC[i]


def row_matrix(ids):
    return np.array([row_vec(int(i)) for i in ids])


def features(ids, ons, src, kind):
    """One row of inputs per tick for a listener watching unit `src`."""
    n = len(ids)
    parts = []
    if kind in ("rows_linear", "both_linear"):
        v = row_matrix(ids[:, src])
        parts.append(np.hstack([np.vstack([np.zeros((d, 16)), v[:n - d]]) for d in range(ROWS_T)]))
    if kind in ("beat_linear", "both_linear"):
        b = ons[:, src].astype(float)
        parts.append(np.stack([np.concatenate([np.zeros(d), b[:n - d]]) for d in range(BEAT_K)], 1))
    return np.hstack(parts + [np.ones((n, 1))])


def learn_linear(ids, ons, kind):
    credit = r5.nearest_predecessor(ons)
    filt = [[None] * N for _ in range(N)]
    n = len(ids)
    for src in range(N):
        x = features(ids, ons, src, kind)[:n - LAT]
        gram = np.linalg.inv(x.T @ x + RIDGE * np.eye(x.shape[1]))
        for dst in range(4):
            if dst != src:
                y = (credit[LAT:, dst] == src).astype(float)
                filt[dst][src] = gram @ (x.T @ y)
    return {"kind": kind, "filt": filt}


class Player:
    """Frozen receptors, round five's waveform trigger and refractory. `held` keeps units
    0-3 silent with the rhythm (round five's test); held=False is a free colony."""

    def __init__(self, base, receptor, held=True):
        self.c = copy.deepcopy(base)
        self.rec, self.held = receptor, held
        self.ids = [row_ids(self.c.q)] * ROWS_T
        self.beats = [np.zeros(N)] * BEAT_K
        self.wave_at = np.full(N, -1)
        self.last = np.full(N, -999)
        self.prev = np.zeros(N, bool)
        self._x = {}

    def inputs(self, src):
        """What a linear receptor watching `src` is shown this tick (cached per tick)."""
        if src not in self._x:
            kind, parts = self.rec["kind"], []
            if kind in ("rows_linear", "both_linear"):
                parts.append(np.concatenate([row_vec(int(self.ids[-1 - d][src]))
                                             for d in range(ROWS_T)]))
            if kind in ("beat_linear", "both_linear"):
                parts.append(np.array([self.beats[-1 - d][src] for d in range(BEAT_K)]))
            self._x[src] = np.concatenate(parts + [np.ones(1)])
        return self._x[src]

    def says_go(self, dst, src):
        rec = self.rec
        thr = rec.get("thr", THR)
        if "tables" in rec:
            for T in sorted(rec["tables"], reverse=True):
                e = rec["tables"][T][dst][src].get(tuple(int(i[src]) for i in self.ids[-T:]))
                if e and e[1] >= 3:
                    return e[0] > thr * e[1]
            return False
        return float(self.inputs(src) @ rec["filt"][dst][src]) > thr

    def tick(self, cue=None):
        c = self.c
        self._x = {}
        if self.rec is not None:
            for dst in range(4):
                if self.wave_at[dst] >= 0 or c.t - self.last[dst] < REFR:
                    continue
                if any(self.says_go(dst, src) for src in range(N) if src != dst):
                    self.wave_at[dst] = 0
                    self.last[dst] = c.t
        if cue is not None and self.wave_at[cue] < 0:
            self.wave_at[cue] = 0
            self.last[cue] = c.t
        force = np.full(N, np.nan)
        for u in range(N):
            if self.wave_at[u] >= 0:
                force[u] = WAVE[self.wave_at[u]]
                self.wave_at[u] = self.wave_at[u] + 1 if self.wave_at[u] < len(WAVE) - 1 else -1
        x = np.zeros(N)
        if self.held:
            x[:4] = AMP * sq(c.t)
        own = c.step(force=force, ext=x)
        loud = own > 3
        onset = loud & ~self.prev
        self.prev = loud
        self.ids = self.ids[1:] + [row_ids(c.q)]
        self.beats = self.beats[1:] + [onset.astype(float)]
        self.last = np.where(onset, c.t, self.last)
        return onset


def probe(player, cue):
    p = copy.deepcopy(player)
    first = [None] * 4
    for k in range(WINDOW):
        on = p.tick(cue if k == 0 else None)
        for u in range(4):
            if on[u] and first[u] is None:
                first[u] = k
    return first


def evaluate(base, receptor, want, held):
    p = Player(base, receptor, held)
    for _ in range(240):
        p.tick()
    rows = []
    for _ in range(TRIALS):
        for _ in range(173):
            p.tick()
        a, b, z = probe(p, 0), probe(p, 3), probe(p, None)
        ja, jb = r5.judge(a, 0, want[0]), r5.judge(b, 3, want[3])
        rows.append({"cue0_timed": ja[1], "cue3_timed": jb[1],
                     "cue0_wrong_order": r5.judge(a, 3, None)[0],
                     "cue3_wrong_order": r5.judge(b, 0, None)[0],
                     "nocue_0123_timed": r5.judge(z, 0, want[0])[1],
                     "nocue_3210_timed": r5.judge(z, 3, want[3])[1]})
    return rows


def state(player, want, ticks=240):
    """Run `ticks` and name the order units 0-3 are beating in."""
    p = copy.deepcopy(player)
    ev = [[] for _ in range(4)]
    for k in range(ticks):
        on = p.tick()
        for u in range(4):
            if on[u]:
                ev[u].append(k)
    if any(len(e) < 2 for e in ev):
        return "silent"
    last = [e[-1] for e in ev]
    per = int(np.median(np.diff(ev[0])))

    def ok(chain, w):
        return None not in w and all(
            min((last[chain[i + 1]] - last[chain[i]] - w[i]) % per,
                (w[i] - last[chain[i + 1]] + last[chain[i]]) % per) <= 1 for i in range(3))
    return "F" if ok([0, 1, 2, 3], want[0]) else "B" if ok([3, 2, 1, 0], want[3]) else "other"


def run(p, ticks, cue=None):
    for k in range(ticks):
        p.tick(cue if k == 0 else None)
    return p


def erase_and_cue(player, cue, delay, hold=160, settle=600):
    p = copy.deepcopy(player)
    while p.c.t % 8:
        p.tick()
    p.held = True
    run(p, hold)
    p.held = False
    run(p, delay)
    run(p, settle, cue)
    return p


def receptor(kind, ids, ons, thr=THR):
    if kind == "none":
        return None
    rec = {"tables": r5.learn(ids, ons)} if kind == "table" else learn_linear(ids, ons, kind)
    rec["thr"] = thr
    return rec


def tally(names):
    return {k: names.count(k) for k in ("F", "B", "other", "silent") if names.count(k)}


def main():
    out = {"spec": {"seeds": SEEDS, "threshold": THR, "refractory": REFR, "latency": LAT,
                    "rows_in_linear_filter": ROWS_T, "beat_ticks_in_linear_filter": BEAT_K,
                    "ridge": RIDGE, "erase_hold_ticks": 160,
                    "cue_delays_after_release": [0, 5, 10, 15, 20, 25]},
           "held": {}, "free": {}}
    taught = {}

    def data(kind, gap, seed):
        if (kind, gap, seed) not in taught:
            taught[(kind, gap, seed)] = r5.teach(kind, seed, gap)
        return taught[(kind, gap, seed)]

    # 1. the round-five test (units held), four receptors on the same teaching data
    for gap in (5, 6, 7, 8, 9, 10, 12, 16):
        for kind, thr in (("table", 0.3), ("rows_linear", 0.3), ("beat_linear", 0.3),
                          ("beat_linear", 0.2), ("both_linear", 0.3)):
            n0 = n3 = quiet = 0
            for seed in range(SEEDS):
                base, ids, ons = data("release_AB", gap, seed)
                want = r5.taught_hops(ons)
                p = run(Player(base, receptor(kind, ids, ons, thr), True), 413)
                n0 += r5.judge(probe(p, 0), 0, want[0])[1]
                n3 += r5.judge(probe(p, 3), 3, want[3])[1]
                quiet += all(x is None for x in probe(p, None))
            name = f"{kind}_thr{thr}_gap{gap}"
            out["held"][name] = {"cue0_timed_of_12": n0, "cue3_timed_of_12": n3,
                                 "silent_without_cue_of_12": quiet}
            print("held", name, out["held"][name], flush=True)

    # 2. the free colony
    for gap, kind, teach_kind in ((6, "rows_linear", "release_AB"), (8, "rows_linear", "release_AB"),
                                  (10, "rows_linear", "release_AB"), (6, "table", "release_AB"),
                                  (8, "table", "release_AB"), (10, "table", "release_AB"),
                                  (8, "beat_linear", "release_AB"), (10, "beat_linear", "release_AB"),
                                  (8, "none", "release_AB"), (8, "rows_linear", "release_random")):
        settle, later, single = [], [], {0: [], 3: []}
        ec = {0: [], 3: [], None: []}
        keep = []
        for seed in range(SEEDS):
            base, ids, ons = data(teach_kind, gap, seed)
            want = r5.taught_hops(data("release_AB", gap, seed)[2])
            c = copy.deepcopy(base)
            r5.release(c, list(np.random.default_rng(70 + seed).permutation(4)), 13)
            p = run(Player(c, receptor(kind, ids, ons), held=False), 1500)
            settle.append(state(p, want))
            later.append(state(run(copy.deepcopy(p), 3000), want))
            if kind == "rows_linear" and teach_kind == "release_AB" and gap in (6, 8):
                for cue in (0, 3):
                    for ph in range(0, 59, 3):
                        q = run(copy.deepcopy(p), ph)
                        single[cue].append((settle[-1], state(run(q, 600, cue), want)))
            for cue in (0, 3, None):
                for delay in (0, 5, 10, 15, 20, 25):
                    q = erase_and_cue(p, cue, delay)
                    s = state(q, want)
                    ec[cue].append(s)
                    if delay == 10 and cue is not None:
                        keep.append(s == state(run(q, 3000), want) and s in ("F", "B"))
        res = {"settled": tally(settle),
               "same_state_3000_ticks_later_of_12": sum(a == b for a, b in zip(settle, later)),
               "erase_then_cue0": tally(ec[0]), "erase_then_cue3": tally(ec[3]),
               "erase_no_cue": tally(ec[None]),
               "written_order_kept_3000_ticks_of_24": sum(keep)}
        if single[0]:
            for cue in (0, 3):
                moved = [(a, b) for a, b in single[cue] if a in ("F", "B")]
                res[f"single_cue{cue}_from_F_or_B"] = {
                    "trials": len(moved), "unchanged": sum(a == b for a, b in moved),
                    "flipped": sum({a, b} == {"F", "B"} for a, b in moved),
                    "broken": sum(b not in ("F", "B") for a, b in moved)}
        name = f"{kind}_gap{gap}" + ("" if teach_kind == "release_AB" else "_random_order_teaching")
        out["free"][name] = res
        print("free", name, json.dumps(res), flush=True)
    (ROOT / "results/round6.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round6.json")


if __name__ == "__main__":
    main()

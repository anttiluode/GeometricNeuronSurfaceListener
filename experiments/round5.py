"""Fifth round (Fable 5.2): a receptor learned from a neighbour's checkerboard rows.

Round three taught a chain with a tally of beat times. Round four showed that a unit's recent
rows say more than its beat times. Here each unit learns, for each neighbour, a receptor over
that neighbour's last T rows: a table of how often the unit's own beat followed LAT ticks after
each short row sequence. Nothing else is learned and no connection weight is changed (all
edges stay at 0.02). At test a unit starts a beat when a neighbour shows a row sequence its
table has seen precede its own beat more than THR of the time.

Teaching is round three's: hold and release, alternating 0->1->2->3 and 3->2->1->0, outputs
never forced. Every colony is scrambled by a random-order release before testing.

Two things here are hand-written and on only at test:
  the trigger   plays the unit's own recorded beat (four lead-up outputs, two beat outputs),
                so a triggered beat shows the same rows as a natural one
  refractory    a unit ignores its receptors for 30 ticks after it last started or made a beat

Question: does the chain replay in the cued order AND at the taught spacing? The beat tally
of round three replays at a fixed 5 ticks per hop whatever was taught.

Run: python experiments/round5.py        Writes: results/round5.json
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
from round3 import N, OFF, AMP  # noqa: E402

SEEDS, TRIALS = 12, 8
REFR, THR, LAT, WINDOW = 30, 0.3, 9, 80
_ROW_ID: dict = {}


def row_ids(q):
    return np.array([_ROW_ID.setdefault(G[x - QMIN].tobytes(), len(_ROW_ID)) for x in q])


def natural_wave():
    """The six outputs a free unit writes on its way into a beat (4 lead-up, 2 beat)."""
    c = Colony(1)
    outs, owns = [], []
    for _ in range(1500):
        owns.append(c.step()[0])
        outs.append(float(c.pipe[-1][0]))
    on = [i for i in range(1300, 1499) if owns[i] > 3 and owns[i - 1] <= 3][0]
    return np.array(outs[on - 8:on - 2])


WAVE = natural_wave()


def record(c, ticks_fn):
    """Run a teaching episode, returning row ids [t, N] and beat onsets [t, N]."""
    ids, ons = [], []
    prev = np.zeros(N, bool)

    def watch(col):
        nonlocal prev
        loud = col.own > 3
        ids.append(row_ids(col.q))
        ons.append(loud & ~prev)
        prev = loud
    ticks_fn(c, watch)
    return np.array(ids), np.array(ons)


def sq(t):
    return 1.0 if (t % 8) < 4 else -1.0


def hold_ext(c, until):
    x = np.zeros(N)
    for u, tu in until.items():
        if c.t < tu:
            x[u] = AMP * sq(c.t)
    return x


def release(c, order, gap, watch=None, hold=160, free=340):
    """Round three's hold and release, with the hold aligned to the rhythm so that every
    block writes the same lags."""
    while c.t % 8:
        c.step()
        if watch:
            watch(c)
    until = {u: c.t + hold + r * gap for r, u in enumerate(order)}
    for _ in range(hold + 3 * gap + free):
        c.step(ext=hold_ext(c, until))
        if watch:
            watch(c)


def teach(kind, seed, gap, w=0.0):
    c = Colony(N, w=np.full((N, N), w) * OFF, rng=np.random.default_rng(seed))
    rng = np.random.default_rng(500 + seed)

    def episode(col, watch):
        for b in range(16):
            fwd = b % 2 == 0
            if kind == "release_AB":
                release(col, [0, 1, 2, 3] if fwd else [3, 2, 1, 0], gap, watch)
            elif kind == "release_random":
                release(col, list(rng.permutation(4)), gap, watch)
            else:
                for _ in range(500):
                    col.step()
                    watch(col)
    ids, ons = record(c, episode)
    return c, ids, ons


def key(ids_window, ordered):
    return tuple(ids_window) if ordered else tuple(sorted(ids_window))


def nearest_predecessor(ons, reach=29):
    """credit[t, dst] = the unit whose beat most recently preceded dst's beat at t (within
    `reach` ticks), or -1. This is Sol's nearest-wins competition from the earlier repo."""
    n = len(ons)
    credit = np.full((n, N), -1)
    last = np.full(N, -10_000)
    for t in range(n):
        for dst in np.flatnonzero(ons[t]):
            age = t - last
            age[dst] = 10_000
            src = int(np.argmin(age))
            if 1 <= age[src] <= reach:
                credit[t, dst] = src
        last[ons[t]] = t
    return credit


def learn(ids, ons, depths=(1, 2, 3), ordered=True):
    """tables[T][dst][src][row sequence] = [credited, seen].

    'seen' counts every time src showed that row sequence. 'credited' counts the times dst
    then beat LAT ticks later with src as its nearest predecessor. So at its own beat a unit
    looks back LAT ticks at what the neighbour that beat just before it was showing."""
    credit = nearest_predecessor(ons)
    out = {}
    n = len(ids)
    for T in depths:
        tables = [[{} for _ in range(N)] for _ in range(N)]
        for t in range(T - 1, n - LAT):
            fut = credit[t + LAT]
            for src in range(N):
                k = key(ids[t - T + 1:t + 1, src], ordered)
                for dst in range(N):
                    if dst != src:
                        e = tables[dst][src].setdefault(k, [0, 0])
                        e[0] += fut[dst] == src
                        e[1] += 1
        out[T] = tables
    return out


class Player:
    """The colony at test: frozen receptors, waveform trigger, refractory. Units 0-3 are held
    silent by the rhythm throughout, so the only beats are cued or triggered ones."""

    def __init__(self, base, tables, ordered=True):
        self.c = copy.deepcopy(base)
        self.tables, self.ordered = tables, ordered
        self.depths = sorted(tables, reverse=True) if tables else []
        self.hist = [row_ids(self.c.q)] * 3
        self.wave_at = np.full(N, -1)
        self.last = np.full(N, -999)
        self.prev = np.zeros(N, bool)

    def says_go(self, dst, src, h):
        for T in self.depths:                    # the longest row sequence it has seen decides
            e = self.tables[T][dst][src].get(key(h[-T:, src], self.ordered))
            if e and e[1] >= 3:
                return e[0] > THR * e[1]
        return False

    def tick(self, cue=None):
        c = self.c
        if self.tables:
            h = np.array(self.hist)
            for dst in range(4):
                if self.wave_at[dst] >= 0 or c.t - self.last[dst] < REFR:
                    continue
                if any(self.says_go(dst, src, h) for src in range(N) if src != dst):
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
        x[:4] = AMP * sq(c.t)
        own = c.step(force=force, ext=x)
        self.hist = self.hist[1:] + [row_ids(c.q)]
        loud = own > 3
        onset = loud & ~self.prev
        self.prev = loud
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


def taught_hops(ons):
    """The lags teaching actually wrote: modal gap from each unit to the next in line,
    forward (0->1->2->3) and backward (3->2->1->0)."""
    def modal(a, b):
        ta, tb = np.flatnonzero(ons[:, a]), np.flatnonzero(ons[:, b])
        d = [int(x - ta[ta < x][-1]) for x in tb if (ta < x).any()]
        d = [x for x in d if 1 <= x <= 29]
        return int(np.bincount(d).argmax()) if d else None
    return {0: [modal(0, 1), modal(1, 2), modal(2, 3)], 3: [modal(3, 2), modal(2, 1), modal(1, 0)]}


def judge(first, head, want):
    chain = [0, 1, 2, 3] if head == 0 else [3, 2, 1, 0]
    t = [first[u] for u in chain]
    if any(x is None for x in t):
        return 0, 0, None
    hops = [t[i + 1] - t[i] for i in range(3)]
    order = int(all(h > 0 for h in hops))
    timed = int(order and want is not None and None not in want
                and all(abs(h - w) <= 1 for h, w in zip(hops, want)))
    return order, timed, (hops if order else None)


def evaluate(base, tables, ordered, want):
    p = Player(base, tables, ordered)
    for _ in range(240):
        p.tick()
    rows = []
    for _ in range(TRIALS):
        for _ in range(173):
            p.tick()
        a, b, z = probe(p, 0), probe(p, 3), probe(p, None)
        ja, jb = judge(a, 0, want[0]), judge(b, 3, want[3])
        rows.append({"cue0_order": ja[0], "cue0_timed": ja[1], "cue3_order": jb[0],
                     "cue3_timed": jb[1], "cue0_wrong": judge(a, 3, None)[0],
                     "cue3_wrong": judge(b, 0, None)[0],
                     "nocue_any_beat": int(any(x is not None for x in z)),
                     "hops": (ja[2] or []) + (jb[2] or [])})
    return rows


def summarise(rows):
    res = {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != "hops"}
    hops = [h for r in rows for h in r["hops"]]
    res["median_hop_ticks"] = float(np.median(hops)) if hops else None
    res["n"] = len(rows)
    return res


def main():
    out = {"spec": {"seeds": SEEDS, "trials_per_seed": TRIALS, "refractory": REFR,
                    "threshold": THR, "latency": LAT, "window": WINDOW,
                    "wave": [round(float(x), 4) for x in WAVE],
                    "timed_means": "every hop within 1 tick of the lag teaching actually wrote for that pair"},
           "conditions": {}}
    cache = {}

    def run(name, kind, gap, depths, ordered):
        rows, wants = [], []
        for seed in range(SEEDS):
            if (kind, gap, seed) not in cache:
                cache[(kind, gap, seed)] = teach(kind, seed, gap)
            base, ids, ons = cache[(kind, gap, seed)]
            want = taught_hops(ons)
            wants.append(want[0] + want[3])
            rows += evaluate(base, learn(ids, ons, depths, ordered), ordered, want)
        res = summarise(rows)
        w = [x for ws in wants for x in ws if x is not None]
        res["taught_hop_ticks"] = sorted(set(w))
        out["conditions"][f"{name}_gap{gap}"] = res
        print(f"{name}_gap{gap}", json.dumps({k: (round(v, 3) if isinstance(v, float) else v)
                                              for k, v in res.items()}), flush=True)

    for gap in (5, 6, 7, 8, 9, 10, 12):
        run("receptor", "release_AB", gap, (1, 2, 3), True)
        run("receptor_order_thrown_away", "release_AB", gap, (1, 2, 3), False)
        run("receptor_one_row", "release_AB", gap, (1,), True)
    for gap in (6, 9):
        run("random_order_teaching", "release_random", gap, (1, 2, 3), True)
        run("untaught", "untaught", gap, (1, 2, 3), True)
    (ROOT / "results/round5.json").write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE results/round5.json")


if __name__ == "__main__":
    print("wave", WAVE.round(3))
    main()

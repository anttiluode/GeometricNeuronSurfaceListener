"""Second round (Fable 5.2): why the colony goes silent, and what the 8-tick rhythm can do.

Four measurements, all on the unchanged loop dynamics (quiet.py re-implements gn/core.py's
step so the heard signal's two routes can be separated; parity is tested).

  ripple    one unit, a small zero-mean square wave: which period and which route silence it
  fixes     six units, every listening rule, with three candidate repairs on and off
  release   hold a unit with the rhythm, let go: when does it beat next
  lags      write a lag between two units by staggered release; what each coupling does to it

Run: python experiments/round2.py        Writes: results/round2.json
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quiet import QuietColony  # noqa: E402


def sq(t, period=8):
    return 1.0 if (t % period) < period / 2 else -1.0


def count_beats(route, amp, period, seeds=8, ticks=1500, kind="square"):
    """Beats of one unit in the last 590 ticks, summed over starts (10 per start is normal).

    route: 'both' = the heard port as the original has it (drive and memory),
           'drive' = drive only, 'memory' = memory only, 'dc' = constant, 'noise' = Gaussian.
    """
    total = 0
    for s in range(seeds):
        c = QuietColony(1, mode="null", memory=(route != "drive"),
                        rng=np.random.default_rng(s))
        g = np.random.default_rng(100 + s)
        prev = False
        for t in range(ticks):
            if kind == "dc":
                v = amp
            elif kind == "noise":
                v = amp * g.standard_normal()
            else:
                v = amp * sq(t, period)
            x = np.array([v])
            own = c.step(ext=x if route != "memory" else None,
                         mod=x if route == "memory" else None)[0]
            loud = own > 3
            if t >= 910 and loud and not prev:
                total += 1
            prev = loud
    return total


def ripple():
    amps = (0.05, 0.1, 0.2, 0.3)
    periods = (2, 4, 6, 8, 10, 12, 16, 24, 40, 59)
    out = {"normal_total": 80,
           "square_by_period": {str(p): {str(a): count_beats("both", a, p) for a in amps}
                                for p in periods},
           "constant": {str(a): count_beats("both", a, 8, kind="dc")
                        for a in (-0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5)},
           "noise": {str(a): count_beats("both", a, 8, kind="noise")
                     for a in (0.05, 0.1, 0.2, 0.3)},
           "route_period8": {r: {str(a): count_beats(r, a, 8)
                                 for a in (0.05, 0.1, 0.2, 0.3, 0.5)}
                             for r in ("both", "drive", "memory")}}
    print("ripple", json.dumps(out), flush=True)
    return out


def survive(mode, w, seeds=8, n=6, ticks=1600, **kw):
    silent, rate = [], []
    for seed in range(seeds):
        c = QuietColony(n, W=np.full((n, n), w), mode=mode,
                        rng=np.random.default_rng(seed), **kw)
        prev = np.zeros(n, bool)
        nb = np.zeros(n, int)
        for t in range(ticks):
            loud = c.step() > 3
            if t >= ticks - 600:
                nb += loud & ~prev
            prev = loud
        silent.append(int((nb == 0).sum()))
        rate.append(float(nb.mean()))
    return {"silent_of_6": float(np.mean(silent)), "beats_per_unit_600": float(np.mean(rate))}


def fixes():
    out = {}
    for mode in ("surface", "raw", "shifted", "fixed", "fixed_taps"):
        out[mode] = {}
        for memory in (True, False):
            for comb in (False, True):
                for adapt in (False, True):
                    key = f"memory={int(memory)},comb={int(comb)},adapt={int(adapt)}"
                    out[mode][key] = {str(w): survive(mode, w, memory=memory, comb=comb,
                                                      adapt=adapt)
                                      for w in (0.02, 0.05, 0.10, 0.20)}
                    print("fixes", mode, key, json.dumps(
                        {w: v["silent_of_6"] for w, v in out[mode][key].items()}), flush=True)
    return out


def release():
    out = {}
    for amp in (0.1, 0.15, 0.2):
        for dur in (100, 200, 400, 403):
            first, during = [], []
            for s in range(48):
                c = QuietColony(1, mode="null", rng=np.random.default_rng(s))
                prev, ev = False, []
                t0, t1 = 900, 900 + dur
                for t in range(t1 + 400):
                    x = np.array([amp * sq(t)]) if t0 <= t < t1 else None
                    loud = c.step(ext=x)[0] > 3
                    if loud and not prev:
                        ev.append(t)
                    prev = loud
                ev = np.array(ev)
                during.append(int(((ev >= t0 + 40) & (ev < t1)).sum()))
                after = ev[ev >= t1]
                first.append(int(after[0] - t1) if len(after) else -1)
            cnt = collections.Counter(first)
            out[f"amp={amp},held={dur}"] = {
                "beats_while_held_after_40_ticks": int(np.sum(during)),
                "first_beat_after_release": {str(k): v for k, v in sorted(cnt.items())}}
            print("release", amp, dur, dict(sorted(cnt.items())), flush=True)
    # six uncoupled units released 8 ticks apart: do they beat in the order of release?
    order = {"held_and_released": 0, "never_held": 0, "trials": 24}
    for s in range(24):
        for held in (True, False):
            c = QuietColony(6, mode="null", rng=np.random.default_rng(s))
            first = np.full(6, -1)
            prev = np.zeros(6, bool)
            for t in range(1100):
                x = np.array([0.2 * sq(t) if held and 300 <= t < 700 + 8 * i else 0.0
                              for i in range(6)])
                loud = c.step(ext=x) > 3
                on = loud & ~prev & (first < 0) & (t >= 700 + 8 * np.arange(6))
                first[on] = t
                prev = loud
            if (first >= 0).all() and list(np.argsort(first, kind="stable")) == list(range(6)) \
                    and len(set(first)) == 6:
                order["held_and_released" if held else "never_held"] += 1
    out["six_units_released_in_order"] = order
    print("release order", order, flush=True)
    return out


def lag_run(mode, w, stagger, ticks=3000):
    c = QuietColony(2, W=np.zeros((2, 2)), mode=mode, rng=np.random.default_rng(1))
    rel = [700, 700 + stagger]
    ton = rel[1] + 60
    ev = [[], []]
    prev = np.zeros(2, bool)
    for t in range(ton + ticks):
        x = np.array([0.2 * sq(t) if 300 <= t < rel[i] else 0.0 for i in range(2)])
        if t == ton:
            c.weights = np.array([[0, w], [w, 0.0]])
        loud = c.step(ext=x) > 3
        for i in range(2):
            if loud[i] and not prev[i]:
                ev[i].append(t)
        prev = loud
    lo = ton + ticks - 400
    a = np.array([e for e in ev[0] if e >= lo])
    b = np.array([e for e in ev[1] if e >= lo])
    if len(a) < 3 or len(b) < 1:
        return None
    period = int(np.median(np.diff(a)))
    p = a[a <= b[-1]]
    return int((b[-1] - p[-1]) % period) if len(p) else None


def lags():
    written = [lag_run("null", 0.0, d) for d in range(59)]
    out = {"written_lags_reachable": sorted(set(written))}
    for mode, w in (("null", 0.0), ("surface", 0.1), ("surface", 0.2), ("fixed_taps", 0.05),
                    ("fixed_taps", 0.1), ("fixed_taps", 0.15)):
        fin = [lag_run(mode, w, d) for d in range(59)]
        cnt = collections.Counter(f for f in fin if f is not None)
        moved = sum(1 for a, b in zip(written, fin)
                    if b is not None and min((a - b) % 59, (b - a) % 59) > 1)
        out[f"{mode},w={w}"] = {"distinct_final_lags": len(cnt), "moved_of_59": moved,
                                "silent_pairs": sum(f is None for f in fin),
                                "final_lag_counts": {str(k): v for k, v in sorted(cnt.items())}}
        print("lags", mode, w, {k: v for k, v in out[f"{mode},w={w}"].items()
                                if k != "final_lag_counts"}, flush=True)
    return out


def main():
    data = {"date": "2026-11-10", "ripple": ripple(), "release": release(), "lags": lags(),
            "fixes": fixes()}
    path = ROOT / "results/round2.json"
    path.write_text(json.dumps(data, indent=1) + "\n")
    print("WROTE", path)


if __name__ == "__main__":
    main()

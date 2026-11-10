"""Surface listening with the heard signal's route into the unit made explicit.

Second round (Fable 5.2). gn/core.py is still untouched; this module re-implements its step so
that the two things the original does with a heard signal can be separated:

    drive   the heard signal is added to the reading R that the controller turns into output
    memory  the heard signal is written into the 50-sample history whose variance decides
            whether the unit damps or amplifies (the "forgetting clock")

and so that the heard signal can be passed through a two-tap comb, y(t) = (x(t) + x(t-4)) / 2,
which removes exactly the 8-tick ripple (8 = twice the loop delay) and its odd harmonics.

With memory=True, comb=False this is the original loop plus Sol's SurfaceColony, to numerical
precision (tests/test_quiet.py).

A third input, `mod`, is written into the memory but NOT into the drive: a rhythm that can hold
a unit's variance up without pushing its output. It is an engineered port, not part of ecg.json.
"""
from __future__ import annotations

import numpy as np
from gn.core import G, QMIN, S4, TARGET, O0, q_of, damp, amplify
from surface import overlap_matrix

D, L = 4, 50


class QuietColony:
    def __init__(self, n, W=None, mode="surface", gain=3.5, memory=True, comb=False,
                 adapt=False, rng=None):
        self.n, self.mode, self.gain = n, mode, float(gain)
        self.memory, self.comb, self.adapt = memory, comb, adapt
        self.heard_hist = np.zeros((L, n))       # last 50 heard values, for adaptation
        self.hcount = 0
        self.weights = np.full((n, n), 0.10) if W is None else np.array(W, dtype=float)
        np.fill_diagonal(self.weights, 0.0)
        self.hist = np.zeros((n, L))
        self.count = 0
        self.pipe = np.full((D, n), np.nan)
        self.pipe[-1] = O0
        if rng is not None:                      # same draws, same order as gn.core.Colony
            self.pipe = rng.uniform(0.3, 1.0, size=(D, n))
            self.hist = rng.uniform(0.0, 1.6, size=(n, L))
            self.count = L
        self.heard_log = np.zeros((D + 1, n))    # raw heard signal, newest first
        self.t = 0
        self.q = np.zeros(n, dtype=int)
        self.var = np.zeros(n)
        self.heard = np.zeros(n)
        self.k = np.zeros((n, n))

    def step(self, ext=None, force=None, mod=None):
        n = self.n
        src = self.pipe[0]
        live = ~np.isnan(src)
        q = q_of(np.where(live, src, 0.0))
        self.q = q
        own = np.where(live, S4[0, q - QMIN], 0.0)
        rows = G[q - QMIN].copy()
        rows[~live] = 0.0
        k = overlap_matrix(rows, self.mode)
        g = 1.0 if self.mode == "fixed_taps" else (0.0 if self.mode == "null" else self.gain)
        raw = g * np.sum(self.weights * k, axis=1)
        self.heard_log = np.roll(self.heard_log, 1, axis=0)
        self.heard_log[0] = raw
        heard = 0.5 * (self.heard_log[0] + self.heard_log[D]) if self.comb else raw
        if self.adapt:                           # hear only the departure from the 50-tick mean
            m = min(self.hcount, L)
            base = self.heard_hist[:m].mean(axis=0) if m else np.zeros(n)
            self.heard_hist[self.hcount % L] = heard
            self.hcount += 1
            heard = heard - base
        if ext is not None:
            heard = heard + np.asarray(ext)
        R = own + heard
        remembered = R if self.memory else own
        if mod is not None:
            remembered = remembered + np.asarray(mod)
        self.hist[:, self.count % L] = remembered
        self.count += 1
        var = np.zeros(n)
        if self.count > 10:
            m = min(self.count, L)
            idx = (self.count - 1 - np.arange(m)) % L
            var = np.var(self.hist[:, idx], axis=1)
        hot = var > TARGET
        o = np.where(hot, damp(R), amplify(R, var))
        if force is not None:
            o = np.where(np.isnan(force), o, force)
        self.pipe = np.vstack([self.pipe[1:], o[None, :]])
        self.var, self.heard, self.k = var, heard, k
        self.t += 1
        return own

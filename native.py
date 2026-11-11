"""The loop with its setpoint port open.

In ecg.json the Homeostatic Coupler has three input ports. `signal_in` carries the four
splitter wires. `setpoint_mod` carries a constant 1.0, which the node turns into
setpoint = 0.5 + 0.1 * (sum of everything wired to setpoint_mod) = 0.6. `gain_mod` is read
but never used in edge_of_chaos mode (the node computes effective_gain and then multiplies
by self.gain), so it is a dead port.

Every round so far kept the setpoint fixed at 0.6 and sent neighbours into signal_in. Here a
neighbour's splitter outputs can also be wired to setpoint_mod, with a weight, exactly as
Perception Lab would sum them. Nothing else changes: same tables, same variance rule.

    m_i(t)  = sum_j v[i, j] * (taps_j[a] + taps_j[a + 1])     what i hears on setpoint_mod
    S_i(t)  = 0.5 + 0.1 * (1.0 + m_i(t) + sp_ext_i(t))
    o_i(t)  = damp or amplify around S_i(t), as before

With v = 0 and no sp_ext this is gn/core.py's Colony exactly (tests/test_native.py).
"""
from __future__ import annotations

import numpy as np
from gn.core import Colony, G, QMIN, S4, TARGET, q_of


class SetpointColony(Colony):
    def __init__(self, n, v=None, sp_tap=0, **kw):
        super().__init__(n, **kw)
        self.v = np.zeros((n, n)) if v is None else np.array(v, dtype=float)
        self.sp_tap = sp_tap
        self.S = np.full(n, 0.6)

    def step(self, ext=None, sp_ext=None, force=None):
        n = self.n
        src = self.pipe[0]
        live = ~np.isnan(src)
        q = q_of(np.where(live, src, 0.0))
        self.q = q
        own = np.where(live, S4[0, q - QMIN], 0.0)
        heard = S4[self.tap, q[None, :] - QMIN]
        np.fill_diagonal(heard, 0.0)
        R = own + (self.w * heard).sum(axis=1)
        if ext is not None:
            R = R + ext
        self.hist[:, self.count % self.L] = R
        self.count += 1
        var = np.zeros(n)
        if self.count > 10:
            m = min(self.count, self.L)
            idx = (self.count - 1 - np.arange(m)) % self.L
            var = np.var(self.hist[:, idx], axis=1)
        a = self.sp_tap
        beat_wires = np.where(live, G[q - QMIN, a] + G[q - QMIN, a + 1], 0.0)   # what j sends
        m_in = self.v @ beat_wires
        if sp_ext is not None:
            m_in = m_in + sp_ext
        S = 0.5 + 0.1 * (1.0 + m_in)
        hot = var > TARGET
        o = np.where(hot, S + (2 / (1 + np.exp(-3 * (R - S))) - 1) / 3,
                     S + np.tanh(2 * (R - S) * (1 + 10 * np.abs(var - TARGET))))
        if force is not None:
            o = np.where(np.isnan(force), o, force)
        self.pipe = np.vstack([self.pipe[1:], o[None, :]])
        self.var, self.mode, self.R, self.own, self.S = var, np.where(hot, -1, 1), R, own, S
        self.t += 1
        return own

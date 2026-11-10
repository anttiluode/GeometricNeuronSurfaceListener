"""State-as-receptor coupling between exact archived ECG loop copies.

The original gn.core.Colony is copied UNMODIFIED from ReturnToGeometricNeuron.
This wrapper sets its inter-unit edge weights to zero and supplies the alternate
listening operator through the existing ext port. Thus the controller, history,
spatial lookup, quantizer, and four-tick pipeline are all identical to the parent.

Speaker j broadcasts row G[q_j], listener i exposes its own row G[q_i].
For the centered surface operator K(i,j)=<norm(G_i-mean_i),
norm(G_j-mean_j)>, an equal-time no-lag K is symmetric. The receiver's input is
    R_i = self_taps_i + gain * sum_{j != i} W[i,j] K(i,j).
No plasticity or cue-specific switching is installed.

Controls:
  surface      centered, normalized moving listener surface (Fable hypothesis)
  raw          literal nonnegative dot / 4 (tests role of centering)
  fixed        fixed q=43/48 average listener surface, same centered normalization
  shifted      each receiver's row circularly misregistered by 4 samples
  fixed_taps   exact parent output taps 6..9 (same weights)
  null         no neighbour coupling
"""
from __future__ import annotations

import copy
import numpy as np
from gn.core import Colony, G, QMIN, S4, q_of

MODES = ("surface", "raw", "fixed", "shifted", "fixed_taps", "null")
EPS = 1e-12


def normalized_centered(rows: np.ndarray) -> np.ndarray:
    r = np.asarray(rows, dtype=np.float64)
    centered = r - np.mean(r, axis=-1, keepdims=True)
    norm = np.linalg.norm(centered, axis=-1, keepdims=True)
    return np.divide(centered, norm, out=np.zeros_like(centered),
                     where=norm > EPS)


_FIXED_TEMPLATE = normalized_centered(
    0.5 * (G[43 - QMIN] + G[48 - QMIN])[None, :]
)[0]


def overlap_matrix(rows: np.ndarray, mode: str) -> np.ndarray:
    """Return unweighted coupling K_ij. Diagonal is always zero."""
    if mode not in MODES:
        raise ValueError(mode)
    n = len(rows)
    if mode == "surface":
        f = normalized_centered(rows)
        k = f @ f.T
    elif mode == "raw":
        k = (rows @ rows.T) / 4.0
    elif mode == "fixed":
        f = normalized_centered(rows)
        k = np.broadcast_to(_FIXED_TEMPLATE @ f.T, (n, n)).copy()
    elif mode == "shifted":
        f = normalized_centered(rows)
        k = np.roll(f, 4, axis=-1) @ f.T
    elif mode == "fixed_taps":
        k = np.broadcast_to(rows[:, 6:10].sum(axis=1), (n, n)).T.copy()
    else:
        k = np.zeros((n, n))
    np.fill_diagonal(k, 0.0)
    return k


class SurfaceColony:
    """A coupled colony; its underlying ECG loop is exactly gn.core.Colony.

    W[i,j] is the edge j->i; W is fixed throughout unless caller changes it.
    All variants get the same W, warm-up, forced pulses and simulation budget.
    """
    def __init__(self, n=2, W=None, mode="surface", gain=3.5, rng=None,
                 base: Colony | None = None):
        if mode not in MODES:
            raise ValueError(mode)
        self.core = copy.deepcopy(base) if base is not None else Colony(n, rng=rng)
        if self.core.n != n:
            raise ValueError("base size mismatch")
        self.core.w = np.zeros((n, n), dtype=np.float64)
        self.weights = (np.full((n, n), 0.10) if W is None
                        else np.asarray(W, dtype=np.float64).copy())
        if self.weights.shape != (n, n):
            raise ValueError("weight dimensions")
        np.fill_diagonal(self.weights, 0.0)
        self.mode = mode
        self.gain = float(gain)
        self.last_k = np.zeros((n, n))
        self.last_extra = np.zeros(n)

    def pre_step_rows(self) -> np.ndarray:
        src = self.core.pipe[0]
        live = ~np.isnan(src)
        q = q_of(np.where(live, src, 0.0))
        rows = G[q - QMIN].copy()
        rows[~live] = 0.0
        return rows

    def step(self, force=None, ext=None, kick=None):
        rows = self.pre_step_rows()
        k = overlap_matrix(rows, self.mode)
        extra = self.gain * np.sum(self.weights * k, axis=1)
        # For exact parent parity, the baseline is NOT scaled by 3.5:
        # the parent hears W[i,j] * sum G_j[6..9].
        if self.mode == "fixed_taps":
            extra = np.sum(self.weights * k, axis=1)
        if self.mode == "null":
            extra[:] = 0
        if ext is not None:
            extra = extra + np.asarray(ext)
        self.last_k = k
        self.last_extra = extra
        return self.core.step(ext=extra, force=force, kick=kick)

    @property
    def q(self):
        return self.core.q

    @property
    def t(self):
        return self.core.t


def aligned_two_unit_state(listener: Colony, speaker: Colony) -> Colony:
    """Join two settled one-unit states without corrupting ring indexing."""
    if listener.n != 1 or speaker.n != 1:
        raise ValueError("Only singleton states may be joined")
    if not (listener.d == speaker.d and listener.L == speaker.L):
        raise ValueError("Incompatible singleton histories")
    c = Colony(2, d=listener.d, W=listener.W[0])
    c.t, c.count = listener.t, listener.count
    c.pipe[:, 0] = listener.pipe[:, 0]
    c.pipe[:, 1] = speaker.pipe[:, 0]
    for unit, src in enumerate([listener, speaker]):
        for age in range(1, c.L + 1):
            c.hist[unit, (c.count - age) % c.L] = src.hist[0, (src.count - age) % src.L]
    # The baseline core's qlog is unused because its weights are zero.
    c.qlog[0, 0] = int(listener.q[0])
    c.qlog[0, 1] = int(speaker.q[0])
    return c

"""quiet.py must be the original loop when nothing is switched on."""
import unittest
import numpy as np
from surface import SurfaceColony
from quiet import QuietColony


class QuietTests(unittest.TestCase):
    def test_parity_with_surface_colony(self):
        for mode in ("surface", "raw", "shifted", "fixed", "fixed_taps", "null"):
            W = np.full((4, 4), 0.05)
            a = SurfaceColony(4, W=W, mode=mode, rng=np.random.default_rng(3))
            b = QuietColony(4, W=W, mode=mode, rng=np.random.default_rng(3))
            for _ in range(300):
                np.testing.assert_array_equal(a.step(), b.step())
                np.testing.assert_allclose(a.core.var, b.var, rtol=0, atol=1e-12)

    def test_free_period_is_59(self):
        c = QuietColony(1, mode="null")
        on, prev = [], False
        for t in range(2000):
            loud = c.step()[0] > 3
            if loud and not prev and t > 1300:
                on.append(t)
            prev = loud
        self.assertTrue(all(b - a == 59 for a, b in zip(on, on[1:])))

    def test_small_rhythm_at_period_8_silences_and_release_resets(self):
        firsts = []
        for s in range(6):
            c = QuietColony(1, mode="null", rng=np.random.default_rng(s))
            ev, prev = [], False
            for t in range(1600):
                x = np.array([0.2 * (1 if t % 8 < 4 else -1)]) if 900 <= t < 1200 else None
                loud = c.step(ext=x)[0] > 3
                if loud and not prev:
                    ev.append(t)
                prev = loud
            self.assertFalse([e for e in ev if 940 <= e < 1200])
            firsts.append([e for e in ev if e >= 1200][0] - 1200)
        self.assertEqual(len(set(firsts)), 1)


if __name__ == "__main__":
    unittest.main()

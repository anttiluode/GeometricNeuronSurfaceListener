"""native.py is the original loop when the setpoint port carries only its constant, and a
setpoint pulse makes a unit beat through its own feedback."""
import copy
import unittest
import numpy as np
from gn.core import Colony
from native import SetpointColony


class NativeTests(unittest.TestCase):
    def test_parity_with_core(self):
        a = Colony(3, rng=np.random.default_rng(1))
        b = SetpointColony(3, rng=np.random.default_rng(1))
        for _ in range(400):
            np.testing.assert_array_equal(a.step(), b.step())

    def test_setpoint_pulse_evokes_a_beat_four_ticks_later(self):
        c = SetpointColony(1)
        for _ in range(1330):
            c.step()
        quiet = copy.deepcopy(c)
        self.assertFalse(any(quiet.step()[0] > 3 for _ in range(8)))
        got = [c.step(sp_ext=np.array([-10.0]) if k < 2 else None)[0] > 3 for k in range(8)]
        self.assertEqual(got.index(True), 4)


if __name__ == "__main__":
    unittest.main()

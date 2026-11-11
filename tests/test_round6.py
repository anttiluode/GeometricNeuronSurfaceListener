"""A free colony keeps whichever taught order it is cued into after an erase."""
import copy
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import round5 as r5  # noqa: E402
import round6 as r6  # noqa: E402


class Round6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base, ids, ons = r5.teach("release_AB", 0, 8)
        cls.want = r5.taught_hops(ons)
        c = copy.deepcopy(base)
        r5.release(c, list(np.random.default_rng(70).permutation(4)), 13)
        cls.linear = r6.run(r6.Player(c, r6.receptor("rows_linear", ids, ons), held=False), 1500)
        cls.bare = r6.run(r6.Player(copy.deepcopy(c), None, held=False), 1500)

    def test_cue_chooses_the_order_the_free_colony_keeps(self):
        f = r6.erase_and_cue(self.linear, 0, 10)
        b = r6.erase_and_cue(self.linear, 3, 10)
        self.assertEqual(r6.state(f, self.want), "F")
        self.assertEqual(r6.state(b, self.want), "B")
        self.assertEqual(r6.state(r6.run(f, 1500), self.want), "F")
        self.assertEqual(r6.state(r6.run(b, 1500), self.want), "B")

    def test_without_receptors_no_order_is_kept(self):
        self.assertEqual(r6.state(r6.erase_and_cue(self.bare, 0, 10), self.want), "other")


if __name__ == "__main__":
    unittest.main()

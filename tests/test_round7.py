"""Round seven: a written order is a root on its own clock plus a triggered wave, and a
summed receptor resolves the shared-unit fork where pairwise receptors cannot."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import round7 as r  # noqa: E402


class Round7Tests(unittest.TestCase):
    def test_written_order_has_one_root_and_exact_cycles(self):
        c, Q, O = r.teach(0, 8, r.CHAIN, (0, 1, 2, 3))
        net = r.Net(c, r.learn(Q, O, "rows", "pairwise", range(4))).run(600)
        n = r.erase_cue(net, 3).run(300)
        own, last = r.roots(n, 590)
        self.assertEqual(own, [3])
        self.assertEqual([(last[u] - last[3]) % 59 for u in (2, 1, 0)], [8, 16, 24])

    def test_fork_needs_the_summed_receptor(self):
        c, Q, O = r.teach(0, 6, r.FORK, (0, 1, 2, 3, 4))
        pair = r.Net(c, r.learn(Q, O, "rows+beats", "pairwise", range(5)), held=range(5)).run(413)
        f = r.first_beats(pair, 0, range(5))
        self.assertTrue(f[2] is not None and f[4] is not None)        # both branches fire
        joint = r.Net(c, r.learn(Q, O, "qcubic+beats", "joint", range(5)), held=range(5)).run(413)
        a, b = r.first_beats(joint, 0, range(5)), r.first_beats(joint, 3, range(5))
        self.assertTrue(a[2] is not None and a[4] is None)
        self.assertTrue(b[4] is not None and b[2] is None)


if __name__ == "__main__":
    unittest.main()

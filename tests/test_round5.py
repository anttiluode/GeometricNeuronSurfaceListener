"""A receptor learned from a neighbour's rows must replay a taught chain at the taught spacing."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import round5 as r  # noqa: E402


class Round5Tests(unittest.TestCase):
    def test_chain_replays_both_ways_at_taught_spacing(self):
        base, ids, ons = r.teach("release_AB", 0, 8)
        self.assertEqual(r.taught_hops(ons), {0: [8, 8, 8], 3: [8, 8, 8]})
        p = r.Player(base, r.learn(ids, ons))
        for _ in range(240):
            p.tick()
        self.assertEqual(r.probe(p, 0), [8, 16, 24, 32])
        self.assertEqual(r.probe(p, 3), [32, 24, 16, 8])
        self.assertEqual(r.probe(p, None), [None] * 4)

    def test_one_row_is_not_enough(self):
        base, ids, ons = r.teach("release_AB", 0, 8)
        p = r.Player(base, r.learn(ids, ons, depths=(1,)))
        for _ in range(240):
            p.tick()
        self.assertEqual(r.probe(p, 0)[1:], [None] * 3)


if __name__ == "__main__":
    unittest.main()

"""Teaching by hold and release must build next-in-line edges, and a random order must not."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from round3 import teach  # noqa: E402

ADJ = [(i, j) for i in range(4) for j in range(4) if abs(i - j) == 1]
FAR = [(i, j) for i in range(4) for j in range(4) if abs(i - j) > 1]


class Round3Tests(unittest.TestCase):
    def test_release_teaching_builds_a_chain(self):
        _, w = teach("release_AB", 0)
        self.assertGreater(np.mean([w[i, j] for i, j in ADJ]),
                           2.5 * np.mean([w[i, j] for i, j in FAR]))

    def test_random_release_order_does_not(self):
        _, w = teach("release_random", 0)
        self.assertLess(np.mean([w[i, j] for i, j in ADJ]),
                        1.5 * np.mean([w[i, j] for i, j in FAR]))


if __name__ == "__main__":
    unittest.main()

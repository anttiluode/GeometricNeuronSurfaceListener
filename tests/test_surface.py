"""Structural controls: do not mistake a correlation table for a working neuron."""
import copy
import unittest
import numpy as np
from gn.core import Colony, G, QMIN
from surface import (SurfaceColony, overlap_matrix, normalized_centered,
                     aligned_two_unit_state)


class SurfaceTests(unittest.TestCase):
    def test_same_stored_table_and_original_single_loop(self):
        self.assertEqual(G.shape, (600, 16))
        one = Colony(1)
        values = []
        for t in range(2000):
            one.step()
            if t >= 1500 and one.own[0] > 3:
                values.append(t)
        onsets = [values[i] for i in range(len(values))
                  if i==0 or values[i] > values[i-1]+1]
        self.assertGreater(len(onsets), 4)
        self.assertTrue(all(b-a == 59 for a,b in zip(onsets,onsets[1:])))

    def test_centered_similarity_is_symmetric_and_contextual(self):
        rows=np.stack([G[43-QMIN],G[48-QMIN],G[78-QMIN]])
        K=overlap_matrix(rows, "surface")
        self.assertTrue(np.allclose(K,K.T,rtol=0,atol=1e-12))
        self.assertTrue(np.all(np.diag(K)==0))
        self.assertGreater(abs(K[0,1]-K[0,2]),0.15)
        self.assertTrue(np.isfinite(K).all())

    def test_raw_and_centered_are_not_the_same_claim(self):
        rows=np.stack([G[43-QMIN],G[78-QMIN]])
        raw=overlap_matrix(rows,"raw")[0,1]
        centered=overlap_matrix(rows,"surface")[0,1]
        self.assertGreater(raw,0.5)
        self.assertLess(abs(centered),0.2)

    def test_moving_receiver_different_from_frozen_receiver(self):
        rows=np.stack([G[43-QMIN],G[48-QMIN],G[78-QMIN]])
        moving=overlap_matrix(rows,"surface")
        frozen=overlap_matrix(rows,"fixed")
        self.assertGreater(np.max(np.abs(moving-frozen)),0.2)

    def test_exact_parent_fixed_taps_parity(self):
        n=4
        W=np.array([[0,.02,.04,.15],[.1,0,.02,.05],
                    [.11,.08,0,.03],[.01,.05,.07,0]],float)
        init=Colony(n,rng=np.random.default_rng(4))
        old=copy.deepcopy(init)
        old.w=W.copy()
        new=SurfaceColony(n,W=W,mode="fixed_taps",base=init)
        for _ in range(180):
            x=old.step()
            y=new.step()
            np.testing.assert_array_equal(x,y)
            np.testing.assert_allclose(old.R,new.core.R,rtol=0,atol=1e-12)
            np.testing.assert_array_equal(old.pipe,new.core.pipe)
            np.testing.assert_allclose(old.var,new.core.var,rtol=0,atol=1e-12)

    def test_no_coupling_cannot_transmit_forced_event(self):
        base=Colony(2,rng=np.random.default_rng(3))
        for _ in range(500):
            base.step()
        W=np.zeros((2,2))
        a=SurfaceColony(2,W=W,mode="surface",base=base)
        b=SurfaceColony(2,W=W,mode="surface",base=base)
        for k in range(90):
            f=np.array([np.nan,-0.28]) if k <2 else None
            xa=a.step(force=f)
            xb=b.step()
            self.assertEqual(xa[0],xb[0])
            self.assertEqual(a.core.R[0],b.core.R[0])

    def test_join_phase_histories_preserves_order(self):
        a,b=Colony(1),Colony(1)
        for _ in range(720):a.step()
        for _ in range(742):b.step()
        c=aligned_two_unit_state(a,b)
        self.assertEqual(c.count,a.count)
        for age in (1,5,17,50):
            for i,o in enumerate((a,b)):
                self.assertEqual(c.hist[i,(c.count-age)%c.L],
                                 o.hist[0,(o.count-age)%o.L])
        for k in range(35):
            oa=a.step();ob=b.step();oc=c.step()
            np.testing.assert_array_equal(oc,np.r_[oa,ob])


if __name__ == "__main__":
    unittest.main()

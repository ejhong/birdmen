"""Scientific checks; run with the optional NumPy/SciPy/Pillow environment."""
import unittest
try:
    import numpy as np
    from pipeline.bathymetry_resolution import block_average,analyse
except ImportError:
    np=None


@unittest.skipIf(np is None,'Optional scientific dependencies not installed in this interpreter')
class ResolutionTests(unittest.TestCase):
    def test_missing_values_are_not_zero_depths_and_partial_blocks_are_weighted(self):
        a=np.array([[-20.,-22.,-24.],[-20.,-1e38,-26.]])
        valid=a>-1e20
        mean,reconstructed,counts=block_average(a,valid,2)
        np.testing.assert_array_equal(counts,[[3,2]])
        np.testing.assert_allclose(mean,[[-62/3,-25]])
        self.assertEqual(reconstructed.shape,a.shape)
        self.assertTrue(np.isfinite(reconstructed).all())
    def test_native_resolution_is_identity_on_observed_cells(self):
        a=np.arange(35,dtype=float).reshape(5,7);mask=np.ones_like(a,dtype=bool);mask[0,0]=False
        _,result,_=block_average(a,mask,1)
        np.testing.assert_array_equal(result[mask],a[mask])
        self.assertTrue(np.isnan(result[0,0]))
    def test_averaging_cannot_add_variance_on_the_original_observed_support(self):
        rng=np.random.default_rng(19);a=rng.normal(size=(31,27));mask=rng.random(a.shape)>.25
        for factor in [2,3,10,20]:
            _,out,_=block_average(a,mask,factor)
            self.assertLessEqual(np.var(out[mask]),np.var(a[mask])+1e-12)
            # Between-block + within-block variance equals original variance.
            self.assertAlmostEqual(np.var(out[mask])+np.mean((out[mask]-a[mask])**2),np.var(a[mask]),places=10)

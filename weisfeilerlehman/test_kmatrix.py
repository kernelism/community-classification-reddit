import unittest
import pickle
import numpy as np

class TestCompleteKernelMatrix(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Load the complete kernel matrix once for all tests
        with open('v2/final_kernel_matrix/complete_kernel_matrix.pkl', 'rb') as f:
            cls.complete_kernel_matrix = pickle.load(f)
    
    def test_shape(self):
        self.assertEqual(self.complete_kernel_matrix.shape, (4032, 4032), "Matrix shape is not (4032, 4032)")
    
    def test_diagonal(self):
        self.assertTrue(np.all(self.complete_kernel_matrix.diagonal() == 1.0), "Diagonal elements are not all 1")
    
    def test_no_zeros(self):
        self.assertFalse(np.any(self.complete_kernel_matrix == 0), "Matrix contains zero elements")
    
    def test_symmetric(self):
        self.assertTrue(np.allclose(self.complete_kernel_matrix, self.complete_kernel_matrix.T, atol=1e-8), "Matrix is not symmetric")

if __name__ == '__main__':
    unittest.main()

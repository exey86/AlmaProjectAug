import unittest
import arbitraje


class ArbitrajeTests(unittest.TestCase):

    def test_tasa_implicita(self):
        tasa = arbitraje.tasa_implicita(100, 90, 30)
        self.assertAlmostEqual(tasa, 1.35185185, delta=1e-6)


if __name__ == '__main__':
    unittest.main()

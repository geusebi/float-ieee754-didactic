import unittest
from floatedu import Float32

precision = 6

class Test_Float32(unittest.TestCase):
    def test_numbers(self):
        numbers = (
            ("0 00000000 00000000000000000000001", 1.4E-45),
            ("0 10001001 00110100100111010011101", 1234.456665),
            ("0 01111111 00000000000000000000000", 1.0),
        )

        for binary, expected in numbers:
            f = Float32(binary)
            self.assertAlmostEqual(f.value, expected, precision)

    def test_specials(self):
        numbers = (
            ("0 00000000 00000000000000000000000", float("+0")),
            ("1 00000000 00000000000000000000000", float("-0")),
            ("0 11111111 00000000000000000000000", float("+inf")),
            ("1 11111111 00000000000000000000000", float("-inf")),
        )

        nan = Float32("0 11111111 10000000000000000000000")
        self.assertNotEqual(nan.value, nan.value)

        for binary, expected in numbers:
            f = Float32(binary)
            self.assertEqual(f.value, expected)

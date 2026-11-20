import unittest

import verify


class RequireStays(unittest.TestCase):
    def test_false_check_raises(self):
        with self.assertRaises(verify.CheckFailure):
            verify.require(False, "planted")


if __name__ == "__main__":
    unittest.main()

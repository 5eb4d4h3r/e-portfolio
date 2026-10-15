"""Unit tests for M4_U10_CaseStudyActivity_security.

These were the first tests written for the module, following the
red-green-refactor cycle set out in the unit's required reading
(Tibi, 2022): each test was written against a function that did not
yet exist, run to confirm it failed for the right reason, and only
then implemented.
"""

import unittest

from M4_U10_CaseStudyActivity_security import hash_password, verify_password


class HashPasswordTests(unittest.TestCase):
    def test_hash_is_not_the_plain_password(self):
        # Arrange
        password = "Sup3rSecret"
        # Act
        hashed = hash_password(password)
        # Assert
        self.assertNotEqual(hashed, password)

    def test_hashing_the_same_password_twice_gives_different_output(self):
        # Arrange
        password = "Sup3rSecret"
        # Act
        first = hash_password(password)
        second = hash_password(password)
        # Assert
        self.assertNotEqual(first, second)  # different random salts

    def test_hash_password_raises_for_input_longer_than_72_bytes(self):
        # This documents a real constraint of the bcrypt algorithm itself
        # (see security.MAX_PASSWORD_BYTES); UserService is responsible
        # for turning this into a policy-level WeakPasswordError before
        # a password ever reaches this function.
        # Arrange
        too_long = "x" * 100
        # Act / Assert
        with self.assertRaises(ValueError):
            hash_password(too_long)


class VerifyPasswordTests(unittest.TestCase):
    def test_correct_password_verifies_true(self):
        # Arrange
        password = "Sup3rSecret"
        stored = hash_password(password)
        # Act
        result = verify_password(password, stored)
        # Assert
        self.assertTrue(result)

    def test_incorrect_password_verifies_false(self):
        # Arrange
        stored = hash_password("Sup3rSecret")
        # Act
        result = verify_password("WrongPassword1", stored)
        # Assert
        self.assertFalse(result)

    def test_malformed_stored_hash_verifies_false_rather_than_raising(self):
        # Arrange
        malformed = "not-a-valid-hash"
        # Act
        result = verify_password("anything", malformed)
        # Assert
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

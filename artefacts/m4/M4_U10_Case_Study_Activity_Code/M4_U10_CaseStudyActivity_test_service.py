"""Unit tests for M4_U10_CaseStudyActivity_service.UserService.

Each public method is exercised with at least one valid case and the
failure cases its docstring commits to. UserService is tested against
InMemoryUserRepository as a test double rather than a real database,
so these remain fast, isolated unit tests (Tibi, 2022, Chapter 4).
"""

import unittest

from M4_U10_CaseStudyActivity_exceptions import (
    AuthenticationError,
    CommonPasswordError,
    DuplicateUserError,
    InvalidEmailError,
    InvalidUsernameError,
    PasswordSimilarToUsernameError,
    UserNotFoundError,
    WeakPasswordError,
)
from M4_U10_CaseStudyActivity_repository import InMemoryUserRepository
from M4_U10_CaseStudyActivity_service import UserService


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.service = UserService(InMemoryUserRepository())

    def test_valid_registration_returns_a_user_with_a_hashed_password(self):
        # Act
        user = self.service.register("alice", "alice@example.com", "Sup3rSecret")
        # Assert
        self.assertEqual(user.username, "alice")
        self.assertNotEqual(user.password_hash, "Sup3rSecret")

    def test_rejects_a_username_shorter_than_five_characters(self):
        with self.assertRaises(InvalidUsernameError):
            self.service.register("al", "alice@example.com", "Sup3rSecret")

    def test_rejects_a_username_starting_with_a_digit(self):
        with self.assertRaises(InvalidUsernameError):
            self.service.register("1alice", "alice@example.com", "Sup3rSecret")

    def test_rejects_a_malformed_email(self):
        with self.assertRaises(InvalidEmailError):
            self.service.register("alice", "not-an-email", "Sup3rSecret")

    def test_rejects_a_password_without_a_digit(self):
        with self.assertRaises(WeakPasswordError):
            self.service.register("alice", "alice@example.com", "NoDigitsHere")

    def test_rejects_a_password_shorter_than_eight_characters(self):
        with self.assertRaises(WeakPasswordError):
            self.service.register("alice", "alice@example.com", "Ab1")

    def test_rejects_a_duplicate_username(self):
        self.service.register("alice", "alice@example.com", "Sup3rSecret")
        with self.assertRaises(DuplicateUserError):
            self.service.register("alice", "someoneelse@example.com", "Sup3rSecret")

    def test_rejects_a_duplicate_email(self):
        self.service.register("alice", "alice@example.com", "Sup3rSecret")
        with self.assertRaises(DuplicateUserError):
            self.service.register("alice2", "alice@example.com", "Sup3rSecret")

    def test_rejects_a_password_equal_to_the_username(self):
        with self.assertRaises(PasswordSimilarToUsernameError):
            self.service.register("alice2024", "alice@example.com", "alice2024")

    def test_rejects_a_password_containing_the_username(self):
        with self.assertRaises(PasswordSimilarToUsernameError):
            self.service.register("alice99", "alice@example.com", "alice99xyz1")

    def test_rejects_a_password_longer_than_bcrypts_byte_limit(self):
        over_limit_password = "Aa1" + "x" * 80  # 83 bytes, all ASCII
        with self.assertRaises(WeakPasswordError):
            self.service.register("bobby", "bobby@example.com", over_limit_password)

    def test_rejects_a_common_password(self):
        with self.assertRaises(CommonPasswordError):
            self.service.register("bobby", "bobby@example.com", "password1")

    def test_rejects_a_common_password_with_digits_appended(self):
        # Baker (2022) notes that appending digits to a dictionary word
        # does not defeat a dictionary attack; the check should not
        # either.
        with self.assertRaises(CommonPasswordError):
            self.service.register("bobby", "bobby@example.com", "dragon12345")


class AuthenticateTests(unittest.TestCase):
    def setUp(self):
        self.service = UserService(InMemoryUserRepository())
        self.service.register("alice", "alice@example.com", "Sup3rSecret")

    def test_correct_credentials_authenticate_true(self):
        self.assertTrue(self.service.authenticate("alice", "Sup3rSecret"))

    def test_incorrect_password_authenticates_false(self):
        self.assertFalse(self.service.authenticate("alice", "WrongPassword1"))

    def test_unknown_username_raises_user_not_found(self):
        with self.assertRaises(UserNotFoundError):
            self.service.authenticate("bob", "whatever1")

    def test_successful_authentication_is_logged(self):
        with self.assertLogs("user_management.audit", level="INFO") as captured:
            self.service.authenticate("alice", "Sup3rSecret")
        self.assertTrue(any("AUTH_SUCCESS" in line and "alice" in line for line in captured.output))

    def test_wrong_password_is_logged_with_reason(self):
        with self.assertLogs("user_management.audit", level="INFO") as captured:
            self.service.authenticate("alice", "WrongPassword1")
        self.assertTrue(any("incorrect password" in line for line in captured.output))

    def test_unknown_username_authentication_is_logged_with_reason(self):
        with self.assertLogs("user_management.audit", level="INFO") as captured:
            with self.assertRaises(UserNotFoundError):
                self.service.authenticate("bob", "whatever1")
        self.assertTrue(any("unknown username" in line for line in captured.output))


class ChangePasswordTests(unittest.TestCase):
    def setUp(self):
        self.service = UserService(InMemoryUserRepository())
        self.service.register("alice", "alice@example.com", "Sup3rSecret")

    def test_changing_with_the_correct_current_password_succeeds(self):
        self.service.change_password("alice", "Sup3rSecret", "NewPassw0rd")
        self.assertTrue(self.service.authenticate("alice", "NewPassw0rd"))

    def test_changing_with_the_wrong_current_password_raises(self):
        with self.assertRaises(AuthenticationError):
            self.service.change_password("alice", "WrongPassword1", "NewPassw0rd")

    def test_wrong_current_password_change_is_logged(self):
        with self.assertLogs("user_management.audit", level="INFO") as captured:
            with self.assertRaises(AuthenticationError):
                self.service.change_password("alice", "WrongPassword1", "NewPassw0rd")
        self.assertTrue(any("incorrect current password" in line for line in captured.output))

    def test_changing_to_a_weak_new_password_raises(self):
        with self.assertRaises(WeakPasswordError):
            self.service.change_password("alice", "Sup3rSecret", "weak")

    def test_unknown_username_raises_user_not_found(self):
        with self.assertRaises(UserNotFoundError):
            self.service.change_password("bob", "whatever1", "NewPassw0rd")

    def test_changing_to_a_password_similar_to_the_username_raises(self):
        with self.assertRaises(PasswordSimilarToUsernameError):
            self.service.change_password("alice", "Sup3rSecret", "alice2024")

    def test_changing_to_a_common_password_raises(self):
        with self.assertRaises(CommonPasswordError):
            self.service.change_password("alice", "Sup3rSecret", "qwerty123")


class HasRoleTests(unittest.TestCase):
    def setUp(self):
        self.service = UserService(InMemoryUserRepository())
        self.service.register("alice", "alice@example.com", "Sup3rSecret", role="learner")

    def test_user_has_their_assigned_role(self):
        self.assertTrue(self.service.has_role("alice", "learner"))

    def test_user_does_not_have_a_different_role(self):
        self.assertFalse(self.service.has_role("alice", "instructor"))

    def test_unknown_username_raises_user_not_found(self):
        with self.assertRaises(UserNotFoundError):
            self.service.has_role("bob", "learner")


if __name__ == "__main__":
    unittest.main()

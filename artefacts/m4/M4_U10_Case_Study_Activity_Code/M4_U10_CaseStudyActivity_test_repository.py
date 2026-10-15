"""Unit tests for M4_U10_CaseStudyActivity_repository.InMemoryUserRepository."""

import unittest

from M4_U10_CaseStudyActivity_models import User
from M4_U10_CaseStudyActivity_repository import InMemoryUserRepository


class InMemoryUserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryUserRepository()

    def test_get_by_username_returns_none_when_empty(self):
        # Act
        result = self.repository.get_by_username("alice")
        # Assert
        self.assertIsNone(result)

    def test_add_then_get_by_username_returns_the_same_user(self):
        # Arrange
        user = User(username="alice", email="alice@example.com", password_hash="x")
        # Act
        self.repository.add(user)
        result = self.repository.get_by_username("alice")
        # Assert
        self.assertIs(result, user)

    def test_get_by_email_finds_a_user_added_under_a_different_key(self):
        # Arrange
        user = User(username="alice", email="alice@example.com", password_hash="x")
        self.repository.add(user)
        # Act
        result = self.repository.get_by_email("alice@example.com")
        # Assert
        self.assertIs(result, user)

    def test_get_by_email_returns_none_when_no_match(self):
        # Act
        result = self.repository.get_by_email("nobody@example.com")
        # Assert
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

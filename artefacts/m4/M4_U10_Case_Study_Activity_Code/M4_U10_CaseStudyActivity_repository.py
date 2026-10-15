"""Persistence abstraction for User records.

UserService depends on this abstraction rather than a concrete store,
so its tests can run against a fast in-memory double instead of a real
database (Tibi, 2022, on test doubles). InMemoryUserRepository also
serves as the module's actual storage for this exercise; a production
deployment would replace it with a database-backed implementation
without changing UserService.
"""

from abc import ABC, abstractmethod
from typing import Optional

from M4_U10_CaseStudyActivity_models import User


class UserRepository(ABC):
    """The storage contract UserService relies on."""

    @abstractmethod
    def add(self, user: User) -> None:
        """Persist a new user. Uniqueness is the caller's responsibility."""

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Return the user with ``username``, or None if none exists."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Return the user with ``email``, or None if none exists."""


class InMemoryUserRepository(UserRepository):
    """A dictionary-backed UserRepository, indexed by both username and
    email, so each lookup is an O(1) dictionary access rather than a
    scan over every registered user."""

    def __init__(self) -> None:
        self._users_by_username: dict[str, User] = {}
        self._users_by_email: dict[str, User] = {}

    def add(self, user: User) -> None:
        self._users_by_username[user.username] = user
        self._users_by_email[user.email] = user

    def get_by_username(self, username: str) -> Optional[User]:
        return self._users_by_username.get(username)

    def get_by_email(self, email: str) -> Optional[User]:
        return self._users_by_email.get(email)

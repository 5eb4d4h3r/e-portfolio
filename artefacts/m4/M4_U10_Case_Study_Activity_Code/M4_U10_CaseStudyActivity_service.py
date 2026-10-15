"""Business logic for registering, authenticating and managing users.

UserService depends on a UserRepository supplied by the caller
(constructor injection) rather than constructing one itself, so a test
can supply an in-memory repository and inspect its state directly,
without touching a real database.
"""

import re

from M4_U10_CaseStudyActivity_audit_log import (
    log_authentication_failure,
    log_authentication_success,
    log_password_change_failure,
    log_password_change_success,
)
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
from M4_U10_CaseStudyActivity_models import User
from M4_U10_CaseStudyActivity_repository import UserRepository
from M4_U10_CaseStudyActivity_security import MAX_PASSWORD_BYTES, hash_password, verify_password

_USERNAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,19}$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_VALID_ROLES = {"learner", "instructor", "admin"}
_MIN_PASSWORD_LENGTH = 8

# A small, illustrative sample of very common or previously breached
# passwords (Baker, 2022, notes that lists of this kind, drawn from
# real breaches, number in the billions; a production system would use
# such a corpus rather than this short list).
_COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "letmein",
    "welcome", "iloveyou", "admin", "monkey", "dragon",
    "sunshine", "princess", "football", "trustno1", "abc12345",
}
_TRAILING_DIGITS = re.compile(r"\d+$")


def _fails_strength_rule(password: str) -> bool:
    return (
        len(password) < _MIN_PASSWORD_LENGTH
        or not any(character.isdigit() for character in password)
        or not any(character.isalpha() for character in password)
    )


def _is_similar_to_username(password: str, username: str) -> bool:
    return password.lower() == username.lower() or username.lower() in password.lower()


def _is_a_common_password(password: str) -> bool:
    # Baker (2022) notes that appending digits to a dictionary word does
    # not defeat a dictionary attack, so a common word is still rejected
    # once any trailing digits are stripped, not only on an exact match.
    candidate = password.lower()
    if candidate in _COMMON_PASSWORDS:
        return True
    stripped = _TRAILING_DIGITS.sub("", candidate)
    return stripped != candidate and stripped in _COMMON_PASSWORDS


def _validate_new_password(password: str, username: str) -> None:
    """Apply every password-policy rule, raising the first one violated.

    Consolidates checks that were previously duplicated between
    register and change_password into a single place, so a new rule
    only needs to be added once.
    """
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise WeakPasswordError(
            f"Password must be no more than {MAX_PASSWORD_BYTES} bytes, "
            "a limit of the bcrypt hashing algorithm used to store it."
        )
    if _fails_strength_rule(password):
        raise WeakPasswordError(
            "Password must be at least 8 characters and include at "
            "least one letter and one digit."
        )
    if _is_similar_to_username(password, username):
        raise PasswordSimilarToUsernameError(
            "Password must not be the same as, or contain, the username."
        )
    if _is_a_common_password(password):
        raise CommonPasswordError(
            "Password is too common or appears in known breached-password lists."
        )


class UserService:
    """Registration, authentication and authorisation for platform users."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def register(self, username: str, email: str, password: str, role: str = "learner") -> User:
        """Create and persist a new user.

        Raises InvalidUsernameError, InvalidEmailError, WeakPasswordError,
        PasswordSimilarToUsernameError, CommonPasswordError, ValueError
        (unknown role) or DuplicateUserError if the corresponding rule
        is violated.
        """
        if not _USERNAME_PATTERN.match(username):
            raise InvalidUsernameError(
                "Username must start with a letter and be 5 to 20 characters "
                "of letters, digits or underscores."
            )
        if not _EMAIL_PATTERN.match(email):
            raise InvalidEmailError("Email address is not in a recognised format.")
        _validate_new_password(password, username)
        if role not in _VALID_ROLES:
            raise ValueError(f"Unknown role: {role!r}")
        if self._repository.get_by_username(username) is not None:
            raise DuplicateUserError(f"Username {username!r} is already registered.")
        if self._repository.get_by_email(email) is not None:
            raise DuplicateUserError(f"Email {email!r} is already registered.")

        user = User(username=username, email=email, password_hash=hash_password(password), role=role)
        self._repository.add(user)
        return user

    def authenticate(self, username: str, password: str) -> bool:
        """Return True if ``password`` matches the stored credential for ``username``.

        Raises UserNotFoundError if no such user is registered. A caller
        presenting results to an end user would typically still show a
        single generic failure message for both cases, to avoid
        confirming which usernames exist; the specific reason is still
        recorded in the audit log for monitoring purposes.
        """
        user = self._repository.get_by_username(username)
        if user is None:
            log_authentication_failure(username, "unknown username")
            raise UserNotFoundError(f"No user registered with username {username!r}.")
        if verify_password(password, user.password_hash):
            log_authentication_success(username)
            return True
        log_authentication_failure(username, "incorrect password")
        return False

    def change_password(self, username: str, current_password: str, new_password: str) -> None:
        """Replace a user's password after verifying the current one.

        Raises UserNotFoundError, AuthenticationError (current password
        incorrect), WeakPasswordError, PasswordSimilarToUsernameError or
        CommonPasswordError (new password fails policy).
        """
        user = self._repository.get_by_username(username)
        if user is None:
            raise UserNotFoundError(f"No user registered with username {username!r}.")
        if not verify_password(current_password, user.password_hash):
            log_password_change_failure(username, "incorrect current password")
            raise AuthenticationError("Current password is incorrect.")
        _validate_new_password(new_password, username)
        user.password_hash = hash_password(new_password)
        log_password_change_success(username)

    def has_role(self, username: str, role: str) -> bool:
        """Return True if the registered user holds ``role``.

        Raises UserNotFoundError if no such user is registered.
        """
        user = self._repository.get_by_username(username)
        if user is None:
            raise UserNotFoundError(f"No user registered with username {username!r}.")
        return user.role == role

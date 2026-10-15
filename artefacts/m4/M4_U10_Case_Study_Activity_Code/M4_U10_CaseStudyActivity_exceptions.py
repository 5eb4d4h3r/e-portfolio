"""Custom exceptions for the User Management module.

Each exception represents a distinct, recoverable validation or
authentication failure so that calling code can react to a specific
case rather than catching a single generic exception type.
"""


class UserManagementError(Exception):
    """Base class for all User Management module exceptions."""


class InvalidUsernameError(UserManagementError):
    """Raised when a username does not satisfy the module's format rules."""


class InvalidEmailError(UserManagementError):
    """Raised when an email address does not satisfy basic format rules."""


class WeakPasswordError(UserManagementError):
    """Raised when a password does not meet the minimum strength policy."""


class PasswordSimilarToUsernameError(WeakPasswordError):
    """Raised when a password matches, or contains, the account's username.

    A subclass of WeakPasswordError: code that only needs to know "the
    password was rejected as weak" can catch WeakPasswordError, while
    code that needs the specific reason can catch this type instead.
    """


class CommonPasswordError(WeakPasswordError):
    """Raised when a password appears on a list of very common or
    previously breached passwords, including a common word with digits
    appended. Also a subclass of WeakPasswordError, for the same reason
    as PasswordSimilarToUsernameError."""


class DuplicateUserError(UserManagementError):
    """Raised when registration is attempted with a username or email
    that is already in use."""


class UserNotFoundError(UserManagementError):
    """Raised when an operation references a username that does not exist."""


class AuthenticationError(UserManagementError):
    """Raised when credential verification fails, for example an
    incorrect current password during a password change."""

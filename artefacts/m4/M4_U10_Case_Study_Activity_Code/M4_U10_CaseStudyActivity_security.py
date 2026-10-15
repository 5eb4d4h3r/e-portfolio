"""Password hashing utilities.

Uses bcrypt (Provos and Mazieres, 1999). bcrypt.gensalt() generates a
fresh random salt on every call and bcrypt stores it as part of its own
output, so two users who choose the same password never produce the
same stored hash, and there is no separate salt to generate, store or
retrieve by hand, unlike the module's first, hand-rolled PBKDF2 version.
"""

import bcrypt

MAX_PASSWORD_BYTES = 72
"""bcrypt truncates or rejects input beyond 72 bytes; this is a
constraint of the algorithm itself, not a policy choice, and is
enforced as policy by UserService before hash_password is called."""


def hash_password(password: str) -> str:
    """Return a bcrypt hash of ``password`` as a UTF-8 string.

    Precondition: ``len(password.encode("utf-8")) <= MAX_PASSWORD_BYTES``.
    The caller is expected to have already validated password strength
    and length; this function is concerned only with secure storage,
    not policy.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    """Return True if ``password`` matches a hash produced by hash_password.

    Returns False, rather than raising, for a malformed ``stored_hash``
    so a corrupt record fails closed instead of crashing the caller.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except ValueError:
        return False

"""Domain model for the User Management module."""

from dataclasses import dataclass


@dataclass
class User:
    """A registered platform user.

    ``password_hash`` holds a salted hash produced by
    ``M4_U10_CaseStudyActivity_security.hash_password``, never a plain-text
    password.
    """

    username: str
    email: str
    password_hash: str
    role: str = "learner"

    def to_public_dict(self) -> dict:
        """Return this user's data with credentials removed.

        Intended for use wherever a user record is exposed outside the
        module, for example a future API response, so that the password
        hash is never serialised by mistake.
        """
        return {"username": self.username, "email": self.email, "role": self.role}

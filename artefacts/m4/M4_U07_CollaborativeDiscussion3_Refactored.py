import bcrypt
import time

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 60


class User:
    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password


class AuthenticationSystem:
    def __init__(self):
        self.users = {}            # username -> hashed password
        self.failed_attempts = {}  # username -> count of consecutive failures
        self.lockout_until = {}    # username -> timestamp lockout expires

    def add_user(self, username, password):
        # Type gate: reject non-string usernames (None, int, etc.) by
        # collapsing them to "", so the check below catches them uniformly.
        username = username.strip() if isinstance(username, str) else ""
        # Empty string and non-string password both fail this one condition.
        if not username or not isinstance(password, str):
            raise ValueError("Invalid username or password")
        # Duplicate check: without this, a second call with the same username
        # silently overwrites the existing hash (account-takeover).
        if username in self.users:
            raise ValueError("Username already exists")
        if len(password) < 9:
            raise ValueError("Password too weak")

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.users[username] = hashed

    def authenticate(self, username, password):
        # password.encode() further down requires password to be a string, and an
        # empty username can never match a stored account, so both are rejected
        # here before doing any lookup or hashing work.
        username = username.strip() if isinstance(username, str) else ""
        if not username or not isinstance(password, str):
            return False

        now = time.time()
        if now < self.lockout_until.get(username, 0):
            return False  # account temporarily locked

        hashed = self.users.get(username)
        if hashed is None:
            return False  # unknown username fails safely, no detail leaked

        if bcrypt.checkpw(password.encode(), hashed):
            self.failed_attempts[username] = 0
            return True

        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
        if self.failed_attempts[username] >= MAX_ATTEMPTS:
            self.lockout_until[username] = now + LOCKOUT_SECONDS
        return False
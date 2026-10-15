import time

# Only one of these three import lines should be active at a time.
# Same test file throughout, only the production code underneath changes.
# Test command: pytest M4_U10_Seminar_Prep_Demo.py -v

# Step 1, red: original file, no is_locked method yet. Running pytest now
# fails with AttributeError.
# from M4_U07_CollaborativeDiscussion3_Refactored import AuthenticationSystem, MAX_ATTEMPTS

# Step 2, green: is_locked has been added, but authenticate() still has its
# own separate, duplicated copy of the same check. Both tests pass here.
# from M4_U10_Seminar_Prep_GreenCode import AuthenticationSystem, MAX_ATTEMPTS

# Step 3, refactor: authenticate() now calls is_locked() instead of
# repeating the check, removing the duplication. Both tests still pass.
from M4_U10_Seminar_Prep_NewCode import AuthenticationSystem, MAX_ATTEMPTS


def test_is_locked_true_after_max_failed_attempts(monkeypatch):
    # Arrange: freeze the clock so the test does not depend on real time
    monkeypatch.setattr(time, "time", lambda: 1_000_000.0)
    auth = AuthenticationSystem()
    auth.add_user("carol", "AnotherPass123")

    # Act
    for _ in range(MAX_ATTEMPTS):
        auth.authenticate("carol", "wrongpassword")

    # Assert
    assert auth.is_locked("carol") is True


def test_is_locked_false_once_lockout_window_has_passed(monkeypatch):
    # Arrange: a mutable clock lets the Act step move time forward
    # without a real 60 second sleep in the test run
    clock = {"now": 1_000_000.0}
    monkeypatch.setattr(time, "time", lambda: clock["now"])
    auth = AuthenticationSystem()
    auth.add_user("carol", "AnotherPass123")
    for _ in range(MAX_ATTEMPTS):
        auth.authenticate("carol", "wrongpassword")

    # Act
    clock["now"] += 61

    # Assert
    assert auth.is_locked("carol") is False
    assert auth.authenticate("carol", "AnotherPass123") is True
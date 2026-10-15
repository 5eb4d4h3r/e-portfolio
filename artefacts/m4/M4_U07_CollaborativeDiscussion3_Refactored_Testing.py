from M4_U07_CollaborativeDiscussion3_Refactored import AuthenticationSystem

auth = AuthenticationSystem()
auth.add_user("admin", "@SecurePass123")

assert auth.authenticate("admin", "@SecurePass123") is True, "correct password should succeed"
assert auth.authenticate("admin", "wrongpassword") is False, "wrong password should fail"
assert auth.authenticate("ghost", "anything") is False, "unknown username should fail"

try:
    auth.add_user("bob", "1234")
    assert False, "weak password should have been rejected"
except ValueError:
    pass

try:
    auth.add_user("", "SecurePass123")
    assert False, "empty username should have been rejected"
except ValueError:
    pass

try:
    auth.add_user("admin", "AttackerPass456")
    assert False, "duplicate username should have been rejected"
except ValueError:
    pass

assert auth.authenticate("admin", "@SecurePass123") is True, "original password should still work after blocked duplicate"
assert auth.authenticate("admin", "AttackerPass456") is False, "attacker password should never have been stored"

try:
    auth.add_user("eve", "A" * 100)
    assert False, "overlong password should have been rejected"
except ValueError:
    pass

auth.add_user("carol", "AnotherPass123")
for _ in range(5):
    auth.authenticate("carol", "wrongpassword")
assert auth.authenticate("carol", "AnotherPass123") is False, "account should be locked out after 5 failures"

print("All tests passed")
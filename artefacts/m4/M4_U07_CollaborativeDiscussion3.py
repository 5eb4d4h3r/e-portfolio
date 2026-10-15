class User:
    def __init__(self, username, password):
         self.username = username
         self.password = password


class AuthenticationSystem:
    def __init__(self):
        self.users = []

    def add_user(self, username, password):
        self.users.append(User(username, password))

    def authenticate(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                return True
        return False


# Usage
auth_system = AuthenticationSystem()
auth_system.add_user("admin", "admin123") # Weak password
auth_system.add_user("user1", "password") # Weak password

# Simulate an injection attack
malicious_input = "admin' OR '1'='1"

print(auth_system.authenticate(malicious_input, "anything"))
# Output: True (Vulnerable to SQL injection)
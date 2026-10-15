# Refactored case study code: interface, two channels, UserManager,
# and a composition root

from abc import ABC, abstractmethod


class NotificationService(ABC):
    # Contract every channel must follow. UserManager will depend on
    # this instead of on a concrete class (Taelman et al., 2023).
    @abstractmethod
    def send_notification(self, user, message):
        pass


class EmailService(NotificationService):
    # First channel (Email).
    def send_notification(self, user, message):
        print(f"Sending email to {user}: {message}")


class SMSService(NotificationService):
    # Second channel (SMS), added to show that UserManager needs no change
    # to support it (SOLID open/closed in practice).
    def send_notification(self, user, message):
        print(f"Sending SMS to {user}: {message}")


class UserManager:
    def __init__(self, notifier):
        # Dependency is passed in, not created here, which removes the
        # "Control Freak" anti-pattern of the original code (Laigner et al., 2022).
        self.notifier = notifier

    def register_user(self, user):
        self.notifier.send_notification(user, "Welcome!")


def build_user_manager(channel="email"):
    # Composition root: the one place allowed to know about concrete
    # classes and wire them together. A DI container library such as
    # dependency-injector would automate this in a larger project
    # (Tuğan, Arslan and Tiryaki, 2024); a plain function is used here
    # so the example needs no extra install. This must not be called
    # from inside UserManager itself - that would be the Service
    # Locator anti-pattern (Laigner et al., 2022).
    if channel == "email":
        notifier = EmailService()
    elif channel == "sms":
        notifier = SMSService()
    else:
        raise ValueError(f"Unknown notification channel: {channel}")
    return UserManager(notifier)


if __name__ == "__main__":
    # Same UserManager code, two different channels swapped in.
    build_user_manager("email").register_user("alice@example.com")
    build_user_manager("sms").register_user("+441234567890")
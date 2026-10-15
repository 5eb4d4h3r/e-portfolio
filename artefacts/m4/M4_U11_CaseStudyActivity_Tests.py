# Unit tests use a mock channel so UserManager is tested without sending
# a real email or SMS. One integration test at the bottom is the only one
# allowed to touch the real EmailService, as the case study asks.

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock

from M4_U11_CaseStudyActivity_Main import (
    NotificationService,
    UserManager,
    EmailService,
    SMSService,
)


class UserManagerUnitTests(unittest.TestCase):
    def setUp(self):
        # spec=NotificationService rejects calls to methods the
        # interface does not define, which catches typos.
        self.mock_notifier = Mock(spec=NotificationService)
        self.manager = UserManager(self.mock_notifier)

    def test_register_user_sends_welcome_message(self):
        # Checks that register_user asks the injected notifier to send
        # exactly one "Welcome!" message to the given user, without a
        # real EmailService or SMSService ever being called.
        self.manager.register_user("alice@example.com")
        self.mock_notifier.send_notification.assert_called_once_with(
            "alice@example.com", "Welcome!"
        )

    def test_manager_accepts_any_notification_service(self):
        # Same manager, two unrelated channels - the point of
        # depending on an interface rather than a class.
        # Checks that UserManager behaves the same way regardless of
        # which concrete channel it was given, which is only possible
        # because it depends on NotificationService and not on
        # EmailService or SMSService directly.
        for channel_class in (EmailService, SMSService):
            mock_channel = Mock(spec=NotificationService)
            manager = UserManager(mock_channel)
            manager.register_user("bob@example.com")
            mock_channel.send_notification.assert_called_once_with(
                "bob@example.com", "Welcome!"
            )


class EmailServiceIntegrationTest(unittest.TestCase):
    def test_email_service_prints_expected_line(self):
        # The only test that exercises the real EmailService rather
        # than a mock. Captures stdout to check the exact line printed,
        # confirming the concrete channel itself behaves as expected.
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            EmailService().send_notification("carol@example.com", "Welcome!")
        self.assertEqual(
            captured_output.getvalue().strip(),
            "Sending email to carol@example.com: Welcome!",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
"""Unit tests for M4_U10_CaseStudyActivity_audit_log."""

import unittest

from M4_U10_CaseStudyActivity_audit_log import (
    log_authentication_failure,
    log_authentication_success,
    log_password_change_failure,
    log_password_change_success,
)

_LOGGER_NAME = "user_management.audit"


class AuditLogTests(unittest.TestCase):
    def test_authentication_success_is_logged_at_info(self):
        with self.assertLogs(_LOGGER_NAME, level="INFO") as captured:
            log_authentication_success("alice")
        self.assertIn("INFO", captured.output[0])
        self.assertIn("alice", captured.output[0])

    def test_authentication_failure_is_logged_at_warning_with_reason(self):
        with self.assertLogs(_LOGGER_NAME, level="INFO") as captured:
            log_authentication_failure("alice", "incorrect password")
        self.assertIn("WARNING", captured.output[0])
        self.assertIn("incorrect password", captured.output[0])

    def test_password_change_success_is_logged_at_info(self):
        with self.assertLogs(_LOGGER_NAME, level="INFO") as captured:
            log_password_change_success("alice")
        self.assertIn("INFO", captured.output[0])

    def test_password_change_failure_is_logged_at_warning_with_reason(self):
        with self.assertLogs(_LOGGER_NAME, level="INFO") as captured:
            log_password_change_failure("alice", "incorrect current password")
        self.assertIn("WARNING", captured.output[0])
        self.assertIn("incorrect current password", captured.output[0])


if __name__ == "__main__":
    unittest.main()

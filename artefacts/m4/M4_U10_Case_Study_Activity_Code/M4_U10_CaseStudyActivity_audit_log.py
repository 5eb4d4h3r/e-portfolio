"""Security audit logging for the User Management module.

Authentication and password-change outcomes are logged so they can be
reviewed for monitoring purposes, for example to spot repeated failed
logins against one account. Only what an investigation needs is
logged: the username and a short reason. Passwords, hashed or plain,
are never logged (Shah, 2023, on keeping sensitive data out of error
handling and logging).

This module only creates the logger and attaches a NullHandler, rather
than a FileHandler or StreamHandler, so that using this module does not
silently start writing files. The hosting application decides where
audit records go; see M4_U10_CaseStudyActivity_demo_audit_log.py for an
example that attaches a FileHandler.
"""

import logging

audit_logger = logging.getLogger("user_management.audit")
audit_logger.addHandler(logging.NullHandler())


def log_authentication_success(username: str) -> None:
    audit_logger.info("AUTH_SUCCESS username=%s", username)


def log_authentication_failure(username: str, reason: str) -> None:
    audit_logger.warning("AUTH_FAILURE username=%s reason=%s", username, reason)


def log_password_change_success(username: str) -> None:
    audit_logger.info("PASSWORD_CHANGE_SUCCESS username=%s", username)


def log_password_change_failure(username: str, reason: str) -> None:
    audit_logger.warning("PASSWORD_CHANGE_FAILURE username=%s reason=%s", username, reason)

"""Produce a sample security audit log for demonstration purposes.

The M4_U10_CaseStudyActivity_audit_log module only attaches a NullHandler, so
that importing it does not, on its own, start writing files. This
script shows the wiring a hosting application would add: a
FileHandler on the same logger, pointed at a log file suitable for a
monitoring tool to read.

Run with: python M4_U10_CaseStudyActivity_demo_audit_log.py
"""

import logging

from M4_U10_CaseStudyActivity_audit_log import audit_logger
from M4_U10_CaseStudyActivity_repository import InMemoryUserRepository
from M4_U10_CaseStudyActivity_service import UserService

LOG_FILE = "user_management_audit.log"

handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
audit_logger.addHandler(handler)
audit_logger.setLevel(logging.INFO)

service = UserService(InMemoryUserRepository())
service.register("alice", "alice@example.com", "Sup3rSecret")

service.authenticate("alice", "Sup3rSecret")            # successful login
service.authenticate("alice", "WrongPassword1")          # wrong password
try:
    service.authenticate("nobody", "whatever1")           # unknown username
except Exception:
    pass
try:
    service.change_password("alice", "WrongPassword1", "NewPassw0rd")  # wrong current password
except Exception:
    pass
service.change_password("alice", "Sup3rSecret", "NewPassw0rd1")  # successful change

print(f"Sample audit log written to {LOG_FILE}")

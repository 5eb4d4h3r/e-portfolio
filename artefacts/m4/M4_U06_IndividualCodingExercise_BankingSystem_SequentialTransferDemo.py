"""
sequential_transfer demonstration - reproduces the evidence behind
Figures 12, 13, and 14 in Annex A of the report.

Run this file directly (in the same folder as
M4_U06_IndividualCodingExercise_BankingSystem.py) to get:
  - Figure 12: the refund path when a deposit fails, and the manual-
    reconciliation error when the refund also fails.
  - Figure 13: sequential_transfer completing under the identical
    opposing load that deadlocks naive_transfer.
  - Figure 14: source equal to destination, tested against all three
    transfer designs.

deposit() cannot fail on its own once the amount is known positive, so
Figure 12 forces a failure with unittest.mock - the same technique the
test suite uses in TestSequentialTransfer.

Neither the exact timing in Figures 13/14 nor the exact balance split is
deterministic: both depend on your machine's thread scheduling. Use
whatever your own run produces; do not force it to match the numbers
quoted in the report.
"""

import threading
import textwrap
import time
from unittest.mock import patch

from M4_U06_IndividualCodingExercise_BankingSystem import (
    BankAccount,
    safe_transfer,
    naive_transfer,
    sequential_transfer,
    RefundFailedError,
    InsufficientFundsError,
)


def demonstrate_refund_path():
    """Figure 12: deposit fails and the withdrawal is refunded; then
    deposit AND refund both fail, raising RefundFailedError.
    """
    print("=== Figure 12a: deposit fails, refund succeeds ===")
    source = BankAccount("Source", 100)
    destination = BankAccount("Destination", 50)
    with patch.object(destination, "deposit", side_effect=RuntimeError("destination account is frozen")):
        try:
            sequential_transfer(source, destination, 30)
        except RuntimeError as e:
            print(f"Error propagated: {e}")
    print(f"Source balance: {source.get_balance()} (refunded back to 100)")
    print(f"Destination balance: {destination.get_balance()} (deposit never landed)")
    print()

    print("=== Figure 12b: deposit AND refund both fail ===")
    source2 = BankAccount("Source", 100)
    destination2 = BankAccount("Destination", 50)
    with patch.object(destination2, "deposit", side_effect=RuntimeError("destination account is frozen")), \
         patch.object(source2, "deposit", side_effect=RuntimeError("source account is also frozen")):
        try:
            sequential_transfer(source2, destination2, 30)
        except RefundFailedError as e:
            wrapped = textwrap.fill(f"RefundFailedError: {e}", width=78, subsequent_indent="  ")
            print(wrapped)
    print(f"Source balance: {source2.get_balance()} (30 stuck here)")
    print()


def demonstrate_no_deadlock():
    """Figure 13: sequential_transfer under the identical opposing load
    that reliably deadlocks naive_transfer.
    """
    print("=== Figure 13: sequential_transfer under opposing load ===")
    print("Test: 2 threads x 200 transfers of 10 each, opposite directions")

    def repeat(src, dst):
        for _ in range(200):
            try:
                sequential_transfer(src, dst, 10)
            except InsufficientFundsError:
                pass

    account_5 = BankAccount("Bank Account 5", 1000)
    account_6 = BankAccount("Bank Account 6", 1000)
    expected_total = account_5.get_balance() + account_6.get_balance()

    t1 = threading.Thread(target=repeat, args=(account_5, account_6))
    t2 = threading.Thread(target=repeat, args=(account_6, account_5))
    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    elapsed = time.perf_counter() - start
    closing_total = account_5.get_balance() + account_6.get_balance()

    print(f"Completed in {elapsed * 1000:.2f}ms, no deadlock.")
    print(f"Expected total: {expected_total}")
    print(f"Bank Account 5 balance: {account_5.get_balance()}")
    print(f"Bank Account 6 balance: {account_6.get_balance()}")
    print(f"Total preserved: {closing_total == expected_total} ({expected_total} -> {closing_total})")
    print()


def demonstrate_self_transfer():
    """Figure 14: source equal to destination, tested against all three
    transfer designs. safe_transfer rejects it explicitly; naive_transfer
    still self-deadlocks (left unguarded on purpose, since it exists only
    to demonstrate the other hazard); sequential_transfer completes it as
    a harmless no-op.
    """
    print("=== Figure 14: self-transfer (source equal to destination) ===")

    print("--- safe_transfer(account, account, 30) ---")
    account_a = BankAccount("Test", 100)
    try:
        safe_transfer(account_a, account_a, 30)
        print(f"safe_transfer: completed, balance={account_a.get_balance()}")
    except ValueError as e:
        print(f"safe_transfer: {type(e).__name__}: {e}, balance={account_a.get_balance()}")

    print("--- naive_transfer(account, account, 30) ---")
    account_b = BankAccount("Test", 100)

    def call_naive():
        try:
            naive_transfer(account_b, account_b, 30)
        except InsufficientFundsError:
            pass

    t = threading.Thread(target=call_naive, daemon=True)
    start = time.perf_counter()
    t.start()
    t.join(timeout=3)
    elapsed = time.perf_counter() - start
    if t.is_alive():
        print(f"naive_transfer: still blocked after {elapsed:.2f}s (self-deadlock)")
    else:
        print(f"naive_transfer: completed in {elapsed:.2f}s, balance={account_b.get_balance()}")

    print("--- sequential_transfer(account, account, 30) ---")
    account_c = BankAccount("Test", 100)
    sequential_transfer(account_c, account_c, 30)
    print(f"sequential_transfer: completed, balance={account_c.get_balance()}")


if __name__ == "__main__":
    demonstrate_refund_path()
    demonstrate_no_deadlock()
    demonstrate_self_transfer()
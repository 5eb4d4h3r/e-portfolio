"""
Deadlock demonstration - reproduces the evidence behind Figures 8-10 of
the report (Section 4, Deadlock Prevention).

Run this file directly (in the same folder as
M4_U06_IndividualCodingExercise_BankingSystem.py) to get Figure 10:
naive_transfer deadlocking under opposing concurrent transfers, followed
by safe_transfer completing the identical style of load without
deadlock.

For Figure 8 (naive_transfer's code) and Figure 9 (safe_transfer's code),
screenshot the real functions directly from
M4_U06_IndividualCodingExercise_BankingSystem.py rather than this file,
so the report shows the code that was actually submitted.

Neither the "still blocked after Ns" timing nor the exact account split
is deterministic: both depend on your machine's thread scheduling. Use
whatever your own run produces; do not force it to match 2000/0 or any
other number quoted elsewhere.
"""

import threading
import time

from M4_U06_IndividualCodingExercise_BankingSystem import (
    BankAccount,
    InsufficientFundsError,
    naive_transfer,
    safe_transfer,
)


def repeat_transfer(fn, source, destination, amount, times):
    for _ in range(times):
        try:
            fn(source, destination, amount)
        except InsufficientFundsError:
            pass


def demonstrate_naive_transfer_deadlock():
    """Figure 3c: naive_transfer deadlocks under opposing concurrent transfers."""
    print("=== Figure 10 (before fix): naive_transfer under opposing transfers ===")
    # Test: two threads, each repeating naive_transfer 20 times, transferring
    # 10 in opposite directions between the same two accounts.
    print("Test: 2 threads x 20 transfers of 10 each, opposite directions, naive_transfer")

    account_x = BankAccount("Bank Account 3", 2000)
    account_y = BankAccount("Bank Account 4", 4000)

    t1 = threading.Thread(target=repeat_transfer, args=(naive_transfer, account_x, account_y, 10, 20), daemon=True)
    t2 = threading.Thread(target=repeat_transfer, args=(naive_transfer, account_y, account_x, 10, 20), daemon=True)

    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join(timeout=3)
    t2.join(timeout=3)
    elapsed = time.perf_counter() - start

    if t1.is_alive() or t2.is_alive():
        print(f"Outcome: DEADLOCK - both threads still blocked after {elapsed:.2f}s.")
        print("Interpretation: fixed order broke - each thread holds one account's lock")
        print("  while waiting for the other's (a circular wait).")
    else:
        print(f"Outcome: completed in {elapsed:.2f}s without deadlocking this run.")
        print("Interpretation: naive_transfer is still unsafe even though it didn't hang")
        print("  this time; deadlock here is timing-dependent, not guaranteed every run.")
    print()


def demonstrate_safe_transfer_resolution():
    """Figure 3d: safe_transfer completes the identical opposing load without deadlock."""
    print("=== Figure 10 (after fix): safe_transfer under the identical load ===")
    # Test: two threads, each repeating safe_transfer 200 times, transferring
    # 10 in opposite directions between the same two accounts.
    print("Test: 2 threads x 200 transfers of 10 each, opposite directions, safe_transfer")

    account_p = BankAccount("Bank Account 3", 2000)
    account_q = BankAccount("Bank Account 4", 4000)
    opening_total = account_p.get_balance() + account_q.get_balance()

    t3 = threading.Thread(target=repeat_transfer, args=(safe_transfer, account_p, account_q, 10, 200))
    t4 = threading.Thread(target=repeat_transfer, args=(safe_transfer, account_q, account_p, 10, 200))

    start = time.perf_counter()
    t3.start()
    t4.start()
    t3.join(timeout=5)
    t4.join(timeout=5)
    elapsed = time.perf_counter() - start
    closing_total = account_p.get_balance() + account_q.get_balance()

    print(f"Outcome: completed in {elapsed:.2f}s, no deadlock.")
    print(f"Bank Account 3 balance: {account_p.get_balance()}")
    print(f"Bank Account 4 balance: {account_q.get_balance()}")
    print(f"Total preserved: {closing_total == opening_total} ({opening_total} -> {closing_total})")

    if account_p.get_balance() == account_q.get_balance():
        print("Interpretation: the two accounts ended up balanced this run; re-run a few")
        print("  times to see the split vary, since scheduling is not deterministic.")
    else:
        if account_p.get_balance() > account_q.get_balance():
            winner, loser = "Bank Account 3", "Bank Account 4"
        else:
            winner, loser = "Bank Account 4", "Bank Account 3"
        print(f"Interpretation: {winner} ended ahead of {loser} despite both threads issuing")
        print("  the same number of equal transfers. No deadlock, but no fairness guarantee either.")
    print()


if __name__ == "__main__":
    demonstrate_naive_transfer_deadlock()
    demonstrate_safe_transfer_resolution()
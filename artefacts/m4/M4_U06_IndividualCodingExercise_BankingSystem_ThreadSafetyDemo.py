"""
Thread-safety demonstration - reproduces the evidence behind Figures 5 and 6
of the report.

Run this file directly (in the same folder as M4_U06_IndividualCodingExercise_BankingSystem.py) to get:
  - Figure 5: Bank Account 1, a deliberately unsynchronised control account
    (the UnsafeAccount class below), showing lost updates under concurrent
    load with no lock.
  - Figure 6: Bank Account 2, the real, locked BankAccount from
    M4_U06_IndividualCodingExercise_BankingSystem.py, run under concurrent load for contrast.

Both scenarios print in the same shape (expected balance, then opening
balance, then closing balance, then outcome), so the two console outputs
can be read side by side.

UnsafeAccount is NOT part of the submitted banking system. It exists only
to prove the lock in BankAccount is load-bearing, not decorative, by
showing what happens without it. For the deposit()/withdraw() code itself,
screenshot the real methods directly from M4_U06_IndividualCodingExercise_BankingSystem.py rather than this
file, so the report shows the code that was actually submitted rather than
a second copy of it.

Because Figure 5 demonstrates a genuine race condition, its exact "lost
updates" number is not deterministic: it depends on your machine's thread
scheduling and will very likely differ from any number quoted elsewhere.
That is expected. Use whatever number your own run produces when you write
up the figure; do not force it to match anyone else's.
"""

import threading
import time

from M4_U06_IndividualCodingExercise_BankingSystem import BankAccount


class UnsafeAccount:
    """Deliberately unsynchronised account, used only to demonstrate the
    race condition that BankAccount's lock prevents. Not part of the
    submitted system.
    """

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        current = self.balance
        time.sleep(0.0001)       # widens the window between read and write
        current += amount
        self.balance = current  # another thread may have written here meanwhile


def report_result(figure_label, test_description, owner, expected, opening, closing, interpretation):
    """Print one scenario's result in a fixed shape, so Figure 5 and Figure 6
    are directly comparable: test parameters, then expected/opening/closing,
    then a pass/fail outcome line, then a plain-language interpretation of
    what that outcome actually means for this specific scenario.

    interpretation is supplied by the caller rather than computed here,
    because "expected minus closing" only means "N lost updates" when every
    operation moves the balance by the same fixed amount (true for Figure 5's
    deposit-only test, not true for Figure 6's mixed deposits/withdrawals of
    different sizes). Keeping that arithmetic in each caller, where the
    per-operation amount is actually known, avoids stating a number that
    would be wrong for a scenario with mixed amounts.
    """
    print(f"=== {figure_label} ===")
    print(f"Test: {test_description}")
    print(f"{owner} expected balance: {expected}")
    print(f"{owner} opening balance: {opening}")
    print(f"{owner} closing balance: {closing}")
    if closing == expected:
        print("Outcome: Balance is correct.")
    else:
        print(f"Outcome: Balance is WRONG - closing balance differs from expected by {abs(expected - closing)}.")
    print(f"Interpretation: {interpretation}")
    print()


def demonstrate_unsafe_account():
    """Figure 5: reproduces the race condition on an unsynchronised account."""
    owner = "Bank Account 1"
    opening_balance = 0

    # Test: 8 threads, each performing 200 deposits of 1, on the SAME
    # unsynchronised account. No withdrawals in this scenario: it isolates
    # the deposit-only race condition so the lost-update count is easy to
    # read (every lost unit is a lost deposit, nothing else is competing).
    deposit_n_threads, deposit_n_transactions, deposit_amount = 8, 200, 1

    account = UnsafeAccount(owner, opening_balance)
    threads = [
        threading.Thread(
            target=lambda: [account.deposit(deposit_amount) for _ in range(deposit_n_transactions)]
        )
        for _ in range(deposit_n_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected_balance = opening_balance + deposit_n_threads * deposit_n_transactions * deposit_amount
    total_attempts = deposit_n_threads * deposit_n_transactions
    shortfall = expected_balance - account.balance

    if shortfall > 0:
        # Safe to divide exactly: every deposit() call here moves the balance
        # by the same fixed amount, so the shortfall is an exact multiple of it.
        lost_updates = shortfall // deposit_amount
        interpretation = (
            f"{lost_updates} of {total_attempts} deposits were overwritten (lost updates), "
            f"not missing money."
        )
    else:
        interpretation = "no lost updates this run (non-deterministic - rerun to see it)."

    report_result(
        figure_label="Figure 5: Bank Account 1, unsynchronised (no lock)",
        test_description=f"{deposit_n_threads} threads x {deposit_n_transactions} deposits of "
                          f"{deposit_amount} each, no withdrawals, run concurrently",
        owner=owner,
        expected=expected_balance,
        opening=opening_balance,
        closing=account.balance,
        interpretation=interpretation,
    )


def demonstrate_locked_bankaccount():
    """Figure 6: the real, locked BankAccount under the same style of load,
    with withdrawals added so it also demonstrates mixed concurrent
    operations, not just deposits.
    """
    owner = "Bank Account 2"
    opening_balance = 10000

    # Test: 5 threads x 50 deposits of 20 each, running concurrently with
    # 4 threads x 50 withdrawals of 10 each, all against the SAME locked
    # account, to compare against Figure 5's deposit-only, unlocked test.
    deposit_n_threads, deposit_n_transactions, deposit_amount = 5, 50, 20
    withdraw_n_threads, withdraw_n_transactions, withdraw_amount = 4, 50, 10

    account = BankAccount(owner, opening_balance)

    def deposit_many():
        for _ in range(deposit_n_transactions):
            account.deposit(deposit_amount)

    def withdraw_many():
        for _ in range(withdraw_n_transactions):
            account.withdraw(withdraw_amount)

    threads = (
        [threading.Thread(target=deposit_many) for _ in range(deposit_n_threads)]
        + [threading.Thread(target=withdraw_many) for _ in range(withdraw_n_threads)]
    )
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total_deposited = deposit_n_threads * deposit_n_transactions * deposit_amount
    total_withdrawn = withdraw_n_threads * withdraw_n_transactions * withdraw_amount
    expected_balance = opening_balance + total_deposited - total_withdrawn

    if account.get_balance() == expected_balance:
        interpretation = "no lost updates: the lock forces each call to finish before the next one starts."
    else:
        interpretation = "unexpected - this would indicate a bug in the lock, not normal behaviour."

    report_result(
        figure_label="Figure 6: Bank Account 2, the real BankAccount (locked)",
        test_description=f"{deposit_n_threads} threads x {deposit_n_transactions} deposits of "
                          f"{deposit_amount} each, concurrently with {withdraw_n_threads} threads x "
                          f"{withdraw_n_transactions} withdrawals of {withdraw_amount} each",
        owner=owner,
        expected=expected_balance,
        opening=opening_balance,
        closing=account.get_balance(),
        interpretation=interpretation,
    )


if __name__ == "__main__":
    demonstrate_unsafe_account()
    demonstrate_locked_bankaccount()
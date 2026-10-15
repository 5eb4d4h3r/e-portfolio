"""
Command-pattern simulation demo - reproduces the evidence behind Figure 4
of the report (three simulated users acting concurrently on one shared
account, via TransactionSimulator and TransactionProcessor).

Run this file directly (in the same folder as
M4_U06_IndividualCodingExercise_BankingSystem.py).

M4_U06_IndividualCodingExercise_BankingSystem.py itself is a pure library:
importing or running it produces no output. All demonstrations live in
separate files like this one, so the library and its example usage stay
clearly separated, and each demo can be run and screenshotted
independently without unrelated output alongside it.
"""

from M4_U06_IndividualCodingExercise_BankingSystem import (
    BankAccount,
    TransactionProcessor,
    TransactionSimulator,
    DepositTransaction,
    WithdrawTransaction,
)


def demonstrate_command_pattern_simulation():
    """Figure 4: four users, one shared account, run concurrently through
    the Command pattern (Deposit/WithdrawTransaction -> TransactionProcessor
    -> TransactionSimulator). Three users only ever succeed; a fourth
    issues one deliberately oversized withdrawal, so the log shows both
    a successful and a failed transaction, not just successful ones.
    """
    print("=== Figure 4: Command-pattern simulation, four users, one shared account ===")

    shared_account = BankAccount("Shared Household Account", 500)
    processor = TransactionProcessor()
    simulator = TransactionSimulator(processor)

    # Test: User 1 makes 10 deposits of 50; User 2 makes 10 withdrawals of
    # 30; User 3 makes 1 deposit of 100 then 5 withdrawals of 40; all three
    # run concurrently against one account opened at 500. Every one of
    # these 26 succeeds regardless of execution order, because the total
    # withdrawn (500) never exceeds what has been deposited at any point
    # in any interleaving. User 4 then attempts a single withdrawal of
    # 10,000, far beyond anything the account ever holds, specifically to
    # produce a failed entry in the audit log.
    user_1_txns = [DepositTransaction(shared_account, 50) for _ in range(10)]
    user_2_txns = [WithdrawTransaction(shared_account, 30) for _ in range(10)]
    user_3_txns = ([DepositTransaction(shared_account, 100)]
                    + [WithdrawTransaction(shared_account, 40) for _ in range(5)])
    user_4_txns = [WithdrawTransaction(shared_account, 10_000)]

    print("Demo: User 1 - 10 deposits of 50; User 2 - 10 withdrawals of 30; User 3 - 1 "
          "deposit of 100 + 5 withdrawals of 40;")
    print("      User 4 - 1 withdrawal of 10,000 (designed to fail); opening balance 500; "
          "all run concurrently.")

    simulator.run_concurrently([user_1_txns, user_2_txns, user_3_txns, user_4_txns])

    expected_balance = 500 + (50 * 10) - (30 * 10) + 100 - (40 * 5)  # User 4 never succeeds, so it adds nothing
    closing_balance = shared_account.get_balance()
    history = processor.history()
    failed_count = sum(1 for entry in history if entry.startswith("FAILED"))

    print(f"Expected balance: {expected_balance}")
    print(f"Closing balance: {closing_balance}")
    print("Outcome:", "Balance is correct." if closing_balance == expected_balance else "Balance is WRONG.")
    print(f"Audit log entries recorded: {len(history)} "
          f"({len(history) - failed_count} succeeded, {failed_count} failed as expected)")

    # Look up specific, known transactions by identity, rather than taking
    # whichever entry the scheduler happened to log first: history() is
    # filled concurrently, so "the first Deposit" is not guaranteed to be
    # the same transaction on every run. Looking up these three by their
    # exact string form makes the sample identical on every run.
    print(f"Sample entries (3 of {len(history)}, looked up by transaction identity "
          f"so the result is the same on every run):")
    sample_txns = [("User 1's first deposit", user_1_txns[0]),
                    ("User 2's first withdrawal", user_2_txns[0]),
                    ("User 4's oversized withdrawal", user_4_txns[0])]
    for label, txn in sample_txns:
        match = next((entry for entry in history if entry.endswith(str(txn))), None)
        print(f"  {label}: {match}")


if __name__ == "__main__":
    demonstrate_command_pattern_simulation()
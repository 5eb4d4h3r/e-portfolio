###########################################################################
# Unit tests for M4_U06_IndividualCodingExercise_BankingSystem.py.
#
# Covers, in order: account creation and basic balance access, single-
# threaded deposit/withdraw correctness, overdraft rules, the sequential-
# transfer alternative with refund, transfer behaviour across overdraft
# combinations, self-transfer (source equal to destination), concurrent
# correctness under load, deadlock prevention, and the Command-pattern
# audit log.
#
# Each test prints a short Scope (what is being tested) and Outcome (what
# actually happened), in addition to the usual pass/fail from unittest, so
# running the file shows what each test proves, not just PASS/FAIL.
###########################################################################

import threading
import unittest
from unittest.mock import patch

from M4_U06_IndividualCodingExercise_BankingSystem import (
    BankAccount,
    InsufficientFundsError,
    RefundFailedError,
    DepositTransaction,
    WithdrawTransaction,
    TransferTransaction,
    TransactionProcessor,
    TransactionSimulator,
    safe_transfer,
    naive_transfer,
    sequential_transfer,
)


def report(scope, outcome):
    """Print what a test covered and what happened, so the console output
    is self-explanatory without reading the code alongside it.
    """
    print(f"\nScope: {scope}")
    print(f"Outcome: {outcome}")


class TestAccountCreation(unittest.TestCase):
    """Foundational checks: creating an account and reading its balance,
    independent of deposit(), withdraw(), or any transfer logic.
    """

    def test_account_stores_owner_and_opening_balance(self):
        account = BankAccount("Alice", 500)
        report(
            "BankAccount('Alice', 500)",
            f"owner={account.owner!r}, balance={account.get_balance()} "
            f"(expected 'Alice', 500)",
        )
        self.assertEqual(account.owner, "Alice")
        self.assertEqual(account.get_balance(), 500)

    def test_default_balance_is_zero(self):
        account = BankAccount("Bob")
        report(
            "BankAccount('Bob') with no balance given",
            f"balance is {account.get_balance()} (expected 0)",
        )
        self.assertEqual(account.get_balance(), 0)

    def test_account_number_is_assigned(self):
        account = BankAccount("Carol", 100)
        report(
            "BankAccount('Carol', 100)",
            f"account_number is {account.account_number!r} (expected an int)",
        )
        self.assertIsInstance(account.account_number, int)

    def test_account_numbers_are_unique(self):
        first = BankAccount("Dave", 100)
        second = BankAccount("Erin", 100)
        report(
            "two accounts created one after another",
            f"account_number {first.account_number} vs {second.account_number} "
            f"(expected different)",
        )
        self.assertNotEqual(first.account_number, second.account_number)

    def test_get_balance_reflects_current_state(self):
        account = BankAccount("Frank", 100)
        account.deposit(50)
        report(
            "get_balance() after a deposit(50) on an account opened with 100",
            f"balance is {account.get_balance()} (expected 150)",
        )
        self.assertEqual(account.get_balance(), 150)


class TestBankAccountSingleThreaded(unittest.TestCase):
    """Baseline correctness of deposit/withdraw, independent of concurrency."""

    def test_deposit_increases_balance(self):
        account = BankAccount("Test", 100)
        account.deposit(50)
        report(
            "deposit(50) on an account starting at 100",
            f"balance is {account.get_balance()} (expected 150)",
        )
        self.assertEqual(account.get_balance(), 150)

    def test_withdraw_decreases_balance(self):
        account = BankAccount("Test", 100)
        account.withdraw(40)
        report(
            "withdraw(40) on an account starting at 100",
            f"balance is {account.get_balance()} (expected 60)",
        )
        self.assertEqual(account.get_balance(), 60)

    def test_withdraw_insufficient_funds_raises(self):
        account = BankAccount("Test", 10)
        with self.assertRaises(InsufficientFundsError) as ctx:
            account.withdraw(20)
        report(
            "withdraw(20) from an account holding only 10",
            f"InsufficientFundsError raised: {ctx.exception}",
        )

    def test_deposit_non_positive_amount_raises(self):
        account = BankAccount("Test", 10)
        with self.assertRaises(ValueError):
            account.deposit(0)
        with self.assertRaises(ValueError):
            account.deposit(-5)
        report("deposit(0) and deposit(-5)", "both raised ValueError, as expected")

    def test_withdraw_non_positive_amount_raises(self):
        account = BankAccount("Test", 10)
        with self.assertRaises(ValueError) as ctx:
            account.withdraw(-1)
        report("withdraw(-1)", f"ValueError raised: {ctx.exception}")


class TestOverdraft(unittest.TestCase):
    """Overdraft is off by default and requires an explicit, positive
    limit to enable.
    """

    def test_overdraft_disabled_by_default(self):
        account = BankAccount("Test", 100)
        report(
            "new account created with no overdraft parameters",
            f"overdraft_allowed={account.overdraft_allowed}, "
            f"overdraft_limit={account.overdraft_limit} (expected False, None)",
        )
        self.assertFalse(account.overdraft_allowed)
        self.assertIsNone(account.overdraft_limit)

    def test_overdraft_allowed_without_limit_raises(self):
        with self.assertRaises(ValueError) as ctx:
            BankAccount("Test", 100, overdraft_allowed=True)
        report(
            "BankAccount(overdraft_allowed=True) with no limit given",
            f"ValueError raised: {ctx.exception}",
        )

    def test_overdraft_limit_without_allowed_raises(self):
        with self.assertRaises(ValueError) as ctx:
            BankAccount("Test", 100, overdraft_limit=50)
        report(
            "BankAccount(overdraft_limit=50) with overdraft_allowed left False",
            f"ValueError raised: {ctx.exception}",
        )

    def test_withdraw_within_overdraft_succeeds(self):
        account = BankAccount("Test", 100, overdraft_allowed=True, overdraft_limit=50)
        account.withdraw(120)
        report(
            "withdraw(120) from a 100 balance with a 50 overdraft limit",
            f"balance is {account.get_balance()} (expected -20)",
        )
        self.assertEqual(account.get_balance(), -20)

    def test_withdraw_beyond_overdraft_limit_raises(self):
        account = BankAccount("Test", 100, overdraft_allowed=True, overdraft_limit=50)
        with self.assertRaises(InsufficientFundsError) as ctx:
            account.withdraw(200)
        report(
            "withdraw(200) from a 100 balance with only a 50 overdraft limit",
            f"InsufficientFundsError raised: {ctx.exception}",
        )


class TestSequentialTransfer(unittest.TestCase):
    """sequential_transfer withdraws first, then deposits, and refunds the
    withdrawal if the deposit fails. An alternative transfer design,
    tested here but not used by TransferTransaction. deposit() cannot
    fail on its own once the amount is known positive, so these tests
    force a failure with unittest.mock to reach the refund and
    refund-failure paths.
    """

    def test_successful_transfer(self):
        source = BankAccount("Source", 100)
        destination = BankAccount("Destination", 50)
        sequential_transfer(source, destination, 30)
        report(
            "sequential_transfer(30) from Source(100) to Destination(50)",
            f"Source={source.get_balance()}, Destination={destination.get_balance()} "
            f"(expected 70, 80)",
        )
        self.assertEqual(source.get_balance(), 70)
        self.assertEqual(destination.get_balance(), 80)

    def test_withdrawal_failure_aborts_cleanly(self):
        source = BankAccount("Source", 10)
        destination = BankAccount("Destination", 50)
        with self.assertRaises(InsufficientFundsError):
            sequential_transfer(source, destination, 100)
        report(
            "sequential_transfer(100) from Source(10, not enough) to Destination(50)",
            f"withdrawal failed, nothing changed: Source={source.get_balance()}, "
            f"Destination={destination.get_balance()}",
        )
        self.assertEqual(source.get_balance(), 10)
        self.assertEqual(destination.get_balance(), 50)

    def test_deposit_failure_refunds_source(self):
        source = BankAccount("Source", 100)
        destination = BankAccount("Destination", 50)

        with patch.object(destination, "deposit", side_effect=RuntimeError("destination rejected the deposit")):
            with self.assertRaises(RuntimeError) as ctx:
                sequential_transfer(source, destination, 30)

        report(
            "sequential_transfer(30), deposit forced to fail",
            f"refunded back to Source={source.get_balance()} (expected 100), "
            f"Destination={destination.get_balance()} (expected 50), "
            f"error propagated: {ctx.exception}",
        )
        self.assertNotIsInstance(ctx.exception, RefundFailedError)
        self.assertEqual(source.get_balance(), 100)
        self.assertEqual(destination.get_balance(), 50)

    def test_deposit_and_refund_both_failing_raises_refund_failed_error(self):
        source = BankAccount("Source", 100)
        destination = BankAccount("Destination", 50)

        with patch.object(destination, "deposit", side_effect=RuntimeError("destination rejected the deposit")), \
             patch.object(source, "deposit", side_effect=RuntimeError("source cannot accept the refund")):
            with self.assertRaises(RefundFailedError) as ctx:
                sequential_transfer(source, destination, 30)

        report(
            "sequential_transfer(30), deposit AND refund both forced to fail",
            f"RefundFailedError raised, 30 stuck at Source={source.get_balance()} "
            f"(expected 70): {ctx.exception}",
        )
        self.assertEqual(source.get_balance(), 70)
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)


class TestTransferOverdraftCombinations(unittest.TestCase):
    """safe_transfer, the live transfer mechanism, across all four
    overdraft combinations: both sides allow it, neither does, and the
    two mixed cases. Only the source account's own settings should
    govern whether a transfer succeeds.
    """

    def test_both_accounts_overdraft_allowed(self):
        source = BankAccount("Source", 100, overdraft_allowed=True, overdraft_limit=100)
        destination = BankAccount("Destination", 100, overdraft_allowed=True, overdraft_limit=100)
        safe_transfer(source, destination, 150)
        report(
            "safe_transfer(150), both accounts allow overdraft",
            f"Source={source.get_balance()} (expected -50), "
            f"Destination={destination.get_balance()} (expected 250)",
        )
        self.assertEqual(source.get_balance(), -50)
        self.assertEqual(destination.get_balance(), 250)

    def test_neither_account_overdraft_allowed(self):
        source = BankAccount("Source", 100)
        destination = BankAccount("Destination", 100)
        with self.assertRaises(InsufficientFundsError):
            safe_transfer(source, destination, 150)
        report(
            "safe_transfer(150), neither account allows overdraft",
            f"failed as expected, balances unchanged: Source={source.get_balance()}, "
            f"Destination={destination.get_balance()}",
        )
        self.assertEqual(source.get_balance(), 100)
        self.assertEqual(destination.get_balance(), 100)

    def test_source_overdraft_allowed_destination_not(self):
        source = BankAccount("Source", 100, overdraft_allowed=True, overdraft_limit=100)
        destination = BankAccount("Destination", 100)
        safe_transfer(source, destination, 150)
        report(
            "safe_transfer(150), only the source allows overdraft",
            f"Source={source.get_balance()} (expected -50), "
            f"Destination={destination.get_balance()} (expected 250)",
        )
        self.assertEqual(source.get_balance(), -50)
        self.assertEqual(destination.get_balance(), 250)

    def test_destination_overdraft_allowed_source_not(self):
        source = BankAccount("Source", 100)
        destination = BankAccount("Destination", 100, overdraft_allowed=True, overdraft_limit=100)
        with self.assertRaises(InsufficientFundsError):
            safe_transfer(source, destination, 150)
        report(
            "safe_transfer(150), only the destination allows overdraft (should not matter)",
            f"failed as expected, balances unchanged: Source={source.get_balance()}, "
            f"Destination={destination.get_balance()}",
        )
        self.assertEqual(source.get_balance(), 100)
        self.assertEqual(destination.get_balance(), 100)


class TestSelfTransfer(unittest.TestCase):
    """What happens when source and destination are the same account.
    safe_transfer rejects this explicitly, since it would otherwise
    self-deadlock. naive_transfer still self-deadlocks: it is kept
    unguarded on purpose, since it exists only to demonstrate a hazard.
    sequential_transfer happens to complete as a harmless no-op, since it
    never nests locks in the first place.
    """

    def test_safe_transfer_rejects_same_account(self):
        account = BankAccount("Test", 100)
        with self.assertRaises(ValueError) as ctx:
            safe_transfer(account, account, 30)
        report(
            "safe_transfer(account, account, 30)",
            f"rejected: {ctx.exception}; balance unchanged at {account.get_balance()}",
        )
        self.assertEqual(account.get_balance(), 100)

    def test_naive_transfer_self_deadlocks(self):
        account = BankAccount("Test", 100)

        def call():
            try:
                naive_transfer(account, account, 30)
            except InsufficientFundsError:
                pass

        t = threading.Thread(target=call, daemon=True)
        t.start()
        t.join(timeout=2)

        report(
            "naive_transfer(account, account, 30)",
            f"still blocked after timeout: alive={t.is_alive()} "
            f"(self-deadlock expected; naive_transfer is left unguarded on purpose)",
        )
        self.assertTrue(t.is_alive(),
                         "Expected naive_transfer to self-deadlock when source is destination.")

    def test_sequential_transfer_same_account_is_a_no_op(self):
        account = BankAccount("Test", 100)
        sequential_transfer(account, account, 30)
        report(
            "sequential_transfer(account, account, 30)",
            f"completed with no error; balance is {account.get_balance()} (expected 100, unchanged)",
        )
        self.assertEqual(account.get_balance(), 100)


class TestConcurrentAccessIsRaceFree(unittest.TestCase):
    """Regression tests for the race condition the locking prevents.

    A high thread/iteration count is used deliberately: without correct
    locking, this volume of interleaving reliably exposes lost updates,
    even though a race condition is generally non-deterministic and
    cannot be proven absent purely by testing.
    """

    def test_concurrent_deposits_and_withdrawals_preserve_expected_balance(self):
        opening_balance = 10_000
        account = BankAccount("Stress", opening_balance)

        deposit_threads, deposit_iterations, deposit_amount = 8, 200, 5
        withdraw_threads, withdraw_iterations, withdraw_amount = 6, 200, 5

        def deposit_many():
            for _ in range(deposit_iterations):
                account.deposit(deposit_amount)

        def withdraw_many():
            for _ in range(withdraw_iterations):
                account.withdraw(withdraw_amount)

        threads = (
            [threading.Thread(target=deposit_many) for _ in range(deposit_threads)]
            + [threading.Thread(target=withdraw_many) for _ in range(withdraw_threads)]
        )
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = (
            opening_balance
            + deposit_threads * deposit_iterations * deposit_amount
            - withdraw_threads * withdraw_iterations * withdraw_amount
        )
        report(
            f"{deposit_threads} threads x {deposit_iterations} deposits of {deposit_amount}, "
            f"concurrently with {withdraw_threads} threads x {withdraw_iterations} "
            f"withdrawals of {withdraw_amount}",
            f"closing balance is {account.get_balance()} (expected {expected})",
        )
        self.assertEqual(account.get_balance(), expected)

    def test_concurrent_transfers_conserve_total_funds(self):
        account_a = BankAccount("A", 1000)
        account_b = BankAccount("B", 1000)
        total_before = account_a.get_balance() + account_b.get_balance()

        def transfer_a_to_b():
            for _ in range(300):
                try:
                    safe_transfer(account_a, account_b, 10)
                except InsufficientFundsError:
                    pass

        def transfer_b_to_a():
            for _ in range(300):
                try:
                    safe_transfer(account_b, account_a, 10)
                except InsufficientFundsError:
                    pass

        threads = [threading.Thread(target=transfer_a_to_b),
                   threading.Thread(target=transfer_b_to_a)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total_after = account_a.get_balance() + account_b.get_balance()
        report(
            "2 threads transferring 10 back and forth, 300 times each, between A(1000) and B(1000)",
            f"total before={total_before}, total after={total_after}, "
            f"A={account_a.get_balance()}, B={account_b.get_balance()}",
        )
        self.assertEqual(total_before, total_after)
        # Every individual balance must also stay non-negative.
        self.assertGreaterEqual(account_a.get_balance(), 0)
        self.assertGreaterEqual(account_b.get_balance(), 0)


class TestDeadlockPrevention(unittest.TestCase):
    """Timing-bounded evidence that safe_transfer avoids the circular wait
    naive_transfer is built to exhibit, and that sequential_transfer
    avoids it too, structurally, by never holding two locks at once.

    This does not prove the absence of deadlock in general; it shows
    that under the exact conditions that make naive_transfer hang
    reliably, the other two designs complete.
    """

    def test_naive_transfer_deadlocks_under_opposing_load(self):
        account_x = BankAccount("X", 1000)
        account_y = BankAccount("Y", 1000)

        def repeat(src, dst):
            for _ in range(10):
                try:
                    naive_transfer(src, dst, 10)
                except InsufficientFundsError:
                    pass

        t1 = threading.Thread(target=repeat, args=(account_x, account_y), daemon=True)
        t2 = threading.Thread(target=repeat, args=(account_y, account_x), daemon=True)
        t1.start()
        t2.start()
        t1.join(timeout=2)
        t2.join(timeout=2)

        report(
            "2 threads x 10 opposing naive_transfer calls between X and Y",
            f"still blocked after timeout: t1_alive={t1.is_alive()}, "
            f"t2_alive={t2.is_alive()} (deadlock expected)",
        )
        # This documents the hazard: it expects the naive version to still
        # be blocked. A demonstration, not a design goal.
        self.assertTrue(t1.is_alive() or t2.is_alive(),
                         "Expected naive_transfer to deadlock under this load; "
                         "if this fails, the hazard was not reproduced this run.")

    def test_safe_transfer_completes_under_the_same_opposing_load(self):
        account_p = BankAccount("P", 1000)
        account_q = BankAccount("Q", 1000)

        def repeat(src, dst):
            for _ in range(200):
                try:
                    safe_transfer(src, dst, 10)
                except InsufficientFundsError:
                    pass

        t1 = threading.Thread(target=repeat, args=(account_p, account_q))
        t2 = threading.Thread(target=repeat, args=(account_q, account_p))
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)

        report(
            "2 threads x 200 opposing safe_transfer calls between P and Q",
            f"completed without deadlock: t1_alive={t1.is_alive()}, t2_alive={t2.is_alive()}, "
            f"total={account_p.get_balance() + account_q.get_balance()} (expected 2000)",
        )
        self.assertFalse(t1.is_alive() or t2.is_alive(),
                          "safe_transfer should not deadlock under the same load.")
        self.assertEqual(account_p.get_balance() + account_q.get_balance(), 2000)

    def test_sequential_transfer_completes_under_the_same_opposing_load(self):
        account_m = BankAccount("M", 1000)
        account_n = BankAccount("N", 1000)

        def repeat(src, dst):
            for _ in range(200):
                try:
                    sequential_transfer(src, dst, 10)
                except InsufficientFundsError:
                    pass

        t1 = threading.Thread(target=repeat, args=(account_m, account_n))
        t2 = threading.Thread(target=repeat, args=(account_n, account_m))
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)

        report(
            "2 threads x 200 opposing sequential_transfer calls between M and N",
            f"completed without deadlock: t1_alive={t1.is_alive()}, t2_alive={t2.is_alive()}, "
            f"total={account_m.get_balance() + account_n.get_balance()} (expected 2000)",
        )
        self.assertFalse(t1.is_alive() or t2.is_alive(),
                          "sequential_transfer should never deadlock: it never holds two locks at once.")
        self.assertEqual(account_m.get_balance() + account_n.get_balance(), 2000)


class TestCommandPatternAuditLog(unittest.TestCase):
    """The Command-pattern layer must log every attempted transaction,
    including failures, and must not lose entries under concurrency.
    """

    def test_successful_and_failed_transactions_are_both_logged(self):
        account = BankAccount("Test", 50)
        processor = TransactionProcessor()

        processor.process(DepositTransaction(account, 10))
        with self.assertRaises(InsufficientFundsError):
            processor.process(WithdrawTransaction(account, 1000))

        history = processor.history()
        report(
            "one successful deposit, one failed withdrawal, via TransactionProcessor",
            f"log has {len(history)} entries (expected 2): {history}",
        )
        self.assertEqual(len(history), 2)
        self.assertTrue(history[0].startswith("OK"))
        self.assertTrue(history[1].startswith("FAILED"))

    def test_concurrent_users_produce_one_log_entry_per_transaction(self):
        account = BankAccount("Shared", 1000)
        processor = TransactionProcessor()
        simulator = TransactionSimulator(processor)

        user_lists = [
            [DepositTransaction(account, 1) for _ in range(100)],
            [WithdrawTransaction(account, 1) for _ in range(100)],
            [TransferTransaction(account, BankAccount("Other"), 1) for _ in range(50)],
        ]
        simulator.run_concurrently(user_lists)

        report(
            "3 simulated users issuing 250 transactions concurrently on shared accounts",
            f"audit log has {len(processor.history())} entries (expected 250)",
        )
        self.assertEqual(len(processor.history()), 250)


if __name__ == "__main__":
    unittest.main(verbosity=2)
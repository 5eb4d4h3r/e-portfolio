###########################################################################
# Thread-safe banking system.
#
# BankAccount stores its balance behind a private attribute and a lock, so
# deposits, withdrawals, and balance checks are all safe under concurrent
# access. Overdraft is off by default and requires an explicit limit to
# enable.
#
# Three transfer designs are provided:
#
#   - naive_transfer: locks source then destination in call order. Kept
#     only to demonstrate the deadlock this allows when two transfers run
#     in opposite directions at once. Not used by the system.
#   - safe_transfer: locks both accounts together, always in ascending
#     account_number order regardless of direction, removing the circular
#     wait naive_transfer allows. This is the transfer TransferTransaction
#     actually uses.
#   - sequential_transfer: withdraws from source, then deposits into
#     destination, as two separate operations with no dual-lock step at
#     all, refunding the withdrawal if the deposit fails. Tested as an
#     alternative design, closer to how a real sequential debit-then-credit
#     payment behaves, but not adopted for the live system.
# 
# Each operation is also available as a Command object (see the Transaction
# classes), so a TransactionProcessor can log every attempt and a
# TransactionSimulator can run several users concurrently against shared
# accounts.
###########################################################################

import threading
import time
from abc import ABC, abstractmethod
from itertools import count


class InsufficientFundsError(ValueError):
    """Raised when a withdrawal or transfer exceeds the available balance."""


class RefundFailedError(RuntimeError):
    """Raised when sequential_transfer's compensating refund also fails
    after the deposit leg failed. The withdrawn amount is stuck between
    the two accounts and needs manual reconciliation by a bank operator,
    rather than a further automatic retry.
    """


class BankAccount:
    """A bank account with a thread-safe balance.

    The balance is private. Ordinary callers change it only through
    deposit() and withdraw(). safe_transfer and naive_transfer, below,
    need to hold two accounts' locks together for one combined update, so
    they use the internal _apply_delta()/_available_funds() methods
    instead of calling deposit()/withdraw() (which would try to
    re-acquire a lock already held). sequential_transfer does not need
    this: it only ever calls the public deposit()/withdraw() methods.
    """

    _id_counter = count(1)

    def __init__(self, owner, balance=0, overdraft_allowed=False, overdraft_limit=None):
        self.account_number = next(BankAccount._id_counter)
        self.owner = owner
        self.__balance = balance
        self._lock = threading.Lock()  # protects this account's balance only

        if overdraft_allowed:
            if overdraft_limit is None or overdraft_limit <= 0:
                raise ValueError(
                    "overdraft_limit must be a positive amount when overdraft_allowed is True."
                )
            self.overdraft_allowed = True
            self.overdraft_limit = overdraft_limit
        else:
            if overdraft_limit is not None:
                raise ValueError(
                    "overdraft_limit must be left unset when overdraft_allowed is False."
                )
            self.overdraft_allowed = False
            self.overdraft_limit = None

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        with self._lock:
            self._apply_delta(amount)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        with self._lock:
            if amount > self._available_funds():
                raise InsufficientFundsError(
                    f"Account {self.account_number} has insufficient funds."
                )
            self._apply_delta(-amount)

    def get_balance(self):
        with self._lock:
            return self.__balance

    def _available_funds(self):
        """Balance plus overdraft headroom, if any. Caller must already
        hold self._lock.
        """
        headroom = self.overdraft_limit if self.overdraft_allowed else 0
        return self.__balance + headroom

    def _apply_delta(self, delta):
        """Change the balance by delta without locking. Caller must
        already hold self._lock. Used internally, and by safe_transfer/
        naive_transfer, which need to update two accounts under both
        locks at once; ordinary callers should use deposit()/withdraw().
        """
        self.__balance += delta

    def __repr__(self):
        return f"BankAccount(account_number={self.account_number}, owner={self.owner!r})"


def safe_transfer(source, destination, amount):
    """Move funds between two accounts without risking deadlock.

    Both locks are acquired together, always in ascending account_number
    order, regardless of which account is the source. This avoids the
    circular wait that naive_transfer below can produce. Used by
    TransferTransaction.

    source and destination must be different accounts: if they were the
    same, sorted() would return that one account twice, and the two
    nested `with` blocks below would try to acquire its plain, non-
    reentrant Lock a second time from the thread that already holds it,
    self-deadlocking. Checked explicitly here rather than left to hang.
    """
    if amount <= 0:
        raise ValueError("Transfer amount must be positive.")
    if source is destination:
        raise ValueError("Cannot transfer to the same account.")
    first, second = sorted((source, destination), key=lambda acc: acc.account_number)
    with first._lock:
        with second._lock:
            if amount > source._available_funds():
                raise InsufficientFundsError(
                    f"Account {source.account_number} has insufficient funds."
                )
            source._apply_delta(-amount)
            destination._apply_delta(amount)


def naive_transfer(source, destination, amount):
    """Deadlock-prone transfer, kept only to demonstrate the hazard.

    Locks are acquired in call order (source, then destination). If one
    thread transfers A to B while another transfers B to A at the same
    time, each can hold one lock while waiting for the other: a circular
    wait. Not used by TransactionProcessor.
    """
    with source._lock:
        time.sleep(0.05)  # widens the window so the race is reliably observable
        with destination._lock:
            if amount > source._available_funds():
                raise InsufficientFundsError("Insufficient funds.")
            source._apply_delta(-amount)
            destination._apply_delta(amount)


def sequential_transfer(source, destination, amount):
    """Move funds as two separate, sequential operations instead of one
    dual-locked transfer: withdraw, then deposit, using only source and
    destination's own public methods.

    Withdraw first. If that fails, nothing has happened and the transfer
    is simply aborted. If the withdrawal succeeds but the deposit then
    fails, the withdrawal is refunded back to source. If the refund
    itself also fails, RefundFailedError is raised so the failure
    surfaces for manual handling instead of disappearing. An alternative
    design, tested but not used by TransferTransaction.
    """
    if amount <= 0:
        raise ValueError("Transfer amount must be positive.")

    source.withdraw(amount)

    try:
        destination.deposit(amount)
    except Exception as deposit_error:
        try:
            source.deposit(amount)
        except Exception as refund_error:
            raise RefundFailedError(
                f"Deposit to account {destination.account_number} failed "
                f"({deposit_error}); refunding account {source.account_number} "
                f"also failed ({refund_error}). {amount} needs manual reconciliation."
            ) from refund_error
        raise


# ---------------------------------------------------------------------------
# Command pattern: each transaction is an object, decoupling the invoker
# (TransactionProcessor) from the receiver (BankAccount) and giving a
# single place to log every attempted operation.
# ---------------------------------------------------------------------------

class Transaction(ABC):
    """Command interface for a single banking operation."""

    @abstractmethod
    def execute(self):
        """Perform the operation. Raises on failure."""

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class DepositTransaction(Transaction):
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

    def execute(self):
        self.account.deposit(self.amount)

    def __str__(self):
        return f"Deposit({self.amount}) -> account {self.account.account_number}"


class WithdrawTransaction(Transaction):
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

    def execute(self):
        self.account.withdraw(self.amount)

    def __str__(self):
        return f"Withdraw({self.amount}) <- account {self.account.account_number}"


class TransferTransaction(Transaction):
    def __init__(self, source, destination, amount):
        self.source = source
        self.destination = destination
        self.amount = amount

    def execute(self):
        safe_transfer(self.source, self.destination, self.amount)

    def __str__(self):
        return (f"Transfer({self.amount}) account {self.source.account_number} "
                f"-> account {self.destination.account_number}")


class TransactionProcessor:
    """Invoker: executes Transaction commands and keeps an audit log.

    The log has its own lock, separate from any BankAccount lock, so log
    contention is independent of balance contention.
    """

    def __init__(self):
        self._log = []
        self._log_lock = threading.Lock()

    def process(self, transaction):
        outcome = "OK"
        try:
            transaction.execute()
        except Exception as exc:
            outcome = f"FAILED: {exc}"
            raise
        finally:
            with self._log_lock:
                self._log.append(f"{outcome} | {transaction}")

    def history(self):
        with self._log_lock:
            return list(self._log)


class TransactionSimulator:
    """Client: runs several users' transactions concurrently, one thread
    per user.
    """

    def __init__(self, processor):
        self.processor = processor

    def run_user(self, transactions):
        for txn in transactions:
            try:
                self.processor.process(txn)
            except (ValueError, InsufficientFundsError, RefundFailedError):
                # A failed transaction is expected under concurrent load
                # and is already recorded in the audit log; the user's
                # remaining transactions still proceed.
                continue

    def run_concurrently(self, user_transaction_lists):
        threads = [
            threading.Thread(target=self.run_user, args=(txns,))
            for txns in user_transaction_lists
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
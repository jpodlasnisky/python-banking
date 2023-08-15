# coding=utf-8

from hashlib import sha512
from re import fullmatch
from tabnanny import check
from uuid import UUID, uuid4
from typing import Tuple

from eventsourcing.domain import Aggregate, event


class Account(Aggregate):
    """
    This is the model of the aggregate, it has
    many events that happen, and when you load
    a model using the application object (Bank)
    you get all events saved for the id of the
    individual model. This never saves itself,
    all saving happens in the Bank application.
    """

    _id: UUID

    @event("Opened")
    def __init__(
        self,
        id: UUID,
        full_name: str,
        email_address: str,
        password: str,
    ):
        self._id = id
        self.full_name = full_name
        self.email_address = email_address
        self.password = password
        self.balance = 0
        self.is_closed = False
        self.overdraft_limit = 0

        # complete this function and others below as needed

    @event("Closed")
    def close(self) -> None:
        self.is_closed = True


    @event("Credited")
    def credit(self, amount_in_cents: int) -> None:
        if amount_in_cents <= 0:
            raise InvalidDeposit(amount_in_cents)
        self.balance += amount_in_cents

    @event("Debited")
    def debit(self, amount_in_cents: int) -> None:
        if amount_in_cents <= 0:
            raise ValueError("Invalid amount")
        if self.balance - amount_in_cents < -self.overdraft_limit:
            raise InsufficientFundsError(
                self.balance, amount_in_cents)
        self.balance -= amount_in_cents

    @event("Transferred")
    def transfer_validation(self, to_account_id: UUID, amount_in_cents: int, transaction_id: UUID) -> None:
             
        if amount_in_cents <= 0:
            raise InvalidAmount(amount_in_cents)

        if self.balance - amount_in_cents < -self.overdraft_limit:
            raise InsufficientFundsError(self.balance, amount_in_cents)
        
        if self.check_is_closed():
            raise AccountClosedError(self._id)
        
        if self._id == to_account_id:
            raise TransactionError(transaction_id)


    @event("OverdraftLimitChanged")
    def set_overdraft_limit(self, account_id: UUID, amount_in_cents: int) -> None:
        if amount_in_cents < 0:
            raise AssertionError()
        self.overdraft_limit = amount_in_cents
        self.check_is_closed()


    def authenticate(self, email_address: str, password: str) -> bool:
        if not fullmatch("[^@]+@[^@]+\.[^@]+", email_address):
            raise BadCredentials(email_address)

        hashed_password = sha512(password.encode()).hexdigest()

        if self.email_address != email_address or self.password != hashed_password:
            raise BadCredentials(email_address)
        return True

    @event("PasswordChanged")
    def change_password(self, new_password: str) -> None:
        self.password = sha512(new_password.encode()).hexdigest()
    def check_is_closed(self) -> bool:
        return self.is_closed


class TransactionError(Exception):
    def __init__(self, transaction_id: UUID):
        self.transaction_id = transaction_id
        super().__init__(f"Transaction {transaction_id} ERROR")


class AccountClosedError(Exception):
    def __init__(self, account_id: UUID):
        self.account_id = account_id
        super().__init__(f"Account {account_id} is closed")


class InsufficientFundsError(Exception):
    def __init__(self, balance: int, amount_in_cents: int):
        self.balance = balance
        self.amount_in_cents = amount_in_cents
        super().__init__(
            f"Insufficient funds: balance {balance} < amount {amount_in_cents}"
        )


class BadCredentials(Exception):
    def __init__(self, email_address: str):
        self.email_address = email_address
        super().__init__(f"Bad credentials for {email_address}")


class InvalidAmount(Exception):
    def __init__(self, amount_in_cents: int):
        super().__init__(
            f"Cannot transfer negative or zero amount {amount_in_cents}")


class InvalidDeposit(Exception):
    def __init__(self, amount_in_cents: int):
        super().__init__(f"Cannot deposit negative amount {amount_in_cents}")


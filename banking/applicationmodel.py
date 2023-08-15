# coding=utf-8

from uuid import NAMESPACE_URL, UUID, uuid5

from eventsourcing.application import AggregateNotFound, Application

from banking.domainmodel import Account, AccountClosedError, BadCredentials

from hashlib import sha512


class Bank(Application):

    """
    This is the model of the application, it has
    all of its events in the from of aggregate
    events that it loads. This loads and
    saves aggregates and forms the business logic
    for reading and writing.

    To create an aggregate run:
      new_account = Account(...)

    To load existing aggregates run:
      account1 = self.repository.get(account_id1)
      account2 = self.repository.get(account_id2)

    To save any aggregates run:
      self.save(account1, account2, new_account)
    """

    # Account actions
    def open_account(
        self,
        full_name: str,
        email_address: str,
        password: str,
    ) -> UUID:
        """
        The first few lines of this function are
        completed, but there is more to do.
        """
        password = sha512(password.encode()).hexdigest()
        account = Account(
            self.get_account_id_by_email(email_address),
            full_name=full_name,
            email_address=email_address,
            password=password,
        )
            
                
        self.save(account)

        return account.id

    def get_account_id_by_email(self, email_address: str) -> UUID:
        account_id = uuid5(NAMESPACE_URL, email_address)

        try:
            account = self.repository.get(account_id)
            return account.id
        except AggregateNotFound:
            return account_id

    def close_account(self, account_id: UUID) -> None:
        account = self.get_account(account_id)
        account.close()
        self.save(account)

    def authenticate(self, email_address: str, password: str) -> UUID:
        account_id = self.get_account_id_by_email(email_address)
        account = self.get_account(account_id)
        try:
            account.authenticate(email_address, password)
        except BadCredentials:
            raise BadCredentials(email_address)
        return account_id

    def validate_password(self, account_id: UUID, password: str) -> bool:
        account = self.get_account(account_id)
        hashed_password = sha512(password.encode()).hexdigest()
        if hashed_password != account.password:
            raise BadCredentials(account.email_address)
        return True

    def change_password(self, account_id: UUID, password: str, new_password: str) -> None:
        if self.validate_password(account_id, password):
            account = self.get_account(account_id)
            account.change_password(new_password)
            self.save(account)

    def get_balance(self, account_id: UUID) -> int:

        try:
            account = self.get_account(account_id)
            return account.balance
        except AggregateNotFound:
            raise AccountNotFoundError(account_id)

    def deposit_funds(self, credit_account_id: UUID, amount_in_cents: int) -> None:
        try:
            account = self.get_account(credit_account_id)
            if account.check_is_closed():
                raise AccountClosedError(credit_account_id)
            account.credit(amount_in_cents)
            self.save(account)

        except AggregateNotFound:
            raise AccountNotFoundError(credit_account_id)

    def withdraw_funds(self, debit_account_id: UUID, amount_in_cents: int) -> None:
        try:
            account = self.get_account(debit_account_id)
            if account.check_is_closed():
                raise AccountClosedError(debit_account_id)
            account.debit(amount_in_cents)
            self.save(account)
        except AggregateNotFound:
            raise AccountNotFoundError(debit_account_id)

    def transfer_funds(self, debit_account_id: UUID, credit_account_id: UUID, amount_in_cents: int) -> None:
        transaction_id = uuid5(NAMESPACE_URL, f"{debit_account_id}{credit_account_id}{amount_in_cents}")
        
        try:
            from_account = self.get_account(debit_account_id)
            to_account = self.get_account(credit_account_id)
            from_account.transfer_validation(to_account.id, amount_in_cents, transaction_id)
            from_account.debit(amount_in_cents)
            to_account.credit(amount_in_cents)
            self.save(from_account, to_account)

        except AggregateNotFound:
            raise AccountNotFoundError(debit_account_id)


    def get_overdraft_limit(self, account_id: UUID) -> int:
        try:
            account = self.get_account(account_id)
            return account.overdraft_limit
        except AggregateNotFound:
            raise AccountNotFoundError(account_id)

    def set_overdraft_limit(self, account_id: UUID, amount_in_cents: int) -> None:
        try:
            account = self.get_account(account_id)
            if account.check_is_closed():
                raise AccountClosedError(account_id)
            account.set_overdraft_limit(account_id, amount_in_cents)
            self.save(account)
        except AggregateNotFound:
            raise AccountNotFoundError(account_id)

    def get_account(self, account_id: UUID) -> Account:
        return self.repository.get(account_id)


class AccountNotFoundError(Exception):
    def __init__(self, account_id: UUID):
        super().__init__(f"Account {account_id} not found")
        self.account_id = account_id

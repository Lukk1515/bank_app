import psycopg2
import os
import uuid
from decimal import Decimal
from enum import Enum
from bank_app.models import UserModel, BankAccountModel, TransactionModel
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine

BASE = declarative_base()

DB_NAME = (os.getenv("DBNAME"),)
PASSWORD = (os.getenv("PASSWORD"),)
HOST = (os.getenv("HOST"),)
PORT = (os.getenv("PORT"),)


class TransactionType(Enum):
    BLIK = "BLIK"
    DEBET_CARD = "Debet Card"
    FUNDS_TRANSFER = "Funds Transfer"


class TransactionException(Exception):
    pass


class AccountFundsError(Exception):
    pass


class BankAccount:
    def __init__(self):
        """
        Initialize the BankAccount class with a database connection and schema.

        Parameters:
        schema (str): The schema name for the database.
        """
        self._engine = create_engine("postgresql://postgres:lucas@localhost/postgres")
        self._session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        BASE.metadata.create_all(self._engine)

    def get_balance(self, user_id: uuid.UUID) -> Decimal:
        """
        Retrieve the account balance for a given user ID.

        Parameters:
        user_id (UUID): The user ID.

        Returns:
        Decimal: The account balance.
        """
        with self._session_local() as session:
            account = session.query(BankAccountModel).filter_by(user_id=user_id).first()

            if account is None:
                raise ValueError(f"Account for user {user_id} not found.")

            return account.balance

    def add_user(self, model: UserModel) -> uuid.UUID:
        """
        Add a new user to the database.

        Parameters:
        name (str): User's first name.
        surname (str): User's surname.
        phone_number (str): User's phone number.
        email (str): User's email (must be unique).
        city (str): User's city.
        postal_code (str): User's postal code.
        street (str): User's street.
        street_number (int): User's street number.
        acommodation_number (int): User's accommodation number.

        Returns:
        uuid.UUID: The newly created user's ID.
        """

        with self._session_local() as session:
            session.add(model)
            session.commit()  # Zatwierdzenie zmian
            return model.user_id  # Zwracamy ID nowego użytkownika

    def remove_user(self, user_id: uuid.UUID) -> None:
        """
        Remove a user with the specified ID.

        Parameters:
        user_id (uuid.UUID): The user ID to remove.

        Raises:
        ValueError: If the user does not exist.
        """
        with self._session_local() as session:
            user = session.query(UserModel).filter_by(user_id=user_id).first()

            if user is None:
                raise ValueError(f"User with ID {user_id} not found.")

            session.delete(user)
            session.commit()

    def add_balance(self, user_id: uuid.UUID, amount: Decimal) -> None:
        """
        Add a specified amount to the user's account balance.

        Parameters:
        user_id (uuid.UUID): The user ID.
        amount (Decimal): The amount to add.

        Raises:
        ValueError: If the user account does not exist.
        """
        with self._session_local() as session:
            account = session.query(BankAccountModel).filter_by(user_id=user_id).first()

            if account is None:
                raise ValueError(f"Account for user {user_id} not found.")

            account.balance += amount
            session.commit()

    def remove_balance(self, user_id: uuid.UUID, amount: Decimal) -> None:
        """
        Deduct a specified amount from the user's account balance.

        Parameters:
        user_id (uuid.UUID): The user ID.
        amount (Decimal): The amount to deduct.

        Raises:
        AccountFundsError: If the resulting balance is negative.
        ValueError: If the user account does not exist.
        """
        with self._session_local() as session:
            account = session.query(BankAccountModel).filter_by(user_id=user_id).first()

            if account is None:
                raise ValueError(f"Account for user {user_id} not found.")

            if account.balance < amount:
                raise AccountFundsError("Insufficient funds in the account.")

            account.balance -= amount
            session.commit()

    def funds_transfer(
        self, user_id_from: uuid.UUID, user_id_to: uuid.UUID, amount: Decimal
    ) -> None:
        """
        Transfer funds between two accounts.

        Parameters:
        user_id_from (uuid.UUID): The ID of the sender.
        user_id_to (uuid.UUID): The ID of the recipient.
        amount (Decimal): The amount to transfer.

        Raises:
        ValueError: If the sender does not have enough funds.
        """
        with self._session_local() as session:
            sender = (
                session.query(BankAccountModel).filter_by(user_id=user_id_from).first()
            )
            receiver = (
                session.query(BankAccountModel).filter_by(user_id=user_id_to).first()
            )

            if sender is None:
                raise ValueError(f"Sender account with ID {user_id_from} not found.")
            if receiver is None:
                raise ValueError(f"Receiver account with ID {user_id_to} not found.")

            if sender.balance < amount:
                raise AccountFundsError("Insufficient funds for transfer.")

            sender.balance -= amount
            receiver.balance += amount

            session.commit()

    def user_exists(self, user_id: uuid.UUID) -> bool:
        """
        Check if a user with the specified ID exists.

        Parameters:
        user_id (uuid.UUID): The user ID to check.

        Returns:
        bool: True if the user exists, False otherwise.
        """
        with self._session_local() as session:
            return session.query(
                session.query(UserModel).filter_by(user_id=user_id).exists()
            ).scalar()

    def update_balance(self, user_id: uuid.UUID, new_balance: Decimal) -> None:
        """
        Update the user's account balance to a new value.

        Parameters:
        user_id (uuid.UUID): The user ID.
        new_balance (Decimal): The new account balance.

        Raises:
        ValueError: If the user account is not found.
        """
        with self._session_local() as session:
            account = session.query(BankAccountModel).filter_by(user_id=user_id).first()

            if account is None:
                raise ValueError(f"Account with user ID {user_id} not found.")

            account.balance = new_balance
            session.commit()

    def get_all_users(self) -> list[uuid.UUID]:
        """
        Retrieve a list of all user IDs.

        Returns:
        list[uuid.UUID]: A list of user IDs.
        """
        with self._session_local() as session:
            user_ids = session.query(UserModel.user_id).all()
            return [user_id[0] for user_id in user_ids]

    def add_multiple_users(self, users_list: list[dict]) -> None:
        """
        Add multiple users from a list of dictionaries.

        Parameters:
        users_list (list[dict]): A list of dictionaries containing user details.
        """
        with self._session_local() as session:
            users = [
                UserModel(
                    name=user["name"],
                    surname=user["surname"],
                    phone_number=user["phone_number"],
                    email=user["email"],
                    city=user["city"],
                    postal_code=user["postal_code"],
                    street=user["street"],
                    street_number=user["street_number"],
                    acommodation_number=user["acommodation_number"],
                )
                for user in users_list
            ]

            session.add_all(users)
            session.commit()

    def reset_balance(self, user_id: uuid.UUID) -> None:
        """
        Resets the balance of a user's bank account to zero.

        Parameters:
        user_id (uuid.UUID): The ID of the user whose account balance is to be reset.

        Raises:
        ValueError: If no bank account is found for the given user ID.

        Returns:
        None: This method does not return any value. It commits the balance reset to the database.
        """
        with self._session_local() as session:
            bank_account = (
                session.query(BankAccountModel).filter_by(user_id=user_id).first()
            )

            if bank_account is None:
                raise ValueError(f"Bank account for user with ID {user_id} not found.")

            bank_account.balance = 0
            session.commit()

    def create_bank_account(self, model: BankAccountModel):
        """
        Creates a new bank account in the system.

        Parameters:
        model (BankAccountModel): The bank account model instance containing the account details.

        Returns:
        None: This method does not return any value. It commits the new bank account creation to the database.
        """
        with self._session_local() as session:
            session.add(model)
            session.commit()

    def create_transaction(self, model: TransactionModel):
        """
        Creates a new transaction record in the system.

        Parameters:
        model (TransactionModel): The transaction model instance containing the transaction details.

        Returns:
        None: This method does not return any value. It commits the new transaction to the database.
        """
        with self._session_local() as session:
            session.add(model)
            session.commit()

    def get_all_balance(self) -> dict[uuid.UUID, Decimal]:
        """
        Retrieves a dictionary of all user balances in a single query.

        Returns:
        dict[uuid.UUID, Decimal]: A dictionary {user_id: balance}
        """
        with self._session_local() as session:
            accounts = session.query(
                BankAccountModel.user_id, BankAccountModel.balance
            ).all()
            return {user_id: balance for user_id, balance in accounts}

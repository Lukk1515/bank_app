import psycopg2
import os


class TransactionException(Exception):
    pass


class AccountFundsError(Exception):
    pass


class BankAccount:
    def __init__(self, schema: str = "bank_app"):
        """
        Initialize the BankAccount class with a database connection and schema.

        Parameters:
        schema (str): The schema name for the database.
        """
        self._conn = self._connect_to_db()
        self.schema = schema

    def _connect_to_db(self) -> psycopg2.extensions.connection:
        """
        Establish a connection to the PostgreSQL database.

        Returns:
        psycopg2.extensions.connection: A connection object to the database.
        """
        return psycopg2.connect(
            dbname=os.getenv("DBNAME"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
        )

    def _execute_query(self, query: str, params: tuple | None = None):
        """
        Execute a database query and handle transactions.

        Parameters:
        query (str): The SQL query to execute.
        params (tuple | None): Parameters for the SQL query.

        Returns:
        list: Query results for SELECT queries.
        """
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    return cursor.fetchall()
                self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            raise e

    def get_balance(self, record_id: int) -> float:
        """
        Retrieve the account balance for a given user ID.

        Parameters:
        record_id (int): The user ID.

        Returns:
        float: The account balance.
        """
        query = f"SELECT balance FROM {self.schema}.accounts WHERE user_id = %s"
        result = self._execute_query(query, (record_id,))
        return result[0][0]

    def add_user(self, user_id: int, balance: float) -> None:
        """
        Add a new user with the specified ID and balance.

        Parameters:
        user_id (int): The user ID.
        balance (float): The initial account balance.
        """
        query = f"INSERT INTO {self.schema}.accounts (user_id, balance) VALUES (%s, %s)"
        self._execute_query(query, (user_id, balance))

    def remove_user(self, user_id: int) -> None:
        """
        Remove a user with the specified ID.

        Parameters:
        user_id (int): The user ID to remove.
        """
        query = f"DELETE FROM {self.schema}.accounts WHERE user_id = %s"
        self._execute_query(query, (user_id,))

    def add_balance(self, user_id: int, amount: float) -> None:
        """
        Add a specified amount to the user's account balance.

        Parameters:
        user_id (int): The user ID.
        amount (float): The amount to add.
        """
        new_balance = self.get_balance(user_id) + amount
        query = f"UPDATE {self.schema}.accounts SET balance = %s WHERE user_id = %s"
        self._execute_query(query, (new_balance, user_id))

    def remove_balance(self, user_id: int, amount: float) -> None:
        """
        Deduct a specified amount from the user's account balance.

        Parameters:
        user_id (int): The user ID.
        amount (float): The amount to deduct.

        Raises:
        AccountFundsError: If the resulting balance is negative.
        """
        new_balance = self.get_balance(user_id) - amount
        if new_balance < 0:
            raise AccountFundsError("Insufficient funds in the account.")
        query = f"UPDATE {self.schema}.accounts SET balance = %s WHERE user_id = %s"
        self._execute_query(query, (new_balance, user_id))

    def funds_transfer(self, user_id_from: int, user_id_to: int, amount: float) -> None:
        """
        Transfer funds between two accounts.

        Parameters:
        user_id_from (int): The ID of the sender.
        user_id_to (int): The ID of the recipient.
        amount (float): The amount to transfer.
        """
        self.remove_balance(user_id_from, amount)
        self.add_balance(user_id_to, amount)

    def user_exists(self, user_id: int) -> bool:
        """
        Check if a user with the specified ID exists.

        Parameters:
        user_id (int): The user ID to check.

        Returns:
        bool: True if the user exists, False otherwise.
        """
        query = (
            f"SELECT EXISTS(SELECT 1 FROM {self.schema}.accounts WHERE user_id = %s)"
        )
        result = self._execute_query(query, (user_id,))
        return result[0][0]

    def update_balance(self, user_id: int, new_balance: float) -> None:
        """
        Update the user's account balance to a new value.

        Parameters:
        user_id (int): The user ID.
        new_balance (float): The new account balance.
        """
        query = f"UPDATE {self.schema}.accounts SET balance = %s WHERE user_id = %s"
        self._execute_query(query, (new_balance, user_id))

    def get_all_users(self) -> list[int]:
        """
        Retrieve a list of all user IDs.

        Returns:
        list[int]: A list of user IDs.
        """
        query = f"SELECT user_id FROM {self.schema}.accounts"
        result = self._execute_query(query)
        return [user[0] for user in result]

    def add_multiple_users(self, users_list: list[dict]) -> None:
        """
        Add multiple users from a list of dictionaries.

        Parameters:
        users_list (list[dict]): A list of dictionaries containing user_id and balance.
        """
        query = f"INSERT INTO {self.schema}.accounts (user_id, balance) VALUES (%s, %s)"
        values = [(user["user_id"], user["balance"]) for user in users_list]
        with self._conn.cursor() as cursor:
            cursor.executemany(query, values)
        self._conn.commit()

    def reset_balance(self, user_id: int) -> None:
        """
        Reset the user's account balance to 0.

        Parameters:
        user_id (int): The user ID.
        """
        query = f"UPDATE {self.schema}.accounts SET balance = 0 WHERE user_id = %s"
        self._execute_query(query, (user_id,))

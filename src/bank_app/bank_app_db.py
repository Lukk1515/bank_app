import psycopg2


class BankAccount:

    def __init__(self, schema="bank_app"):
        # Initializes the BankAccount class, creating a connection to the database
        self._conn = self._connect_to_db()
        self.schema = schema

    def _connect_to_db(self):
        # Establishes a connection to the PostgreSQL database
        # Tworzymy połączenie z bazą danych
        conn = psycopg2.connect(
            dbname="postgres",  # nazwa bazy danych
            user="postgres",  # nazwa użytkownika
            password="lucas",  # hasło do bazy danych
            host="localhost",  # host, jeśli lokalny to 'localhost'
            port="5432",  # port PostgreSQL, domyślnie 5432
        )
        return conn

    def get_balance(self, record_id):
        # Retrieves the account balance for a specified user_id
        with self._conn.cursor() as cursor:
            query = f"SELECT balance FROM {self.schema}.accounts WHERE user_id = %s"
            cursor.execute(query, (record_id,))
            result = cursor.fetchone()
            return result

    def add_user(self, user_id, balance):
        # Adds a new user with the specified user_id and balance
        try:
            with self._conn.cursor() as cursor:
                query = f"""INSERT INTO {self.schema}.accounts (user_id, balance) VALUES (%s, %s)"""
                cursor.execute(query, (user_id, balance))
                self._conn.commit()
                print(f"Succesfully added user with id: {user_id}")

        except Exception as e:
            print(f"Unable to add user: {e}")
            self._conn.rollback()

    def remove_user(self, user_id):
        # Removes the user with the specified user_id
        try:
            with self._conn.cursor() as cursor:
                query = f"DELETE FROM {self.schema}.accounts WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                self._conn.commit()
                print(f"Deleted user {user_id}")
        except Exception as e:
            print(f"Unable to delete user: {e}")

    def add_balance(self, user_id, amount):
        # Adds a specified amount to the user’s account balance
        try:
            with self._conn.cursor() as cursor:
                balance = list(self.get_balance(user_id))
                balance[0] += amount
                query = (
                    f"UPDATE {self.schema}.accounts SET balance = %s WHERE user_id = %s"
                )
                cursor.execute(query, (balance[0], user_id))
                self._conn.commit()
                print(f"Succesfully to add amount {amount} to account {user_id}")

        except Exception as e:
            print(f"Failed to add amount {amount} to account {user_id}.")
            self._conn.rollback()

    def remove_balance(self, user_id, amount):
        # Deducts a specified amount from the user’s account balance
        try:
            with self._conn.cursor() as cursor:
                balance = list(self.get_balance(user_id))
                if balance[0] < amount:
                    raise ValueError("amount is greater than account balance.")
                balance[0] -= amount
                query = (
                    f"UPDATE {self.schema}.accounts SET balance = %s WHERE user_id = %s"
                )
                cursor.execute(query, (balance[0], user_id))
                self._conn.commit()
                print(f"Sucesfully removed {amount} form account")
                return True
        except Exception as e:
            print(f"Failed to remove amount {amount} to account {user_id}.")
            self._conn.rollback()
            return False

    def founds_transfer(self, user_id_from, user_id_to, amount):
        # Transfers funds between two accounts
        result = self.remove_balance(user_id=user_id_from, amount=amount)
        if result is True:
            self.add_balance(user_id=user_id_to, amount=amount)
            print(f"Succesfully transfered founds from {user_id_from} to {user_id_to}")
        else:
            print("Failed to transfer founds.")

    def card_payment(self, user_id, amount):
        # Makes a card payment by deducting the specified amount from the balance
        result = self.remove_balance(user_id, amount)
        if result is True:
            print("Payment accepted")
        else:
            print("Payment declined")

    # ---------------------------

    # def user_exists(self, user_id):
    #     # Checks if a user with the specified user_id exists in the system
    #     try:
    #         with self._conn.cursor() as cursor:
    #             query = f"SELECT EXISTS(SELECT 1 FROM {self.schema}.accounts WHERE user_id = %s)"
    #             cursor.execute(query, (user_id,))
    #             result = cursor.fetchone()
    #             if result[0] is True:
    #                 print(f"User {user_id} exists in the system")
    #             else:
    #                 print(f"User {user_id} doesn't exists in the system")

    #     except Exception as e:
    #         print(f"An error occurred while checking if user {user_id} exists: {e}")
    # ---
    def user_exists(self, user_id):
        # Checks if a user with the specified user_id exists in the system
        try:
            with self._conn.cursor() as cursor:
                query = f"SELECT EXISTS(SELECT 1 FROM {self.schema}.accounts WHERE user_id = %s)"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result[0]

        except Exception as e:
            print(f"An error occurred while checking if user {user_id} exists: {e}")

    # ---
    def update_balance(self, user_id, new_balance):
        try:
            with self._conn.cursor() as cursor:
                query = (
                    f"UPDATE {self.schema}.accounts SET balance = %s WHERE user_id = %s"
                )
                cursor.execute(
                    query,
                    (
                        new_balance,
                        user_id,
                    ),
                )
                self._conn.commit()
                print(
                    f"User ID {user_id} balance successfully updated to {new_balance}."
                )

        except Exception as e:
            print(f"An error occurred while updating balance for user {user_id}.")
            self._conn.rollback()

    # metoda do pobierania listy samych użytkowników
    def get_all_users(self):
        # Retrieves a list of all user_ids in the system
        with self._conn.cursor() as cursor:
            query = f"SELECT user_id FROM {self.schema}.accounts"
            cursor.execute(query)
            result = cursor.fetchall()
            user_ids = [user[0] for user in result]
            print(f"User ids: {user_ids}")
            return user_ids

    # metoda do pobierania listy słowników zawierającej dane user_id i balance
    # def get_all_users(self):
    # Retrieves a list of dictionaries containing user_id and balance for each user in the system.
    #     with self._conn.cursor() as cursor:
    #         query = f"SELECT user_id, balance FROM {self.schema}.accounts"
    #         cursor.execute(query)
    #         result = cursor.fetchall()
    #         users = []
    #         for user in result:
    #             user_dict = {"user_id": user[0], "balance": float(user[1])}
    #             users.append(user_dict)
    #         print(f"User dicts: {users}")
    #         return users

    def add_multiple_users(self, users_list):
        # Adds multiple users at once from a list of dictionaries
        try:
            with self._conn.cursor() as cursor:
                query = f"INSERT INTO {self.schema}.accounts (user_id, balance) VALUES (%s, %s)"
                values = []
                for user in users_list:
                    user_id = user["user_id"]
                    balance = user["balance"]
                    values.append((user_id, balance))
                cursor.executemany(query, values)
                self._conn.commit()
                print("All users added succesfully")

        except Exception as e:
            print(f"An error occured: {e}")
            self._conn.rollback

    def reset_balance(self, user_id):
        # Resets the user’s account balance to 0
        try:
            with self._conn.cursor() as cursor:
                query = (
                    f"UPDATE {self.schema}.accounts SET balance = 0 WHERE user_id = %s"
                )
                cursor.execute(
                    query,
                    (user_id,),
                )
                self._conn.commit()
                print(f"Account user {user_id} has been reset")

        except Exception as e:
            print(f"An error occurred while reset account {user_id}")
            self._conn.rollback()


# a = BankAccount()

# a.add_user(user_id=1, balance=6000)
# a.add_balance(user_id=1, amount=3000)
# a.remove_balance(user_id=3, amount=4000)
# a.founds_transfer(user_id_from=1, user_id_to=4, amount=20000)
# a.card_payment(user_id=4, amount=1000)
# a.remove_user(user_id=1)
# a.user_exists(user_id=3)
# a.update_balance(user_id=1, new_balance=3000)
# a.get_all_users()
# a.add_multiple_users(users_list=[{'user_id': 7, 'balance': 1000}, {'user_id': 8, 'balance': 2000}])
# a.reset_balance(user_id=2)

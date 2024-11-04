import psycopg2


class BankAccount:

    def __init__(self):
        self._conn = self._connect_to_db()

    def _connect_to_db(self):
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
        with self._conn.cursor() as cursor:
            query = "SELECT balance FROM bank_app.accounts WHERE user_id = %s"
            cursor.execute(query, (record_id,))
            result = cursor.fetchone()
            return result

    def add_user(self, user_id, balance):
        try:
            with self._conn.cursor() as cursor:
                query = """INSERT INTO bank_app.accounts (user_id, balance) VALUES (%s, %s)"""
                cursor.execute(query, (user_id, balance))
                self._conn.commit()
                print(f"Succesfully added user with id: {user_id}")

        except Exception as e:
            print(f"Unable to add user: {e}")
            self._conn.rollback()

    def remove_user(self, user_id):
        try:
            with self._conn.cursor() as cursor:
                query = "DELETE FROM bank_app.accounts WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                self._conn.commit()
                print(f"Deleted user {user_id}")
        except Exception as e:
            print(f"Unable to delete user: {e}")

    def add_balance(self, user_id, amount):
        try:
            with self._conn.cursor() as cursor:
                balance = list(self.get_balance(user_id))
                balance[0] += amount
                query = "UPDATE bank_app.accounts SET balance = %s WHERE user_id = %s"
                cursor.execute(query, (balance[0], user_id))
                self._conn.commit()
                print(f"Succesfully to add amount {amount} to account {user_id}")

        except Exception as e:
            print(f"Failed to add amount {amount} to account {user_id}.")
            self._conn.rollback()

    def remove_balance(self, user_id, amount):
        try:
            with self._conn.cursor() as cursor:
                balance = list(self.get_balance(user_id))
                if balance[0] < amount:
                    raise ValueError("amount is greater than account balance.")
                balance[0] -= amount
                query = "UPDATE bank_app.accounts SET balance = %s WHERE user_id = %s"
                cursor.execute(query, (balance[0], user_id))
                self._conn.commit()
                print(f"Sucesfully removed {amount} form account")
                return True
        except Exception as e:
            print(f"Failed to remove amount {amount} to account {user_id}.")
            self._conn.rollback()
            return False

    def founds_transfer(self, user_id_from, user_id_to, amount):
        result = self.remove_balance(user_id=user_id_from, amount=amount)
        if result is True:
            self.add_balance(user_id=user_id_to, amount=amount)
            print(f"Succesfully transfered founds from {user_id_from} to {user_id_to}")
        else:
            print("Failed to transfer founds.")

    def card_payment(self, user_id, amount):
        result = self.remove_balance(user_id, amount)
        if result is True:
            print("Payment accepted")
        else:
            print("Payment declined")


a = BankAccount()

# a.add_user(user_id=4, balance=8000)
# a.add_balance(user_id=3, amount=3000)
# a.remove_balance(user_id=3, amount=4000)
# a.founds_transfer(user_id_from=1, user_id_to=4, amount=20000)
# a.card_payment(user_id=4, amount=1000)
a.remove_user(user_id=1)
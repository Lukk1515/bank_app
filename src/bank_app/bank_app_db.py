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


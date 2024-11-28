from bank_app_db import BankAccount
import pytest

# INSERT INTO bank_app_integration_tests.accounts (balance) VALUES (3000), (4000), (1000), (2000)


@pytest.fixture
def bank_account_insert_data():
    ba = BankAccount(schema="bank_app_integration_tests")
    conn = ba._conn
    cursor = conn.cursor()
    try:
        # Wstaw dane testowe
        cursor.execute(
            """
            INSERT INTO bank_app_integration_tests.accounts(
            user_id, balance)
            VALUES (1, 1000), (2, 2000), (3, 1300), (4, 3000);
            """
        )
        conn.commit()

        # Przekaż kontrolę do testów
        yield cursor

    finally:
        # Usuń dane testowe
        cursor.execute("DELETE FROM bank_app_integration_tests.accounts;")
        conn.commit()
        cursor.close()
        conn.close()


@pytest.fixture
def bank_account():
    yield BankAccount(schema="bank_app_integration_tests")


def test_get_balance(bank_account, bank_account_insert_data):
    result = bank_account.get_balance(record_id=2)
    assert result[0] == 2000


def test_get_all_users(bank_account, bank_account_insert_data):
    result = bank_account.get_all_users()
    assert result == [1, 2, 3, 4]


def test_add_user(bank_account, bank_account_insert_data):
    bank_account.add_user(user_id=5, balance=5000)
    bank_account_insert_data.execute("SELECT user_id, balance FROM bank_app_integration_tests.accounts WHERE user_id = 5;")    
    query_result=bank_account_insert_data.fetchone()
    assert query_result == (5, 5000)


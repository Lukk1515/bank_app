import pytest
from bank_app.bank_app_db import BankAccount

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
    result = bank_account.get_all_users()
    result2 = bank_account.get_balance(record_id=5)[0]
    assert result == [1, 2, 3, 4, 5]
    assert result2 == 5000


def test_remove_user(bank_account, bank_account_insert_data):
    bank_account.remove_user(user_id=1)
    result = bank_account.get_all_users()
    assert result == [2, 3, 4]


def test_user_exists(bank_account, bank_account_insert_data):
    result = bank_account.user_exists(user_id=2)
    assert result is True

    result = bank_account.user_exists(user_id=15)
    assert result is False


def test_add_balance(bank_account, bank_account_insert_data):
    bank_account.add_balance(user_id=1, amount=1000)
    result = bank_account.get_balance(record_id=1)
    assert result[0] == 2000


def test_remove_balance(bank_account, bank_account_insert_data):
    bank_account.remove_balance(user_id=2, amount=500)
    result = bank_account.get_balance(record_id=2)
    assert result[0] == 1500


def test_founds_transfer(bank_account, bank_account_insert_data):
    bank_account.founds_transfer(user_id_from=1, user_id_to=2, amount=500)
    result = bank_account.get_balance(record_id=1)[0]
    result2 = bank_account.get_balance(record_id=2)[0]
    assert result == 500 and result2 == 2500


def test_card_payment(bank_account, bank_account_insert_data):
    bank_account.card_payment(user_id=3, amount=500)
    result = bank_account.get_balance(record_id=3)[0]
    assert result == 800


def test_update_balance(bank_account, bank_account_insert_data):
    bank_account.update_balance(user_id=1, new_balance=4000)
    result = bank_account.get_balance(record_id=1)[0]
    assert result == 4000


def test_add_multiple_users(bank_account, bank_account_insert_data):
    users = [{"user_id": 5, "balance": 5000}, {"user_id": 6, "balance": 6000}]
    bank_account.add_multiple_users(users)
    result = bank_account.get_all_users()
    assert 5 in result
    assert 6 in result


def test_reset_balance(bank_account, bank_account_insert_data):
    bank_account.reset_balance(user_id=1)
    result = bank_account.get_balance(record_id=1)[0]
    assert result == 0

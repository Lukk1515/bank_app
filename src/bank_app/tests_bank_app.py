from bank_app import BankAccount
import pytest


@pytest.fixture
def first_account():
    ba = BankAccount(1000, "12345678", "John Doe")
    yield ba


@pytest.fixture
def second_account():
    ba = BankAccount(500, "87654321", "Johny Smith")
    yield ba


def test_get_balance(first_account):
    x = first_account.get_balance()
    assert x == 1000


def test_add_balance(first_account):
    first_account.add_balance(amount=500)
    assert first_account.get_balance() == 1500


def test_card_payment(first_account):
    first_account.card_payment(price=300)
    assert first_account.get_balance() == 700


def test_card_payment_transaction_rejected(first_account):
    with pytest.raises(ValueError, match="Transaction rejected. No funds in account."):
        first_account.card_payment(price=1500)


def test_transfer(first_account, second_account):
    first_account.transfer(amount=100, other_account=second_account)
    assert first_account.get_balance() == 900
    assert second_account.get_balance() == 600


def test_get_transaction_history(first_account, second_account):
    first_account.transfer(amount=100, other_account=second_account)
    history = first_account.get_transaction_history()
    expected_transaction = "Transferred 100 to account 87654321"
    assert expected_transaction in history

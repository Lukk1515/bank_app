import pytest
import uuid
import os
from decimal import Decimal
from bank_app.bank_app_db import BankAccount
from bank_app.models import Base, UserModel, BankAccountModel, TransactionModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


USER = os.getenv("USER")
DB_NAME = os.getenv("DBNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")


@pytest.fixture
def bank_account():
    yield BankAccount()


@pytest.fixture(scope="function")
def setup_test_data():
    # Tworzenie bazy w pamięci (SQLite, zamień na PostgreSQL jeśli używasz go w testach)
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Tworzenie użytkownika
    user_id = uuid.uuid4()
    user_id2 = uuid.uuid4()
    user = UserModel(
        user_id=user_id,
        name="John",
        surname="Smith",
        phone_number="555123456",
        email="john.smith@example.com",
        city="New York",
        postal_code="10001",
        street="Broadway",
        street_number=123,
        acommodation_number=45,
    )
    user2 = UserModel(
        user_id=user_id2,
        name="Rob",
        surname="Robin",
        phone_number="6667778867",
        email="kategrere.wirewglliams@example.com",
        city="Los Angeles",
        postal_code="12010",
        street="Main Street",
        street_number=156,
        acommodation_number=30,
    )
    session.add_all([user, user2])
    session.commit()

    # Tworzenie kont bankowych
    account1 = BankAccountModel(
        user_id=user_id, balance=1200.00, account_type="checking", account_number=1
    )
    account2 = BankAccountModel(
        user_id=user_id, balance=3000.00, account_type="savings", account_number=2
    )

    account3 = BankAccountModel(
        user_id=user_id2, balance=2000.00, account_type="savings", account_number=3
    )

    session.add_all([account1, account2, account3])
    session.commit()

    # Tworzenie przykładowej transakcji
    transaction = TransactionModel(
        account_number_from=account1.account_number,
        account_number_to=account2.account_number,
        amount=250.00,
        status="completed",
        type="transfer",
    )
    session.add(transaction)
    session.commit()

    yield user_id, user_id2

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)


# v
def test_get_balance(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    balance = bank_account.get_balance(user_id=user_id, account_number=1)
    assert balance == Decimal("1200")


# v
def test_add_user(bank_account, setup_test_data):
    user_id = uuid.uuid4()
    user = UserModel(
        user_id=user_id,
        name="Kate",
        surname="Williams",
        phone_number="666777888",
        email="kate.williams@example.com",
        city="Los Angeles",
        postal_code="12010",
        street="Main Street",
        street_number=156,
        acommodation_number=30,
    )
    added_user_id = bank_account.add_user(user)
    assert added_user_id == user_id
    users = bank_account.get_all_users()
    assert user_id in users


# p.d. Obsłuż usuwanie użytkownika o określonym user_id z bazy danych. Problem polega na tym że użytkownik jest powiązany z innymi tabelami takimi jak konta bankowe a konta bankowe są powiązane z tranzakcjami. Wszystko to powoduje złożony problem ponieważ nie możemy usunąc użytkownika gdy jest powiązany z innymi tabelami


# v
def test_remove_user(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    assert bank_account.user_exists(user_id) is True
    bank_account.remove_user(user_id)
    assert bank_account.user_exists(user_id) is False


# v
def test_add_balance(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    actually_balance = bank_account.get_balance(user_id, 2)
    assert actually_balance == Decimal("3000.00")
    bank_account.add_balance(user_id, Decimal("300"), 2)
    new_user_balance = bank_account.get_balance(user_id, 2)
    assert new_user_balance == Decimal("3300.00")


# v
def test_remove_balance(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    bank_account.remove_balance(user_id, 100, 2)
    new_user_balance = bank_account.get_balance(user_id, 2)
    assert new_user_balance == Decimal("2900.00")


# v
# dodać parametr account_number
def test_founds_transfer(bank_account, setup_test_data):
    user_id_from, user_id_to = setup_test_data
    bank_account.funds_transfer(user_id_from, user_id_to, Decimal("200"), 1, 3)
    assert bank_account.get_balance(user_id_to, 3) == Decimal("2200.00")
    assert bank_account.get_balance(user_id_from, 1) == Decimal("1000.00")


# v
def test_user_exists(bank_account, setup_test_data):
    existing_useer_id, _ = setup_test_data
    assert bank_account.user_exists(existing_useer_id) is True
    non_existing_user_id = uuid.uuid4()
    assert bank_account.user_exists(non_existing_user_id) is False


# v
def test_update_balance(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    initial_balance = bank_account.get_balance(user_id, 2)
    assert initial_balance == Decimal("3000.00")
    bank_account.update_balance(user_id, 2, Decimal("3500.00"))
    update_balance = bank_account.get_balance(user_id, 2)
    assert update_balance == Decimal("3500.00")


# v
def test_get_all_users(bank_account, setup_test_data):
    user_id_1, user_id_2 = setup_test_data
    user_ids = bank_account.get_all_users()
    assert isinstance(user_ids, list)
    assert user_id_1 in user_ids
    assert user_id_2 in user_ids
    assert len(user_ids) >= 2


def test_add_multiple_users(bank_account, setup_test_data):
    users_list = [
        {
            "name": "John",
            "surname": "Doe",
            "phone_number": "555123456",
            "email": "john.doe@example.com",
            "city": "New York",
            "postal_code": "10001",
            "street": "Broadway",
            "street_number": 101,
            "acommodation_number": 22,
        },
        {
            "name": "Alice",
            "surname": "Smith",
            "phone_number": "555987654",
            "email": "alice.smith@example.com",
            "city": "Chicago",
            "postal_code": "60610",
            "street": "Lake Shore Drive",
            "street_number": 300,
            "acommodation_number": 15,
        },
        {
            "name": "David",
            "surname": "Johnson",
            "phone_number": "555678901",
            "email": "david.johnson@example.com",
            "city": "San Francisco",
            "postal_code": "94105",
            "street": "Market Street",
            "street_number": 50,
            "acommodation_number": 7,
        },
    ]

    bank_account.add_multiple_users(users_list)

    with bank_account._session_local() as session:
        users = session.query(UserModel.email).all()
        user_emails = [user_id[0] for user_id in users]

    assert "john.doe@example.com" in user_emails
    assert "alice.smith@example.com" in user_emails
    assert "david.johnson@example.com" in user_emails


# v
def test_reset_balance(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    initial_balance = bank_account.get_balance(user_id, 1)
    assert initial_balance == Decimal("1200.00")
    bank_account.reset_balance(user_id, 1)
    new_balance = bank_account.get_balance(user_id, 1)
    assert new_balance == Decimal("0.00")


# create_bank_account
def test_create_bank_account(bank_account, setup_test_data):
    user_id, _ = setup_test_data
    account = BankAccountModel(account_number=55, user_id=user_id, account_type="xyz")
    bank_account.create_bank_account(account)

    with bank_account._session_local() as session:
        account_users = session.query(BankAccountModel.user_id).all()
        user_ids = [user_id[0] for user_id in account_users]

    assert user_id in user_ids


def test_create_transaction(bank_account, setup_test_data):
    user_id_from, user_id_to = setup_test_data
    from_account_number = 1
    to_account_number = 3
    amount = Decimal("150.00")

    balance_from_before = bank_account.get_balance(user_id_from, from_account_number)
    balance_to_before = bank_account.get_balance(user_id_to, to_account_number)

    transaction_id = bank_account.create_transaction(
        account_number_from=from_account_number,
        account_number_to=to_account_number,
        amount=amount,
        status="completed",
        type="checking",
    )
    assert transaction_id is not None

    balance_from_after = bank_account.get_balance(user_id_from, from_account_number)
    balance_to_after = bank_account.get_balance(user_id_to, to_account_number)

    assert balance_from_after == balance_from_before - amount
    assert balance_to_after == balance_to_before + amount

    with bank_account._session_local() as session:
        transaction = (
            session.query(TransactionModel)
            .filter_by(transaction_id=transaction_id)
            .first()
        )

        assert transaction is not None
        assert transaction.account_number_from == 1
        assert transaction.account_number_to == 3
        assert transaction.amount == amount
        assert transaction.status == "completed"
        assert transaction.type == "checking"


def test_get_all_balance(bank_account, setup_test_data):
    user_id_1, user_id_2 = setup_test_data
    user_ids = bank_account.get_all_balance()
    assert isinstance(user_ids, dict)

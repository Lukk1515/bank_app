import pytest
from bank_app import BankAccount
from decimal import Decimal
from unittest.mock import patch, MagicMock
import uuid


@pytest.fixture
def mock_session():
    with patch("bank_app.bank_app_db.sessionmaker") as mock_sessionmaker:
        mock_session = MagicMock()
        mock_sessionmaker.return_value = mock_session
        yield mock_session


@pytest.fixture
def bank():
    with patch("bank_app.bank_app_db.Base.metadata.create_all"):
        return BankAccount()


def test_get_balance_success(bank):
    mock_account = MagicMock()
    mock_account.balance = Decimal("100.00")

    with patch.object(bank, "_session_local") as mock_session_local:
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_account
        )
        mock_session_local.return_value.__enter__.return_value = mock_session

        user_id = uuid.uuid4()
        balance = bank.get_balance(user_id)

        assert balance == Decimal("100.00")


def test_get_balance_account_not_found(bank):
    with patch.object(bank, "_session_local") as mock_session_local:
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session_local.return_value.__enter__.return_value = mock_session

        with pytest.raises(ValueError, match="Account for user .* not found."):
            bank.get_balance(uuid.uuid4())


def test_funds_transfer_success(bank):
    sender = MagicMock(balance=Decimal("100.00"), user_id="sender")
    receiver = MagicMock(balance=Decimal("100.00"), user_id="receiver")

    with patch.object(bank, "_session_local") as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_session

        def filter_by_side_effect(**kwargs):
            return MagicMock(
                first=MagicMock(
                    return_value=(
                        sender if kwargs.get("user_id") == "sender" else receiver
                    )
                )
            )

        mock_session.query.return_value.filter_by.side_effect = filter_by_side_effect

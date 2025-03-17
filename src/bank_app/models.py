import uuid
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DECIMAL,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "bank_app"}
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    street = Column(String, nullable=False)
    street_number = Column(Integer, nullable=False)
    acommodation_number = Column(Integer, nullable=False)


class BankAccountModel(Base):
    __tablename__ = "bank_accounts"
    __table_args__ = {"schema": "bank_app"}

    account_number = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("bank_app.users.user_id"), nullable=False
    )
    balance = Column(DECIMAL(15, 2), default=0.00)
    account_type = Column(String(250))
    created_at = Column(TIMESTAMP, default=func.now())

    # Relacja do modelu użytkownika (opcjonalna, jeśli chcesz uzyskać powiązane obiekty)
    user = relationship("UserModel", backref="bank_accounts")


class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "bank_app"}

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number_from = Column(
        Integer, ForeignKey("bank_app.bank_accounts.account_number"), nullable=False
    )
    account_number_to = Column(
        Integer, ForeignKey("bank_app.bank_accounts.account_number"), nullable=False
    )
    amount = Column(DECIMAL(15, 2), default=0.00)
    date = Column(TIMESTAMP, default=func.now())
    status = Column(String(250))
    type = Column(
        String, nullable=False
    )  # Zmienione na String zamiast ENUM, ponieważ wymaga dodatkowej definicji

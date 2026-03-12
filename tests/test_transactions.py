import pytest
from decimal import Decimal
from services.transactions_service import deposit, withdraw, transfer, TransactionError
from models.model import Account
from database import db


def test_cannot_withdraw_more_than_balance(app, accounts):
    a1_id, _ = accounts
    with app.app_context():
        a1 = db.session.get(Account, a1_id)

        with pytest.raises(TransactionError):
            withdraw(a1, Decimal("1000.00"))

def test_cannot_transfer_more_than_balance(app, accounts):
    a1_id, a2_id = accounts
    with app.app_context():
        a1 = db.session.get(Account, a1_id)
        a2 = db.session.get(Account, a2_id)
        with pytest.raises(TransactionError):
            transfer(a1, a2, Decimal("999.00"))

def test_cannot_deposit_negative_amount(app, accounts):
    a1_id, _ = accounts
    with app.app_context():
        a1 = db.session.get(Account, a1_id)

        with pytest.raises(TransactionError):
            deposit(a1, Decimal("-10.00"))

def test_cannot_withdraw_negative_amount(app, accounts):
    a1_id, _ = accounts
    with app.app_context():
        a1 = db.session.get(Account, a1_id)

        with pytest.raises(TransactionError):
            withdraw(a1, Decimal("-5.00"))

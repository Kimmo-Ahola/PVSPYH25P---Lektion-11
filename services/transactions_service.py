from decimal import Decimal
from database import db
from models.model import Account, Transaction
from datetime import datetime

class TransactionError(Exception):
    pass

def _validate_amount(amount: Decimal):
    if amount is None:
        raise TransactionError("Belopp saknas.")
    if amount <= Decimal("0"):
        raise TransactionError("Belopp måste vara större än 0.")

def deposit(account: Account, amount: Decimal, operation="Deposit"):
    _validate_amount(amount)

    new_balance = (account.Balance or Decimal("0")) + amount

    t = Transaction(
        Type="Credit",
        Operation=operation,
        Date=datetime.now(),
        Amount=amount,
        NewBalance=new_balance,
        AccountId=account.Id,
    )

    account.Balance = new_balance
    db.session.add(t)
    db.session.commit()
    return t

def withdraw(account: Account, amount: Decimal, operation="Withdraw"):
    _validate_amount(amount)

    balance = account.Balance or Decimal("0")
    if amount > balance:
        raise TransactionError("Otillräckligt saldo för uttag.")

    new_balance = balance - amount

    t = Transaction(
        Type="Debit",
        Operation=operation,
        Date=datetime.now(),
        Amount=amount,
        NewBalance=new_balance,
        AccountId=account.Id,
    )

    account.Balance = new_balance
    db.session.add(t)
    db.session.commit()
    return t

def transfer(from_account: Account, to_account: Account, amount: Decimal):
    _validate_amount(amount)

    if from_account.Id == to_account.Id:
        raise TransactionError("Du kan inte överföra till samma konto.")

    balance = from_account.Balance or Decimal("0")
    if amount > balance:
        raise TransactionError("Otillräckligt saldo för överföring.")

    from_new = balance - amount
    to_new = (to_account.Balance or Decimal("0")) + amount

    t_out = Transaction(
        Type="Debit",
        Operation=f"Transfer to {to_account.Id}",
        Date=datetime.now(),
        Amount=amount,
        NewBalance=from_new,
        AccountId=from_account.Id,
    )
    t_in = Transaction(
        Type="Credit",
        Operation=f"Transfer from {from_account.Id}",
        Date=datetime.now(),
        Amount=amount,
        NewBalance=to_new,
        AccountId=to_account.Id,
    )

    from_account.Balance = from_new
    to_account.Balance = to_new

    db.session.add_all([t_out, t_in])
    db.session.commit()
    return t_out, t_in

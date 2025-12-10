from sqlalchemy import MetaData, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Annotated
from flask_sqlalchemy import SQLAlchemy
import barnum
import random
from datetime import datetime
from datetime import timedelta

db = SQLAlchemy()


class Types:
    int_pk = Annotated[
        int, mapped_column(Integer, primary_key=True, autoincrement=True)
    ]


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Customer(db.Model):
    __tablename__ = "Customers"
    Id: Mapped[Types.int_pk]
    GivenName = mapped_column(db.String(50), unique=False, nullable=False)
    Surname = mapped_column(db.String(50), unique=False, nullable=False)
    Streetaddress = mapped_column(db.String(50), unique=False, nullable=False)
    City = mapped_column(db.String(50), unique=False, nullable=False)
    Zipcode = mapped_column(db.String(10), unique=False, nullable=False)
    Country = mapped_column(db.String(30), unique=False, nullable=False)
    CountryCode = mapped_column(db.String(2), unique=False, nullable=False)
    Birthday = mapped_column(db.DateTime, unique=False, nullable=False)
    NationalId = mapped_column(db.String(20), unique=False, nullable=False)
    TelephoneCountryCode = mapped_column(db.Integer, unique=False, nullable=False)
    Telephone = mapped_column(db.String(20), unique=False, nullable=False)
    EmailAddress = mapped_column(db.String(50), unique=False, nullable=False)

    Accounts = db.relationship("Account", backref="Customer", lazy=True)


class Account(db.Model):
    __tablename__ = "Accounts"
    Id: Mapped[Types.int_pk]
    AccountType = mapped_column(db.String(10), unique=False, nullable=False)
    Created = mapped_column(db.DateTime, unique=False, nullable=False)
    Balance = mapped_column(db.Integer, unique=False, nullable=False)
    Transactions = db.relationship("Transaction", backref="Account", lazy=True)
    CustomerId = mapped_column(
        db.Integer, db.ForeignKey("Customers.Id"), nullable=False
    )


class Transaction(db.Model):
    __tablename__ = "Transactions"
    Id: Mapped[Types.int_pk]
    Type = mapped_column(db.String(20), unique=False, nullable=False)
    Operation = mapped_column(db.String(50), unique=False, nullable=False)
    Date = mapped_column(db.DateTime, unique=False, nullable=False)
    Amount = mapped_column(db.Integer, unique=False, nullable=False)
    NewBalance = mapped_column(db.Integer, unique=False, nullable=False)
    AccountId = mapped_column(db.Integer, db.ForeignKey("Accounts.Id"), nullable=False)


def seedData(db):
    antal = Customer.query.count()
    countries = ["SV", "DK", "NO", "FI"]
    while antal < 5000:
        customer = Customer()

        customer.GivenName, customer.Surname = barnum.create_name()

        customer.Streetaddress = barnum.create_street()
        customer.Zipcode, customer.City, _ = barnum.create_city_state_zip()
        customer.Country = random.choice(countries)
        customer.CountryCode = random.choice(countries)
        customer.Birthday = barnum.create_birthday()
        n = barnum.create_cc_number()
        customer.NationalId = customer.Birthday.strftime("%Y%m%d-") + n[1][0][0:4]
        customer.TelephoneCountryCode = 55
        customer.Telephone = barnum.create_phone()
        customer.EmailAddress = barnum.create_email().lower()

        for x in range(random.randint(1, 4)):
            account = Account()

            c = random.randint(0, 100)
            if c < 33:
                account.AccountType = "Personal"
            elif c < 66:
                account.AccountType = "Checking"
            else:
                account.AccountType = "Savings"

            start = datetime.now() + timedelta(days=-random.randint(1000, 10000))
            account.Created = start
            account.Balance = 0

            for n in range(random.randint(0, 30)):
                belopp = random.randint(0, 30) * 100
                tran = Transaction()
                start = start + timedelta(days=-random.randint(10, 100))
                if start > datetime.now():
                    break
                tran.Date = start
                account.Transactions.append(tran)
                tran.Amount = belopp
                if account.Balance - belopp < 0:
                    tran.Type = "Debit"
                else:
                    if random.randint(0, 100) > 70:
                        tran.Type = "Debit"
                    else:
                        tran.Type = "Credit"

                r = random.randint(0, 100)
                if tran.Type == "Debit":
                    account.Balance = account.Balance + belopp
                    if r < 20:
                        tran.Operation = "Deposit cash"
                    elif r < 66:
                        tran.Operation = "Salary"
                    else:
                        tran.Operation = "Transfer"
                else:
                    account.Balance = account.Balance - belopp
                    if r < 40:
                        tran.Operation = "ATM withdrawal"
                    if r < 75:
                        tran.Operation = "Payment"
                    elif r < 85:
                        tran.Operation = "Bank withdrawal"
                    else:
                        tran.Operation = "Transfer"

                tran.NewBalance = account.Balance

            customer.Accounts.append(account)

        db.session.add(customer)

        antal = antal + 1
    db.session.commit()

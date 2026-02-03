from enum import StrEnum
from enum import Enum as PyEnum
import random
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, text
from typing import Annotated, Optional
from flask_security.core import RoleMixin, UserMixin

from datetime import datetime
from datetime import timedelta
from database import db
from faker import Faker
from datetime import datetime, timedelta


class Types:
    int_pk = Annotated[
        int, mapped_column(Integer, primary_key=True, autoincrement=True)
    ]


class UserRoles(StrEnum):
    CASHIER = "CASHIER"
    ADMIN = "ADMIN"


roles_employees = db.Table(
    "roles_employees",
    db.Column("employee_id", db.Integer, db.ForeignKey("employees.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    id: Mapped[Types.int_pk]
    name: Mapped[str] = mapped_column(String(20), default=UserRoles.CASHIER.value)
    description: Mapped[Optional[str]] = mapped_column(String(100))
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", secondary=roles_employees, back_populates="roles"
    )


class Employee(db.Model, UserMixin):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)

    password: Mapped[str] = mapped_column(String(2000))
    active: Mapped[bool] = mapped_column(default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship(
        "Role", secondary=roles_employees, back_populates="employees"
    )



class Customer(db.Model):
    __tablename__ = "customers"
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


class AccountType(PyEnum):
    PERSONAL = "PERSONAL"
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class Account(db.Model):
    __tablename__ = "accounts"
    Id: Mapped[Types.int_pk]
    AccountType = mapped_column(
        db.Enum(AccountType),
        default=AccountType.PERSONAL,
        server_default=text(f"'{AccountType.PERSONAL.value}'"),
        unique=False,
        nullable=False,
    )
    Created = mapped_column(db.DateTime, unique=False, nullable=False)
    Balance = mapped_column(db.Integer, unique=False, nullable=False)
    Transactions = db.relationship("Transaction", backref="Account", lazy=True)
    CustomerId = mapped_column(
        db.Integer, db.ForeignKey("customers.Id"), nullable=False
    )


class Transaction(db.Model):
    __tablename__ = "transactions"
    Id: Mapped[Types.int_pk]
    Type = mapped_column(db.String(20), unique=False, nullable=False)
    Operation = mapped_column(db.String(50), unique=False, nullable=False)
    Date = mapped_column(db.DateTime, unique=False, nullable=False)
    Amount = mapped_column(db.Integer, unique=False, nullable=False)
    NewBalance = mapped_column(db.Integer, unique=False, nullable=False)
    AccountId = mapped_column(db.Integer, db.ForeignKey("accounts.Id"), nullable=False)


def seed_employees(db, data_store):
    cashier = data_store.find_role(UserRoles.CASHIER.value)
    admin = data_store.find_role(UserRoles.ADMIN.value)

    if not admin:
        data_store.create_role(name=UserRoles.ADMIN.value, description="Admin handles employees") # remember to use .value when using the enum

    if not cashier:
        data_store.create_role(name=UserRoles.CASHIER.value, description="Cashier handles accounts and transactions")

    db.session.commit()

    employees = db.session.query(Employee).count()


    from flask_security.utils import hash_password # Use hash_password to keep passwords from being in plain text
    if employees == 0:
        data_store.create_user(email="admin@test.se",
                               username="Admin",
                               password=hash_password("Hejsan123!"), # ideally we should load passwords from .env, but this is not needed for this exercise
                               roles=[data_store.find_role(UserRoles.ADMIN.value)])
        
        data_store.create_user(email="cashier@test.se",
                               username="Cashier",
                               password=hash_password("Hejsan123!"),
                               roles=[data_store.find_role(UserRoles.CASHIER.value)])

    db.session.commit()

def seedData(db):
    locales = {"SV": "sv_SE", "DK": "da_DK", "NO": "no_NO", "FI": "fi_FI"}
    antal = db.session.query(Customer).count()
    countries = ["SV", "DK", "NO", "FI"]

    while antal < 5:
        customer = Customer()
        country = random.choice(countries)
        locale = locales[country]
        fake = Faker(locale)

        # Generate names
        customer.GivenName = fake.first_name()
        customer.Surname = fake.last_name()

        # Address
        customer.Streetaddress = fake.street_address()
        customer.Zipcode = fake.postcode()
        customer.City = fake.city()
        customer.Country = random.choice(countries)
        customer.CountryCode = random.choice(countries)

        # Birthday & NationalId
        customer.Birthday = fake.date_of_birth(minimum_age=18, maximum_age=90)
        cc_number = fake.random_number(digits=4, fix_len=True)
        customer.NationalId = customer.Birthday.strftime("%Y%m%d-") + str(cc_number)

        # Phone & Email
        customer.TelephoneCountryCode = 55
        customer.Telephone = fake.phone_number()
        customer.EmailAddress = fake.email().lower()

        # Accounts
        for _ in range(random.randint(1, 4)):
            account = Account()

            c = random.randint(0, 100)
            if c < 33:
                account.AccountType = AccountType.PERSONAL
            elif c < 66:
                account.AccountType = AccountType.CHECKING
            else:
                account.AccountType = AccountType.SAVINGS

            start = datetime.now() + timedelta(days=-random.randint(1000, 10000))
            account.Created = start
            account.Balance = 0

            # Transactions
            for _ in range(random.randint(0, 30)):
                tran = Transaction()
                start = start + timedelta(days=-random.randint(10, 100))
                if start > datetime.now():
                    break
                tran.Date = start

                belopp = random.randint(0, 30) * 100
                tran.Amount = belopp

                # Determine debit/credit
                if account.Balance - belopp < 0:
                    tran.Type = "Debit"
                else:
                    tran.Type = "Credit" if random.randint(0, 100) > 70 else "Debit"

                # Operations
                r = random.randint(0, 100)
                if tran.Type == "Debit":
                    account.Balance += belopp
                    if r < 20:
                        tran.Operation = "Deposit cash"
                    elif r < 66:
                        tran.Operation = "Salary"
                    else:
                        tran.Operation = "Transfer"
                else:
                    account.Balance -= belopp
                    if r < 40:
                        tran.Operation = "ATM withdrawal"
                    elif r < 75:
                        tran.Operation = "Payment"
                    elif r < 85:
                        tran.Operation = "Bank withdrawal"
                    else:
                        tran.Operation = "Transfer"

                tran.NewBalance = account.Balance
                account.Transactions.append(tran)

            customer.Accounts.append(account)

        db.session.add(customer)
        antal += 1

    db.session.commit()

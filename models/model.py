from enum import StrEnum
from enum import Enum as PyEnum
import random
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, text, Numeric
from typing import Annotated, Optional
from flask_security.core import RoleMixin, UserMixin
import uuid
from datetime import datetime
from datetime import timedelta
from database import db
from faker import Faker
from datetime import datetime, timedelta
from flask_security.utils import hash_password
from decimal import Decimal



class Types:
    int_pk = Annotated[
        int, mapped_column(Integer, primary_key=True, autoincrement=True)
    ]


class UserRoles(StrEnum):
    Cashier = "Cashier"
    Admin = "Admin"


roles_employees = db.Table(
    "roles_employees",
    db.Column("employee_id", db.Integer, db.ForeignKey("employees.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
)


class Role(db.Model, RoleMixin):
    __tablename__ = "roles"
    id: Mapped[Types.int_pk] # type: ignore
    name: Mapped[str] = mapped_column(String(20), default=UserRoles.Cashier.value) # type: ignore
    description: Mapped[Optional[str]] = mapped_column(String(100)) # type: ignore
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", secondary=roles_employees, back_populates="roles")




class Employee(db.Model, UserMixin):
    __tablename__ = "employees"

    id: Mapped[Types.int_pk] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(2000), nullable=False)
    active: Mapped[bool] = mapped_column(default=True)

    # Flask-Security kräver denna (unik och inte null)
    fs_uniquifier = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        default=lambda: uuid.uuid4().hex
    )

    roles = db.relationship("Role", secondary=roles_employees, back_populates="employees") # type: ignore






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
    Balance =mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
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
    Amount = mapped_column(Numeric(18, 2), nullable=False)
    NewBalance = mapped_column(Numeric(18, 2), nullable=False)
    AccountId = mapped_column(db.Integer, db.ForeignKey("accounts.Id"), nullable=False)





    

def seed_employees(db, data_store):
    # Roller
    if not data_store.find_role(UserRoles.Admin.value):
        data_store.create_role(
            name=UserRoles.Admin.value,
            description="Admin handles employees"
        )

    if not data_store.find_role(UserRoles.Cashier.value):
        data_store.create_role(
            name=UserRoles.Cashier.value,
            description="Cashier handles accounts and transactions"
        )

    db.session.commit()

    # Users (EXAKT enligt uppgiften)
    admin_email = "kimmo.ahola@systementor.se"
    cashier_email = "kimmo.ahola@webbramwerk.se"

    admin_user = data_store.find_user(email=admin_email)
    if not admin_user:
        data_store.create_user(
            email=admin_email,
            username="Admin",
            password=hash_password("Hejsan123!"),
            roles=[data_store.find_role(UserRoles.Admin.value)],
        )

    cashier_user = data_store.find_user(email=cashier_email)
    if not cashier_user:
        data_store.create_user(
            email=cashier_email,
            username="Cashier",
            password=hash_password("Hejsan123!"),
            roles=[data_store.find_role(UserRoles.Cashier.value)],
        )

    db.session.commit()



def seedData(db, target_customers=500):
    locales = {"SV": "sv_SE", "DK": "da_DK", "NO": "no_NO", "FI": "fi_FI"}
    countries = ["SV", "DK", "NO", "FI"]

    antal = db.session.query(Customer).count()
    batch_size = 50  # commit i klumpar

    while antal < target_customers:
        batch = []
        to_create = min(batch_size, target_customers - antal)

        for _ in range(to_create):
            customer = Customer()
            country = random.choice(countries)
            fake = Faker(locales[country])

            customer.GivenName = fake.first_name()
            customer.Surname = fake.last_name()

            customer.Streetaddress = fake.street_address()
            customer.Zipcode = fake.postcode()
            customer.City = fake.city()
            customer.Country = country
            customer.CountryCode = country

            customer.Birthday = fake.date_of_birth(minimum_age=18, maximum_age=90)
            cc_number = fake.random_number(digits=4, fix_len=True)
            customer.NationalId = customer.Birthday.strftime("%Y%m%d-") + str(cc_number)

            customer.TelephoneCountryCode = 46
            customer.Telephone = fake.phone_number()
            customer.EmailAddress = fake.email().lower()

            # Accounts (håll ner antalet för fart)
            for _ in range(random.randint(1, 2)):
                account = Account()
                account.AccountType = random.choice(list(AccountType))
                start = datetime.now() - timedelta(days=random.randint(1000, 10000))
                account.Created = start
                account.Balance = 0

                # Transactions (håll ner för fart)
                for _ in range(random.randint(0, 10)):
                    tran = Transaction()
                    start = start + timedelta(days=random.randint(1, 30))
                    tran.Date = start

                    belopp = random.randint(1, 30) * 100
                    is_deposit = random.randint(0, 100) < 50

                    if is_deposit:
                        tran.Type = "Credit"
                        tran.Operation = "Deposit"
                        account.Balance += belopp
                    else:
                        tran.Type = "Debit"
                        tran.Operation = "Payment"
                        # tillåt att det kan gå minus i seed eller skydda:
                        if account.Balance - belopp < 0:
                            # gör insättning istället om det saknas saldo
                            tran.Type = "Credit"
                            tran.Operation = "Deposit"
                            account.Balance += belopp
                        else:
                            account.Balance -= belopp

                    tran.Amount = belopp
                    tran.NewBalance = account.Balance
                    account.Transactions.append(tran)

                customer.Accounts.append(account)

            batch.append(customer)

        db.session.add_all(batch)
        db.session.commit()
        antal = db.session.query(Customer).count()


    
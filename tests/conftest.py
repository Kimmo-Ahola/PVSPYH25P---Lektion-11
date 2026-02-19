import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import Flask
from datetime import datetime
from decimal import Decimal

from database import db
from models.model import Customer, Account, AccountType


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def _create_customer():
    c = Customer(
        GivenName="Test",
        Surname="User",
        Streetaddress="Testgatan 1",
        City="Teststad",
        Zipcode="12345",
        Country="SV",
        CountryCode="SV",
        Birthday=datetime(1990, 1, 1),
        NationalId="19900101-1234",
        TelephoneCountryCode=46,
        Telephone="0700000000",
        EmailAddress="test@example.com",
    )
    db.session.add(c)
    db.session.commit()
    return c

@pytest.fixture()
def accounts(app):
    with app.app_context():
        c = Customer(
            GivenName="Test",
            Surname="User",
            Streetaddress="Testgatan 1",
            City="Teststad",
            Zipcode="12345",
            Country="SV",
            CountryCode="SV",
            Birthday=datetime(1990, 1, 1),
            NationalId="19900101-1234",
            TelephoneCountryCode=46,
            Telephone="0700000000",
            EmailAddress="test@example.com",
        )
        db.session.add(c)
        db.session.commit()

        a1 = Account(
            CustomerId=c.Id,
            AccountType=AccountType.PERSONAL,
            Created=datetime.now(),
            Balance=Decimal("100.00"),
        )
        a2 = Account(
            CustomerId=c.Id,
            AccountType=AccountType.CHECKING,
            Created=datetime.now(),
            Balance=Decimal("0.00"),
        )
        db.session.add_all([a1, a2])
        db.session.commit()

        return a1.Id, a2.Id
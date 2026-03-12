from flask import Blueprint, render_template, request, flash
from flask_security.decorators import auth_required, roles_required

from models.model import UserRoles

from models.model import Customer, Account, Transaction, UserRoles
from database import db

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_bp.route("/", methods=["GET"])
@auth_required()
@roles_required(UserRoles.Cashier.value)
def customer_profile():
    customer_id = request.args.get("customer_id", "").strip()

    if not customer_id:
        return render_template("cashier/customer.html", customer=None)

    if not customer_id.isdigit():
        flash("Ange ett giltigt kundnummer.", "danger")
        return render_template("cashier/customer.html", customer=None)

    customer = Customer.query.filter_by(Id=int(customer_id)).first()

    if not customer:
        flash("Ingen kund hittades med det kundnumret.", "warning")
        return render_template("cashier/customer.html", customer=None)

    accounts = Account.query.filter_by(CustomerId=customer.Id).all()
    total_balance = sum((a.Balance or 0) for a in accounts)

    return render_template(
        "cashier/customer.html",
        customer=customer,
        accounts=accounts,
        total_balance=total_balance,
    )


@customer_bp.route("/search", methods=["GET"])
@auth_required()
@roles_required(UserRoles.Cashier.value)
def search():
    name = request.args.get("name", "").strip()
    city = request.args.get("city", "").strip()
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by", "Id")
    sort_order = request.args.get("sort_order", "asc")

    allowed_columns = {
        "Id": Customer.Id,
        "NationalId": Customer.NationalId,
        "GivenName": Customer.GivenName,
        "Surname": Customer.Surname,
        "Streetaddress": Customer.Streetaddress,
        "City": Customer.City,
    }

    query = Customer.query

    if name:
        like = f"%{name}%"
        query = query.filter(
            db.or_(
                Customer.GivenName.ilike(like),
                Customer.Surname.ilike(like)
            )
        )

    if city:
        query = query.filter(Customer.City.ilike(f"%{city}%"))

    sort_column = allowed_columns.get(sort_by, Customer.Id)

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    pagination = query.paginate(page=page, per_page=20, error_out=False)

    return render_template(
        "cashier/search.html",
        customers=pagination.items,
        pagination=pagination,
        name=name,
        city=city,
        sort_by=sort_by,
        sort_order=sort_order,
    )


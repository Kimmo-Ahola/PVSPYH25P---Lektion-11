from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security.decorators import auth_required, roles_required
from decimal import Decimal, InvalidOperation
from models.model import UserRoles, Account, Transaction
from services.transactions_service import deposit, withdraw, transfer, TransactionError
from models.model import Customer, Account, Transaction, UserRoles
from database import db


account_bp = Blueprint("account", __name__,url_prefix="/account")


@account_bp.route("/<int:account_id>")
@auth_required()
@roles_required(UserRoles.Cashier.value)
def account(account_id):
    acc = Account.query.get_or_404(account_id)
    transactions = (
        Transaction.query
        .filter_by(AccountId=acc.Id)
        .order_by(Transaction.Date.desc(), Transaction.Id.desc())
        .all()
    )
    return render_template("cashier/account.html", account=acc, transactions=transactions)


def _parse_amount(s: str) -> Decimal:
    s = (s or "").strip().replace(",", ".")
    if not s:
        raise TransactionError("Du måste ange ett belopp.")

    try:
        amount = Decimal(s)
    except (InvalidOperation, ValueError):
        raise TransactionError("Ogiltigt belopp.")

    if amount <= 0:
        raise TransactionError("Beloppet måste vara större än 0.")

    return amount


@account_bp.route("/<int:account_id>/deposit", methods=["POST"])
@auth_required()
@roles_required(UserRoles.Cashier.value)
def deposit_route(account_id):
    acc = Account.query.get_or_404(account_id)

    try:
        amount = _parse_amount(request.form.get("amount"))
        deposit(acc, amount)
        flash("Insättning genomförd.", "success")
    except TransactionError as e:
        flash(str(e), "danger")

    return redirect(url_for("account.account", account_id=account_id))


@account_bp.route("/<int:account_id>/withdraw", methods=["POST"])
@auth_required()
@roles_required(UserRoles.Cashier.value)
def withdraw_route(account_id):
    acc = Account.query.get_or_404(account_id)

    try:
        amount = _parse_amount(request.form.get("amount"))
        withdraw(acc, amount)
        flash("Uttag genomfört.", "success")
    except TransactionError as e:
        flash(str(e), "danger")

    return redirect(url_for("account.account", account_id=account_id))


@account_bp.route("/<int:account_id>/transfer", methods=["POST"])
@auth_required()
@roles_required(UserRoles.Cashier.value)
def transfer_route(account_id):
    from_acc = Account.query.get_or_404(account_id)

    try:
        to_account_raw = (request.form.get("to_account_id") or "").strip()

        if not to_account_raw:
            raise TransactionError("Du måste ange mottagarkonto.")

        if not to_account_raw.isdigit():
            raise TransactionError("Mottagarkonto måste vara ett giltigt kontonummer.")

        to_id = int(to_account_raw)

        if to_id == account_id:
            raise TransactionError("Du kan inte överföra till samma konto.")

        to_acc = Account.query.get_or_404(to_id)

        amount = _parse_amount(request.form.get("amount"))
        transfer(from_acc, to_acc, amount)

        flash("Överföring genomförd.", "success")

    except TransactionError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Ogiltigt mottagarkonto.", "danger")

    return redirect(url_for("account.account", account_id=account_id))
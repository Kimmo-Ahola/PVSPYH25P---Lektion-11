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
    transactions = (Transaction.query
        .filter_by(AccountId=acc.Id)
        .order_by(Transaction.Date.desc(), Transaction.Id.desc())
        .all()
    )
    return render_template("cashier/account.html", account=acc, transactions=transactions)

def _parse_amount(s: str) -> Decimal:
    try:
        
        s = (s or "").strip().replace(",", ".")
        return Decimal(s)
    except (InvalidOperation, ValueError):
        raise TransactionError("Ogiltigt belopp.")

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
        to_id = int(request.form.get("to_account_id"))
        to_acc = Account.query.get_or_404(to_id)
        amount = _parse_amount(request.form.get("amount"))
        transfer(from_acc, to_acc, amount)
        flash("Överföring genomförd.", "success")
    except (ValueError, TypeError):
        flash("Ogiltigt mottagarkonto.", "danger")
    except TransactionError as e:
        flash(str(e), "danger")
    return redirect(url_for("account.account", account_id=account_id))
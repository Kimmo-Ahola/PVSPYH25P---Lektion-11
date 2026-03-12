from flask import Blueprint, render_template, request, flash
from flask_security.decorators import auth_required, roles_required, roles_accepted
from models.model import UserRoles

from models.model import Customer, Account, Transaction, UserRoles
from database import db


cashier_bp = Blueprint("cashier", __name__, url_prefix="/cashier")

@cashier_bp.route("/")
@auth_required()
@roles_required(UserRoles.Cashier.value)  
@roles_accepted( "Cashier")
def cashier():
    return render_template("cashier/cashier.html")

from flask import Blueprint, render_template
from flask_security.decorators import auth_required, roles_required

from models.model import UserRoles

cashier_bp = Blueprint("cashier", __name__, url_prefix="/cashier")

@cashier_bp.route("/")
@auth_required()
@roles_required(UserRoles.CASHIER.value)
def start():
    return render_template("cashier.html")
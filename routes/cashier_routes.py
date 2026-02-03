from flask import Blueprint, render_template
from flask_security.decorators import auth_required, roles_required

from models.model import UserRoles

cashier_bp = Blueprint("cashier", __name__, url_prefix="/cashier")

@cashier_bp.route("/")
@auth_required() # use @auth_required() or @login_required to enforce login status. Remember to put this decorator on all routes you wish to protect.
@roles_required(UserRoles.CASHIER.value) # adds role requirement to the route. We need to be logged in AND have the correlt role(s)
def start():
    return render_template("cashier.html")

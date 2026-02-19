from flask import Blueprint, render_template, request, flash
from flask_security.decorators import auth_required, roles_required

from models.model import UserRoles

from models.model import Customer, Account, Transaction, UserRoles
from database import db




bp = Blueprint("main", __name__)

@bp.route("/after-login")   
def after_login():
    ...

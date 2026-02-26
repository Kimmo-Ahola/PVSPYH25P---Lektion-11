import os
from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from dotenv import load_dotenv

from database import db
from models.model import Employee, Role, seed_employees, seedData, Customer, Account, UserRoles

from flask_security import Security, current_user
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.decorators import roles_required, roles_accepted

from routes.cashier_routes import cashier_bp
from routes.customer_routes import customer_bp
from routes.account_routes import account_bp

from flask_security.forms import LoginForm

load_dotenv()
from functools import wraps
from flask import session, redirect, url_for, flash



def create_app():
    app = Flask(__name__)

    # --- Config ---
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///bank.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Security
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT", "dev_salt_change_me")
    app.config["SECURITY_REGISTERABLE"] = False
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_PASSWORD_HASH"] = "pbkdf2_sha512"

    # Efter login 
    app.config["SECURITY_POST_LOGIN_VIEW"] = "/after-login"
    app.config["SECURITY_LOGIN_URL"] = "/login"


    db.init_app(app)
    Migrate(app, db)

    # --- Security datastore ---
    user_datastore = SQLAlchemyUserDatastore(db, Employee, Role)
    Security(app, user_datastore)

    # --- Blueprints ---
    
    app.register_blueprint(cashier_bp)
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(account_bp, url_prefix="/account")

    # --- Routes ---
    @app.route("/")
    def home():
        customer_count = db.session.query(Customer).count()
        account_count = db.session.query(Account).count()
        total_balance = db.session.query(db.func.coalesce(db.func.sum(Account.Balance), 0)).scalar()

        return render_template(
            "user/index.html",
            customer_count=customer_count,
            account_count=account_count,
            total_balance=total_balance,
        )

    @app.route("/about")
    def about():
        return render_template("user/about.html")
    

    @app.route("/login-choice")
    def login_choice():
        return render_template("user/login_choice.html")

    @app.route("/login-admin")
    def login_admin_page():
        form = LoginForm()
        return render_template(
            "user/login_admin.html", 
            preset_email="kimmo.ahola@systementor.se",
            login_user_form=form
        )

    @app.route("/login-cashier") 
    def login_cashier_page():
        form = LoginForm() 
        return render_template(
            "user/login_cashier.html", 
            preset_email="kimmo.ahola@webbramwerk.se",
            login_user_form=form
        )


    @app.route("/customer-area")
    def customer_start():
    
        return redirect(url_for('customer.customer_profile')) 

    
    from models.model import UserRoles

    @app.route("/admin-dashboard")
    @roles_required("Admin")
    def admin_dashboard():
        employee_count = db.session.query(Employee).count()
    
    
        return render_template("admin/dashboard.html", employee_count=employee_count)


    
    @app.route("/after-login")
    def after_login():
        if current_user.has_role(UserRoles.Cashier.value):
            return redirect(url_for("cashier.cashier"))

        if current_user.has_role(UserRoles.Admin.value):
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("home"))


    with app.app_context():
        db.create_all()
        seed_employees(db, user_datastore)
        seedData(db)

    print(app.url_map)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
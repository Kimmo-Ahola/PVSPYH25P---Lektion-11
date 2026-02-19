import os
from flask import Flask, render_template
from flask_migrate import Migrate
from dotenv import load_dotenv

from database import db
from models.model import Employee, Role, seed_employees, seedData, Customer, Account
from flask_security import Security
from flask_security.datastore import SQLAlchemyUserDatastore

from routes.cashier_routes import cashier_bp  # se till att denna finns och har url_prefix
from routes.customer_routes import customer_bp
from routes.account_routes import account_bp



load_dotenv()

def create_app():
    app = Flask(__name__)

    for r in app.url_map.iter_rules():
        print(r.endpoint, "=>", r.rule)

 

    # --- Config ---
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # VIKTIGT: välj EN databasinställning (inte två).
    # Använd env om du vill, annars fallback sqlite:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///bank.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Security behöver salt (sätt gärna i .env)
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT", "dev_salt_change_me")
    # Valfritt men bra:
    app.config["SECURITY_REGISTERABLE"] = False
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_PASSWORD_HASH"] = "pbkdf2_sha512"

    SECURITY_POST_LOGIN_VIEW = "/after-login"


    # --- Init extensions ---
    db.init_app(app)
    Migrate(app, db)

    # --- Security (roles/users) ---
    user_datastore = SQLAlchemyUserDatastore(db, Employee, Role)
    Security(app, user_datastore)

    # --- Blueprints ---
    

    app.register_blueprint(cashier_bp, url_prefix="/cashier")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(account_bp, url_prefix="/account")


    # --- Routes ---
from flask import render_template, request, redirect, url_for
from flask_security import current_user

@app.route("/after-login")
def after_login():
    if not current_user.is_authenticated:
        return redirect(url_for("security.login"))

    if current_user.has_role("admin"):
        return redirect("/admin")

    if current_user.has_role("cashier"):
        return redirect("/cashier")

    return redirect("/")






    @app.route("/")
    def home():
        # G-krav: statistik synlig även utan inlogg
        customer_count = db.session.query(Customer).count()
        account_count = db.session.query(Account).count()

        # Summa saldo (om du senare byter till Decimal/Numeric funkar detta ändå)
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

    # --- Seeding vid start (bara i dev) ---
    with app.app_context():
        db.create_all()  # ok för sqlite/dev (om du kör migrate kan du ta bort den)
        seed_employees(db, user_datastore)
        seedData(db)

    return app



app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

print(app.url_map)

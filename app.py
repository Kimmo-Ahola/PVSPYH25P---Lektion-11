import os
from flask import Flask, render_template
from flask_migrate import Migrate
from database import db
from models.model import Employee, Role, seed_employees, seedData
from dotenv import load_dotenv
from models.model import seedData
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from routes.cashier_routes import cashier_bp

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
environment = os.getenv("FLASK_DEBUG")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") # ni har redan från WTForms
app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT") # ge den värdet bcrypt i .env
app.config["SECURITY_PASSWORD_HASH"] = os.getenv("SECURITY_PASSWORD_HASH") # ge den ett långt värde, gärna med koden i script.py
app.config["SECURITY_PASSWORD_SINGLE_HASH"] = False


db.init_app(app)
migrate = Migrate(app, db)
app.register_blueprint(cashier_bp)
# Create a user datastore that registers users in our system
# Connects a user to a role
user_datastore = SQLAlchemyUserDatastore(db, Employee, Role)
Security(app, user_datastore)

@app.route("/")
def home():
    return render_template("user/index.html")

if __name__ == "__main__":

    if os.environ.get("FLASK_DEBUG") == "1":
        with app.app_context():
            # We need the app_context when using the db outside of a request
            seedData(db)
            seed_employees(db, user_datastore)
        app.run(debug=True)
    else:
        app.run()

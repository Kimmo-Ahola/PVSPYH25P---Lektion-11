import os
from flask import Flask, render_template
from flask_migrate import Migrate
from livereload import Server
from database import db
from models.model import seedData
from dotenv import load_dotenv
from models.model import seedData

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
environment = os.getenv("FLASK_DEBUG")
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def home():
    return render_template("user/index.html")


if __name__ == "__main__":

    if os.environ.get("FLASK_DEBUG") == "1":
        with app.app_context():
            # We need the app_context when using the db outside of a request
            seedData(db)
        app.run(debug=True)
    else:
        app.run()

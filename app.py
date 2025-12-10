from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from livereload import Server
from models.model import db, seedData


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:user123@localhost/Bank"
db.app = app
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def startpage():
    return render_template("index.html")


if __name__ == "__main__":
    import os

    if os.environ.get("FLASK_DEBUG") == "1":
        from livereload import Server

        server = Server(app.wsgi_app)
        server.watch("templates/")
        server.watch("static/")
        server.serve(open_url_delay=True)
    else:
        # TODO implement something better later
        app.run()

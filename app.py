from flask import Flask, render_template, request, redirect, flash, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import dbInit
import userHandling
app = Flask(__name__)
app.secret_key = "charizard"

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    user_id = session.get("user_id")
    if cursor.execute("""SELECT hasPref FROM user WHERE Id = ?""", (user_id,)):
        return redirect("/about")

    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method == "POST":
        login_input = request.form["login"]
        password = request.form["password"]

        user = userHandling.get_user_by_login(login_input)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect("/")

        flash("Invalid username/email or password")

    return redirect("/login")
    
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/createAccount")
def createAccount():
    return render_template("createAccount.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    if userHandling.create_user(username, password, email):
        return redirect("/login")
    else:
        flash("Username already taken")
        return redirect("/createAccount")

@app.route("/delete-account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        abort(403)

    delete_user(session["user_id"])
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    dbInit.initDatabase()
    app.run(debug=True)



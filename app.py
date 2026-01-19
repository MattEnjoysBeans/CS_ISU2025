from flask import Flask, render_template, request, redirect, flash, session, abort
from urllib.parse import urlparse
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import dbInit
import userHandling
import scraping
import json
app = Flask(__name__)
app.secret_key = "charizard"

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row
    user_id = session.get("user_id")
    cursor.execute("""SELECT hasPref FROM user WHERE Id = (?)""", (session["user_id"],))
    result = cursor.fetchone()

    if result == 0:
        return redirect("/prefs")

    return render_template("home.html")

@app.route("/prefs")
def prefs():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row
    sources = connection.execute(
        "SELECT SourceId, SourceName FROM source_list WHERE UserID = (?)", (session["user_id"],)).fetchall()
    connection.close()
    return render_template("prefs.html", sources=sources)

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

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        items = request.form.getlist("items[]")

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("""SELECT hasPref FROM user WHERE Id = (?)""", (session["user_id"],))
        resultskip = cursor.fetchone

        if resultskip == 1 and not items:
            connection.commit()
            connection.close()
            return redirect("/")

        for item in items:
            if item.strip():
                urlRaw = item
                parsedUrl = urlparse(urlRaw)
                urlPath = parsedUrl.path
                sourceName = parsedUrl.netloc
                if sourceName == "www.youtube.com":
                    sourceName += urlPath

                cursor.execute(
                    "INSERT INTO source_list (url, SourceName, UserID) VALUES (?, ?, ?)",
                    (item.strip(), sourceName, session["user_id"],)
                )
                cursor.execute(
                    "SELECT * FROM source_list WHERE UserId = (?)",
                    (session["user_id"],)
                )

                result = cursor.fetchone()

        if result:
            cursor.execute(
                "UPDATE user SET hasPref = 1 WHERE Id = (?)",
                (session["user_id"],)
            )
            connection.commit()
            connection.close()
            return redirect("/")
        else:
            connection.commit()
            connection.close()
            return redirect("/prefs")

    connection.commit()
    connection.close()
    return redirect("/prefs")

@app.route("/clearpref", methods=["GET", "POST"])
def clearpref():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM source_list WHERE UserID = ?",
        (session["user_id"],)
    )
    cursor.execute(
        "UPDATE user SET hasPref = 0 WHERE Id = (?)",
        (session["user_id"],)
    )
    connection.commit()
    connection.close()
    return redirect("/prefs")

@app.route("/search", methods=["GET"])
def search():
    if request.method == "GET":
        userSearch = request.args.get("q", "")
        print(userSearch)
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        connection.row_factory = sqlite3.Row
        cursor.execute(
            "SELECT SourceName FROM source_list WHERE UserId = (?)",
                (session["user_id"],)
            )
        items = cursor.fetchall()
        connection.close()
        print(items)
        results = []
        for item in items:
            combinedSearch = str(userSearch) + " tab " + str(item)
            result = scraping.searchQuery(combinedSearch)
            results.append(result)
        print(results)
        return render_template("results.html", results=results)

@app.route("/favourite", methods=["POST"])
def favourite():
    result = request.form.get("result")
    is_favourite = "favourite" in request.form

    print(result)
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row
    cursor.execute("""
        INSERT INTO Tsaved (UserID, url, IsFav)
        VALUES (?, ?, ?)
        ON CONFLICT(UserID, url)
        DO UPDATE SET IsFavourite = excluded.IsFavourite
    """, (session["user_id"], result, is_favourite))

    connection.commit()
    connection.close()
    return redirect(request.referrer)

if __name__ == "__main__":
    dbInit.initDatabase()
    app.run(debug=True)





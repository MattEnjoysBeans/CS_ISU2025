from flask import Flask, render_template, request, redirect, flash, session, abort, make_response
from urllib.parse import urlparse
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import dbInit
import userHandling
import scraping
import json
import secrets
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = "charizard"

#tries to redirect user to homepage, if fails redirect to login, checks for 'remember' cookie
@app.route("/")
def index():
    if "user_id" not in session:
        token = request.cookies.get("remember_token")
        if token:
            cursor.execute(
                "SELECT user_id FROM remember_tokens WHERE token = ? AND expires_at > CURRENT_TIMESTAMP",
                (token,)
            )
            row = cursor.fetchone()
            if row:
                session["user_id"] = row["user_id"]
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

#sends user to preference page and loads their prefered sites
@app.route("/prefs")
def prefs():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row
    sources = connection.execute(
        "SELECT SourceId, SourceName FROM source_list WHERE UserID = (?)", (session["user_id"],)).fetchall()
    connection.close()
    return render_template("prefs.html", sources=sources)

#redirect to login page
@app.route("/login")
def login():
    return render_template("login.html")

#check credentials/cookie if user clicked 'remember me'
@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method == "POST":
        login_input = request.form["login"]
        password = request.form["password"]

        user = userHandling.get_user_by_login(login_input)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            connection = sqlite3.connect("database.db")
            cursor = connection.cursor()

            response = make_response(redirect("/"))
            if request.form.get("remember"):
            
                token = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(days=30)

                cursor.execute(
                    "INSERT INTO remember_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
                    (user["Id"], token, expires)
                )
            
                response.set_cookie(
                    "remember_token",
                    token,
                    max_age=60 * 60 * 24 * 30,
                    httponly=True,
                    samesite="Lax"
                )
            connection.commit()
            connection.close()
            return response

        flash("Invalid username/email or password")

    return redirect("/login")
    
#end session and void cookie
@app.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("remember_token")

    if token:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM remember_tokens WHERE token = ?", (token,))
        connection.commit()
        connection.close()

    session.clear()
    response = make_response(redirect("/login"))
    response.delete_cookie("remember_token")
    return response

#redirect to the register page
@app.route("/createAccount")
def createAccount():
    return render_template("createAccount.html")

#register account info into database then send user back to login
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

#deletes account (only accessible through terminal not on the site)
@app.route("/delete-account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        abort(403)

    delete_user(session["user_id"])
    session.clear()
    return redirect("/")

#submit all preferences to database and filter out the name/url
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

#remove all preferences associated to the user
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

#query the user's search alongside their preferred sites
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

#save the specific search result into another table
@app.route("/favourite", methods=["GET"])
def favourite():
    if request.method == "GET":
        resultLink = request.args.get("resultlink")
        resultName = request.args.get("resultname")

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        connection.row_factory = sqlite3.Row
        cursor.execute("""
            INSERT INTO Tsaved (UserID, url, urlName, IsFav)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(UserID, url)
            DO UPDATE SET IsFav = excluded.IsFav
        """, (session["user_id"], resultLink, resultName, True))

        connection.commit()
        connection.close()
        return redirect(request.referrer)

#redirect to favourites page and load all of user's favourited results
@app.route("/saved")
def saved():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row
    saved = connection.execute(
        "SELECT url, urlName FROM Tsaved WHERE UserID = (?)", (session["user_id"],)).fetchall()
    connection.close()
    return render_template("favourites.html", saved=saved)

#remove all favourited results
@app.route("/clearfav", methods=["GET", "POST"])
def clearfav():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM Tsaved WHERE UserID = ?",
        (session["user_id"],)
    )
    connection.commit()
    connection.close()
    return redirect("/saved")


if __name__ == "__main__":
    dbInit.initDatabase()
    app.run(debug=True)





from flask import Flask, render_template, request, redirect, flash, session, abort
import dbInit
import userHandling
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if create_user(username, password):
        return redirect("/login")
    else:
        flash("Username already taken")
        return redirect("/register")

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



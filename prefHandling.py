import sqlite3
def addPrefs():
    items = request.form.getlist("items[]")
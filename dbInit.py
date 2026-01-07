import sqlite3

def initDatabase():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor
    cursor.close()
    connection.close()
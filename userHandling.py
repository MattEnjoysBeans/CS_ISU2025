import sqlite3
from werkzeug.security import generate_password_hash

def create_user(username, password):
    password_hash = generate_password_hash(password)

    try:
        connection = connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row

        connection.execute(
            "INSERT INTO user (Username, Password_Hash) VALUES (?, ?)",
            (username, password_hash)
        )
        connection.commit()
        connection.close()
        return True

    except sqlite3.IntegrityError:
        return False

def delete_user(Id):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM user WHERE Id = ?",
        (Id,)
    )

    connection.commit()
    rows_deleted = cursor.rowcount
    connection.close()

    return rows_deleted > 0


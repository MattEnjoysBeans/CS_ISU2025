import sqlite3
from werkzeug.security import generate_password_hash

def create_user(username, password, email):
    password_hash = generate_password_hash(password)

    try:
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row

        connection.execute(
            "INSERT INTO user (Username, Password_Hash, Email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        connection.commit()
        connection.close()
        return True

    except sqlite3.IntegrityError:
        return False

def get_user_by_login(login):
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    user = connection.execute(
        """
        SELECT * FROM user
        WHERE username = ?
           OR email = ?
        """,
        (login, login)
    ).fetchone()
    connection.close()
    return user

def delete_user(Id):
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM user WHERE Id = ?",
        (Id,)
    )

    connection.commit()
    rows_deleted = cursor.rowcount
    connection.close()

    return rows_deleted > 0

for i in range(0):
    kill = delete_user(input("Id: "))

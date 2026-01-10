import sqlite3

def initDatabase():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    queryFK = '''
    PRAGMA foreign_keys = ON;
    '''
    enableFK = cursor.execute(queryFK)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_list (
            SourceId INTEGER PRIMARY KEY AUTOINCREMENT,
            SourceName TEXT NOT NULL,
            Url TEXT NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password_Hash TEXT NOT NULL,
            Email TEXT UNIQUE,
            Created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tabPref (
            TpID INTEGER PRIMARY KEY,
            UserID INTEGER,
            FOREIGN KEY (UserID) REFERENCES user(Id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YTPref (
            VidpID INTEGER PRIMARY KEY,
            UserID INTEGER,
            FOREIGN KEY (UserID) REFERENCES user(Id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tsaved (
            UserID INTEGER,
            FOREIGN KEY (UserID) REFERENCES user(Id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YTsaved (
            UserID INTEGER,
            FOREIGN KEY (UserID) REFERENCES user(Id)
        );
    """)

    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]

    if "hasPref" not in columns:
        cursor.execute("""
            ALTER TABLE user
            ADD COLUMN hasPref INTEGER DEFAULT 0 NOT NULL;
        """)

    connection.commit()
    connection.close()
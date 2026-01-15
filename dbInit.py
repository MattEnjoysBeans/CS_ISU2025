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
            Url TEXT NOT NULL,
            UserID INTEGER,
            FOREIGN KEY (UserID) REFERENCES user(Id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password_Hash TEXT NOT NULL,
            Email TEXT UNIQUE,
            Created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
            hasPref INTEGER DEFAULT 0 NOT NULL
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tabPref (
            TpID INTEGER PRIMARY KEY,
            UserID INTEGER,
            SId INTEGER NOT NULL,
            FOREIGN KEY (SId) REFERENCES source_list(SourceId) ON DELETE CASCADE,
            FOREIGN KEY (UserID) REFERENCES user(Id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YTPref (
            VidpID INTEGER PRIMARY KEY,
            UserID INTEGER NOT NULL,
            FOREIGN KEY (UserID) REFERENCES user(Id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tsaved (
            UserID INTEGER NOT NULL,
            url TEXT,
            FOREIGN KEY (UserID) REFERENCES user(Id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YTsaved (
            UserID INTEGER NOT NULL,
            url TEXT,
            FOREIGN KEY (UserID) REFERENCES user(Id) ON DELETE CASCADE
        );
    """)

    cursor.execute("PRAGMA table_info(tabPref)")
    columns = [col[1] for col in cursor.fetchall()]

    connection.commit()
    connection.close()
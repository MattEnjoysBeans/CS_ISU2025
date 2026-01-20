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
        CREATE TABLE IF NOT EXISTS Tsaved (
            UserID INTEGER NOT NULL ,
            url TEXT,
            urlName TEXT,
            IsFav BOOLEAN,
            FOREIGN KEY (UserID) REFERENCES user(Id) ON DELETE CASCADE,
            UNIQUE(UserID, url)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remember_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(Id) ON DELETE CASCADE
    );
    """)

    cursor.execute("PRAGMA table_info(tabPref)")
    columns = [col[1] for col in cursor.fetchall()]

    connection.commit()
    connection.close()
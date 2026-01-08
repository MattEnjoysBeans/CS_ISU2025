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
            UserId INTEGER PRIMARY KEY,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL UNIQUE,
            Email TEXT UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tabPref (
            TpID INTEGER PRIMARY KEY,
            UserID FOREIGN KEY
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YTPref (
            VidpID INTEGER PRIMARY KEY,
            UserID FOREIGN KEY
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tsaved (
            UserID FOREIGN KEY,
            Url_1 TEXT,
            Url_2 TEXT,
            Url_3 TEXT,
            Url_4 TEXT,
            Url_5 TEXT, 
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YTsaved (
            UserID FOREIGN KEY,
            Url_1 TEXT,
            Url_2 TEXT,
            Url_3 TEXT,
            Url_4 TEXT,
            Url_5 TEXT, 
        );
    """)
    cursor.commit()
    cursor.close()
    connection.close()
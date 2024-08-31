from utils.db.connect import connect
import sqlite3 as sq


def create_tables():
    """Create tables if they do not exist"""
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            create = '''
            CREATE TABLE IF NOT EXISTS volunteer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                TGID TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                highest_education TEXT NOT NULL,
                is_employed BOOLEAN NOT NULL,
                needs TEXT NOT NULL,
                bio TEXT, 
                profile_pic TEXT,
                is_joined_group BOOLEAN NOT NULL DEFAULT 0,
                JOINED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
            cursor.execute(create)
            database.commit()
    except sq.Error as e:
        print(f"An error occurred: {e}")


def insert_data(data):
    """Insert data into the database"""
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            insert = '''
            INSERT INTO volunteer (
                TGID, username, first_name, last_name, email, phone, address, highest_education, is_employed, needs, bio, profile_pic
            ) VALUES (?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?) '''
            cursor.execute(insert, data)
            database.commit()
    except sq.Error as e:
        print(f"An error occurred: {e}")

# create_tables()

from utils.db.connect import connect
import sqlite3 as sq


def create_tables():
    """Create tables if they do not exist."""
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
                gender TEXT NOT NULL,
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
        print(f"An error occurred while creating the tables: {e}")
    finally:
        conn.close()


def insert_data(data):
    """Insert data into the volunteer table."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            insert = '''
            INSERT INTO volunteer (
                TGID, username, first_name, last_name, gender, email, phone, address, highest_education, is_employed, 
                needs, bio, profile_pic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert, data)
            database.commit()
    except sq.Error as e:
        print(f"An error occurred while inserting data: {e}")
    finally:
        conn.close()


def search_table_by_tg_id(tg_id):
    """Search the volunteer table by TGID."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            search = 'SELECT * FROM volunteer WHERE TGID = ?'
            cursor.execute(search, (tg_id,))
            return cursor.fetchone()
    except sq.Error as e:
        print(f"An error occurred while searching for TGID {tg_id}: {e}")
    finally:
        conn.close()


def search_table_by_username(username):
    """Search the volunteer table by username."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            search = 'SELECT * FROM volunteer WHERE username = ?'
            cursor.execute(search, (username,))
            return cursor.fetchone()
    except sq.Error as e:
        print(f"An error occurred while searching for username {username}: {e}")
    finally:
        conn.close()


def search_table_by_phone(phone):
    """Search the volunteer table by phone number."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            search = 'SELECT * FROM volunteer WHERE phone = ?'
            cursor.execute(search, (phone,))
            return cursor.fetchone()
    except sq.Error as e:
        print(f"An error occurred while searching for phone number {phone}: {e}")
    finally:
        conn.close()


def search_table_by_email(email):
    """Search the volunteer table by email."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            search = 'SELECT * FROM volunteer WHERE email = ?'
            cursor.execute(search, (email,))
            return cursor.fetchone()
    except sq.Error as e:
        print(f"An error occurred while searching for email {email}: {e}")
    finally:
        conn.close()


def is_joined_group(tg_id):
    """Check if the volunteer has joined the group."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            search = 'SELECT is_joined_group FROM volunteer WHERE TGID = ?'
            cursor.execute(search, (tg_id,))
            return bool(cursor.fetchone()[0])
    except sq.Error as e:
        print(f"An error occurred while searching for TGID {tg_id}: {e}")
    finally:
        conn.close()


def change_joined_group_status(tg_id, status):
    """Change the joined group status of the volunteer."""
    create_tables()  # Ensure the table exists
    conn = connect()
    try:
        with conn as database:
            cursor = database.cursor()
            update = 'UPDATE volunteer SET is_joined_group = ? WHERE TGID = ?'
            cursor.execute(update, (status, tg_id))
            database.commit()
    except sq.Error as e:
        print(f"An error occurred while changing the joined group status of TGID {tg_id}: {e}")
    finally:
        conn.close()

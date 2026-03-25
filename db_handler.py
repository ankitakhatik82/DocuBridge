import sqlite3

# Dono jagah same naam rakho
DB_NAME = "docubridge.db"

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def setup_database():
    conn = get_db()
    cursor = conn.cursor()
    # Username ko UNIQUE kar diya taaki same name se do account na banein
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user TEXT, 
            filename TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database check: Tables are ready!")

def register_user(u, p):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        return True
    except sqlite3.IntegrityError: 
        # Agar username pehle se exist karta hai
        return False
    except: 
        return False
    finally: 
        conn.close()

def check_login(u, p):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    user = cursor.fetchone()
    conn.close()
    return user

def add_to_history(u, f):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (user, filename) VALUES (?, ?)", (u, f))
    conn.commit()
    conn.close()

def get_user_history(u):
    conn = get_db()
    cursor = conn.cursor()
    # Order by ID DESC taaki nayi files upar dikhein
    cursor.execute("SELECT id, filename FROM history WHERE user=? ORDER BY id DESC", (u,))
    rows = cursor.fetchall() 
    conn.close()
    return rows

def delete_history_item(hid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id=?", (hid,))
    conn.commit()
    conn.close()
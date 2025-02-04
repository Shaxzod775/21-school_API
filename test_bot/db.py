import sqlite3
import random

def init_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                   chatId INTEGER PRIMARY KEY AUTOINCREMENT,
                   language TEXT NOT NULL,
                   campus TEXT NOT NULL,
                   stream TEXT NOT NULL
    )''')

    conn.commit()
    conn.close() 

def create_user(chatId, language, campus, stream):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    insert_values = (chatId, language, campus, stream)

    try:
        cursor.execute("INSERT INTO users (chatId, language, campus, stream) VALUES (?, ?, ?, ?)", insert_values)

        conn.commit()
        print("User created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating user: {e}")
        conn.rollback()

    finally:
        conn.close()

def get_user(chatId):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chatId == ?", (chatId,))
    user = cursor.fetchone()

    conn.close()  
    return user


def update_user(chatId, language=None, campus=None, stream=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    if campus:
        cursor.execute('UPDATE users SET campus = ? WHERE chatId = ?', (campus, chatId))
    if stream:
        cursor.execute('UPDATE users SET stream = ? WHERE chatId = ?', (stream, chatId))
    if language:
        cursor.execute('UPDATE users SET language = ? WHERE chatId = ?', (language, chatId))
    conn.commit()
    conn.close()

def drop_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE users")

        conn.commit()
        print("The table has been successfully dropped!")

    except sqlite3.Error as e:
        print(f"Error dropping table: {e}")
        conn.rollback()

    finally:
        conn.close()


if __name__ == '__main__':
    init_table()
    user = get_user(00000)
    if user:
        print("User already exists in db")
        print(user)
    else: 
        create_user(00000, 'russian', 'Samarkand', 'intensiv')
    
    # drop_table()
        
    # create_user(00000, 'russian', 'Samarkand')







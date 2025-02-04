import sqlite3

# Initialize the database
def init_db():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            campus TEXT,
            stream TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user(chat_id):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_user(chat_id, campus=None, stream=None):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()

    # Check if the user already exists
    cursor.execute('SELECT chat_id FROM users WHERE chat_id = ?', (chat_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # User already exists, update their record
        cursor.execute('''
            UPDATE users
            SET campus = ?, stream = ?
            WHERE chat_id = ?
        ''', (campus, stream, chat_id))
    else:
        # User does not exist, insert a new record
        cursor.execute('''
            INSERT INTO users (chat_id, campus, stream)
            VALUES (?, ?, ?)
        ''', (chat_id, campus, stream))

    conn.commit()
    conn.close()
def update_user(chat_id, campus=None, stream=None):
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    if campus:
        cursor.execute('UPDATE users SET campus = ? WHERE chat_id = ?', (campus, chat_id))
    if stream:
        cursor.execute('UPDATE users SET stream = ? WHERE chat_id = ?', (stream, chat_id))
    conn.commit()
    conn.close()

# Call this function at the start of your bot
# init_db()

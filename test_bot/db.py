import sqlite3

def init_table_users():
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

def get_data(chatId, field):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    if field not in ('campus', 'language', 'stream'):
        raise Exception(f"The given field is not in the list of fields!\n{field}")

    cursor.execute(f"SELECT {field} FROM users WHERE chatId == ?", (chatId,))
    data = cursor.fetchone()

    conn.close()  
    return data


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

def drop_table(table):
    conn = sqlite3.connect(f'{table}.db')
    cursor = conn.cursor()

    try:
        cursor.execute(f"DROP TABLE {table}")

        conn.commit()
        print("The table has been successfully dropped!")

    except sqlite3.Error as e:
        print(f"Error dropping table: {e}")
        conn.rollback()

    finally:
        conn.close()



def init_table_posts():
    try:
        conn = sqlite3.connect('posts.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task TEXT UNIQUE NOT NULL,
                            url_passed TEXT UNIQUE,
                            url_scored_hundred TEXT UNIQUE,
                            url_scored_didnt_pass TEXT UNIQUE,
                            url_in_progress TEXT UNIQUE,
                            url_in_reviews TEXT UNIQUE,
                            url_registered TEXT UNIQUE
                        )''')

        conn.commit()
        print("Table 'posts' created or already exists.")  
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:  
            conn.rollback()  
    finally:
        if conn:
            conn.close()



def create_post(task, url, url_type):
    """
    Inserts or updates a post entry in the 'posts' table.

    Parameters:
    - task (str): The task identifier.
    - url (str): The URL to store.
    - url_type (str): The column name where the URL should be stored (e.g., 'url_passed', 'url_in_reviews').
    """
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()

    try:
        allowed_columns = {'url_passed', 'url_scored_hundred', 'url_scored_didnt_pass', 'url_in_progress', 'url_in_reviews', 'url_registered'}
        if url_type not in allowed_columns:
            raise ValueError(f"Invalid url_type: {url_type}")

        cursor.execute("SELECT * FROM posts WHERE task = ?", (task,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(f"UPDATE posts SET {url_type} = ? WHERE task = ?", (url, task))
        else:
            # Insert a new record
            cursor.execute(f"INSERT INTO posts (task, {url_type}) VALUES (?, ?)", (task, url))

        conn.commit()
        print("Post saved successfully.")

    except sqlite3.Error as e:
        print(f"Error creating/updating post: {e}")
        conn.rollback()

    finally:
        conn.close()

def get_post(task, url_type):
    """
    Retrieves a specific URL from the 'posts' table for a given task.

    Parameters:
    - task (str): The task identifier.
    - url_type (str): The column name to retrieve (e.g., 'url_passed', 'url_in_reviews').

    Returns:
    - str: The URL if found, otherwise None.
    """

    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()

    allowed_columns = {'url_passed', 'url_scored_hundred', 'url_scored_didnt_pass', 'url_in_reviews', 'url_registered'}
    if url_type not in allowed_columns:
        raise ValueError(f"Invalid url_type: {url_type}")

    cursor.execute(f"SELECT {url_type} FROM posts WHERE task = ?", (task,))
    post = cursor.fetchone()

    conn.close()

    return post[0] if post and post[0] else None  # Return the URL or None


def update_post(task, url_type, url):
    """
    Updates a specific URL field for a task in the 'posts' table.

    Parameters:
    - task (str): The task identifier.
    - url_type (str): The column name to update (e.g., 'url_passed', 'url_in_reviews').
    - url (str): The new URL to set.

    Returns:
    - bool: True if an update was made, False otherwise.
    """

    if not url:
        return False  
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()

    allowed_columns = {'url_passed', 'url_scored_hundred', 'url_scored_didnt_pass', 'url_in_reviews', 'url_registered'}
    if url_type not in allowed_columns:
        raise ValueError(f"Invalid url_type: {url_type}")

    cursor.execute(f"UPDATE posts SET {url_type} = ? WHERE task = ?", (url, task))
    conn.commit()
    
    updated = cursor.rowcount > 0  # Check if any row was affected

    conn.close()
    
    return updated


if __name__ == '__main__':
    # drop_table("posts")
    init_table_posts()

    # print(get_post("P01D06", "url_passed"))

    # init_table_users()
    # user = get_user(00000)
    # if user:
    #     print("User already exists in db")
    #     print(user)
    # else: 
    #     create_user(00000, 'russian', 'Samarkand', 'intensiv')
    
    # drop_table("users")
        
    # create_user(00000, 'russian', 'Samarkand')







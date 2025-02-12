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
                            url_passed_english_tashkent TEXT UNIQUE,
                            url_passed_russian_tashkent TEXT UNIQUE,
                            url_passed_uzbek_tashkent TEXT UNIQUE,
                            url_hundred_english_tashkent TEXT UNIQUE,
                            url_hundred_russian_tashkent TEXT UNIQUE,
                            url_hundred_uzbek_tashkent TEXT UNIQUE,
                            url_scored_didnt_pass_english_tashkent TEXT UNIQUE,
                            url_scored_didnt_pass_russian_tashkent TEXT UNIQUE,
                            url_scored_didnt_pass_uzbek_tashkent TEXT UNIQUE,
                            url_in_progress_english_tashkent TEXT UNIQUE,
                            url_in_progress_russian_tashkent TEXT UNIQUE,
                            url_in_progress_uzbek_tashkent TEXT UNIQUE,
                            url_in_reviews_english_tashkent TEXT UNIQUE,
                            url_in_reviews_russian_tashkent TEXT UNIQUE,
                            url_in_reviews_uzbek_tashkent TEXT UNIQUE,
                            url_registered_english_tashkent TEXT UNIQUE,
                            url_registered_russian_tashkent TEXT UNIQUE,
                            url_registered_uzbek_tashkent TEXT UNIQUE,
                            url_passed_english_samarkand TEXT UNIQUE,
                            url_passed_russian_samarkand  TEXT UNIQUE,
                            url_passed_uzbek_samarkand TEXT UNIQUE,
                            url_hundred_english_samarkand TEXT UNIQUE,
                            url_hundred_russian_samarkand TEXT UNIQUE,
                            url_hundred_uzbek_samarkand TEXT UNIQUE,
                            url_scored_didnt_pass_english_samarkand TEXT UNIQUE,
                            url_scored_didnt_pass_russian_samarkand TEXT UNIQUE,
                            url_scored_didnt_pass_uzbek_samarkand TEXT UNIQUE,
                            url_in_progress_english_samarkand TEXT UNIQUE,
                            url_in_progress_russian_samarkand TEXT UNIQUE,
                            url_in_progress_uzbek_samarkand TEXT UNIQUE,
                            url_in_reviews_english_samarkand TEXT UNIQUE,
                            url_in_reviews_russian_samarkand TEXT UNIQUE,
                            url_in_reviews_uzbek_samarkand TEXT UNIQUE,
                            url_registered_english_samarkand TEXT UNIQUE,
                            url_registered_russian_samarkand TEXT UNIQUE,
                            url_registered_uzbek_samarkand TEXT UNIQUE
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


def _validate_url_type(url_type):  # Helper function to validate url_type
    allowed_columns = [
        'url_passed_english_tashkent', 'url_passed_russian_tashkent', 'url_passed_uzbek_tashkent',
        'url_hundred_english_tashkent', 'url_hundred_russian_tashkent', 'url_hundred_uzbek_tashkent',
        'url_scored_didnt_pass_english_tashkent', 'url_scored_didnt_pass_russian_tashkent', 'url_scored_didnt_pass_uzbek_tashkent',
        'url_in_progress_english_tashkent', 'url_in_progress_russian_tashkent', 'url_in_progress_uzbek_tashkent',
        'url_in_reviews_english_tashkent', 'url_in_reviews_russian_tashkent', 'url_in_reviews_uzbek_tashkent',
        'url_registered_english_tashkent', 'url_registered_russian_tashkent', 'url_registered_uzbek_tashkent',
        'url_passed_english_samarkand', 'url_passed_russian_samarkand', 'url_passed_uzbek_samarkand',
        'url_hundred_english_samarkand', 'url_hundred_russian_samarkand', 'url_hundred_uzbek_samarkand',
        'url_scored_didnt_pass_english_samarkand', 'url_scored_didnt_pass_russian_samarkand', 'url_scored_didnt_pass_uzbek_samarkand',
        'url_in_progress_english_samarkand', 'url_in_progress_russian_samarkand', 'url_in_progress_uzbek_samarkand',
        'url_in_reviews_english_samarkand', 'url_in_reviews_russian_samarkand', 'url_in_reviews_uzbek_samarkand',
        'url_registered_english_samarkand', 'url_registered_russian_samarkand', 'url_registered_uzbek_samarkand'
    ]
    if url_type not in allowed_columns:
        raise ValueError(f"Invalid url_type: {url_type}")


def create_post(task, url, url_type):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()

    try:
        _validate_url_type(url_type)  # Validate the url_type

        cursor.execute("SELECT * FROM posts WHERE task = ?", (task,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(f"UPDATE posts SET {url_type} = ? WHERE task = ?", (url, task))
        else:
            cursor.execute(f"INSERT INTO posts (task, {url_type}) VALUES (?, ?)", (task, url))

        conn.commit()
        print(f"Post saved successfully. {url_type} URL = {url}")

    except sqlite3.Error as e:
        print(f"Error creating/updating post: {e}")
        conn.rollback()
    except ValueError as e: # Catch the ValueError if the url_type is invalid
        print(e)

    finally:
        conn.close()


def get_post(task, url_type):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()

    try:
        _validate_url_type(url_type)

        cursor.execute(f"SELECT {url_type} FROM posts WHERE task = ?", (task,))
        post = cursor.fetchone()

        return post[0] if post and post[0] else None

    except ValueError as e:
        print(e)
        return None  # Return None if invalid url_type
    finally:
        conn.close()


def update_post(task, url_type, url):
    if not url:
        return False

    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()

    try:
        _validate_url_type(url_type)

        cursor.execute(f"UPDATE posts SET {url_type} = ? WHERE task = ?", (url, task))
        conn.commit()

        updated = cursor.rowcount > 0

        return updated
    except ValueError as e:
        print(e)
        return False
    finally:
        conn.close()


# if __name__ == '__main__':
#     drop_table("posts")
#     init_table_posts()








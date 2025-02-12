import sqlite3
import datetime
from config_api import *

def init_table_tasks():
    try:
        conn = sqlite3.connect('./data/tasks.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            task_id INTEGER PRIMARY KEY,
                            task TEXT UNIQUE NOT NULL,
                            has_been_parsed INTEGER,
                            being_parsed INTEGER,
                            start TEXT,  -- Date when task becomes available
                            end TEXT       -- Date after 7 days from start
                        )''')

        conn.commit()
        print("Table 'tasks' created or already exists.")  
    except sqlite3.Error as e:
        raise Exception(f"An error occured while creating the table. Error: {e}")

def _validate_task(task):
    if task not in INTENSIVE:
        raise ValueError(f"Invalid task: {task}")


def create_task(task, has_been_parsed, being_parsed, start_date, end_date):  # Include start and end dates
    conn = sqlite3.connect('./data/tasks.db')
    cursor = conn.cursor()

    try:
        _validate_task(task)

        cursor.execute("SELECT * FROM tasks WHERE task = ?", (task,))
        existing_task = cursor.fetchone()

        if existing_task:
            cursor.execute("UPDATE tasks SET has_been_parsed = ?, being_parsed = ?, start = ?, end = ? WHERE task = ?", (has_been_parsed, being_parsed, start_date, end_date, task))
        else:
            cursor.execute("INSERT INTO tasks (task, has_been_parsed, being_parsed, start, end) VALUES (?, ?, ?, ?, ?)", (task, has_been_parsed, being_parsed, start_date, end_date))

        conn.commit()
        print(f"Task '{task}' saved successfully. has_been_parsed = {has_been_parsed}, being_parsed = {being_parsed}, start = {start_date}, end = {end_date}")

    except sqlite3.Error as e:
        raise sqlite3.Error(f"An error occured while creating the task. Error: {e}. Task: {task}")
    except ValueError as e:
        raise ValueError(f"ValueError {e}")
    finally:
        conn.close()


def get_task(task):
    conn = sqlite3.connect('./data/tasks.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT has_been_parsed, being_parsed, start, end FROM tasks WHERE task = ?", (task,)) #Added start and end
        task_data = cursor.fetchone()

        if task_data:
            has_been_parsed = bool(task_data[0])
            being_parsed = bool(task_data[1])
            start_date = task_data[2]  # Retrieve start date
            end_date = task_data[3]    # Retrieve end date
            return has_been_parsed, being_parsed, start_date, end_date #Return start and end dates
        else:
            return None, None, None, None  # Return None for all if task not found

    except sqlite3.Error as e:
         raise sqlite3.Error(f"An error occured while getting the task. Error: {e}. Task: {task}")
    finally:
        conn.close()


def update_task(task, has_been_parsed=None, being_parsed=None, start_date=None, end_date=None):  # Added start and end
    conn = sqlite3.connect('./data/tasks.db')
    cursor = conn.cursor()

    try:
        updates = []
        values = []

        if has_been_parsed is not None:
            updates.append("has_been_parsed = ?")
            values.append(int(has_been_parsed))

        if being_parsed is not None:
            updates.append("being_parsed = ?")
            values.append(int(being_parsed))

        if start_date is not None:
            updates.append("start = ?")
            values.append(start_date)

        if end_date is not None:
            updates.append("end = ?")
            values.append(end_date)

        if updates:
            sql = f"UPDATE tasks SET {', '.join(updates)} WHERE task = ?"
            values.append(task)
            cursor.execute(sql, tuple(values))
            conn.commit()
            updated = cursor.rowcount > 0
            return updated
        else:
            return False

    except sqlite3.Error as e:
         raise sqlite3.Error(f"An error occured while changing the task. Error: {e}. Task: {task}")
    finally:
        conn.close()


def populate_tasks():
    start_date = datetime.date(2025, 1, 27)  # Initial start date

    for task, (task_id, week) in INTENSIVE.items():
        has_been_parsed = 0
        being_parsed = 0

        if task.startswith('T'):
            start_time = datetime.time(9, 30)
            duration = datetime.timedelta(hours=36)
        elif task.startswith('E'):
            start_time = datetime.time(14, 30)
            duration = datetime.timedelta(hours=4)  # 18:30 - 14:30 = 4 hours
            start_date = start_date + datetime.timedelta(days=(4 - start_date.weekday()) % 7)  # Start every Friday
        elif task.startswith('P'):
            start_time = datetime.time(12, 00)
            duration = datetime.timedelta(hours=62)
            start_date = start_date + datetime.timedelta(days=(4 - start_date.weekday()) % 7)  # Start every Friday

        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = start_datetime + duration

        # Calculate the actual start date (when the task is *available*)
        available_datetime = start_datetime  # Tasks are available from the start time

        # Calculate the submission deadline (36, 62, or 4 hours later)
        deadline_datetime = start_datetime + duration

        available_str = available_datetime.strftime("%Y-%m-%d %H:%M:%S")
        deadline_str = deadline_datetime.strftime("%Y-%m-%d %H:%M:%S")

        create_task(task, has_been_parsed, being_parsed, available_str, deadline_str) #Store available and deadline times

        start_date = start_date + datetime.timedelta(days=7) 


def drop_table(table):
    conn = sqlite3.connect(f'./data/{table}.db')
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




if __name__ == "__main__":
    # drop_table("tasks")
    init_table_tasks()
    # populate_tasks()
    # task = "E01D05"
    # has_been_parsed, being_parsed, start_date, end_date = get_task(task)
    # print(f"The task is {task} it is start date is {start_date}, it is end date is {end_date}")

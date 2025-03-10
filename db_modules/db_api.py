import os
import sys

sys.path.append("..")

import sqlite3
import datetime
from configs.config_api import *

def init_table_tasks():
    try:
        conn = sqlite3.connect(f'data_{intensive_month_selected}/tasks.db')
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
    print(f"data_{intensive_month_selected}/tasks.db")
    conn = sqlite3.connect(f'data_{intensive_month_selected}/tasks.db')
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


def get_task(task, db_path):
    conn = sqlite3.connect(f'{db_path}')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT has_been_parsed, being_parsed, start, end FROM tasks WHERE task = ?", (task,))
        task_data = cursor.fetchone()

        if task_data:
            has_been_parsed = bool(task_data[0])
            being_parsed = bool(task_data[1])
            start_date = task_data[2]  
            end_date = task_data[3]    
            return has_been_parsed, being_parsed, start_date, end_date 
        else:
            return None, None, None, None  

    except sqlite3.Error as e:
         raise sqlite3.Error(f"An error occured while getting the task. Error: {e}. Task: {task}")
    finally:
        conn.close()


def update_task(db_path, task, has_been_parsed=None, being_parsed=None, start_date=None, end_date=None):  
    conn = sqlite3.connect(db_path)
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
    start_date = datetime.date(2025, 3, 3)  # Initial start date

    for task, (task_id, week) in INTENSIVE.items():
        has_been_parsed = 0
        being_parsed = 0

        if task.startswith('T'):
            # Task T starts every Monday, Tuesday, Wednesday, and Thursday at 9:30 AM
            start_time = datetime.time(9, 30)
            duration = datetime.timedelta(hours=36)
            
            # Calculate the next Monday, Tuesday, Wednesday, or Thursday
            while start_date.weekday() not in [0, 1, 2, 3]:  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday
                start_date += datetime.timedelta(days=1)

        elif task.startswith('E'):
            # Task E starts every Friday at 2:30 PM
            start_time = datetime.time(14, 30)
            duration = datetime.timedelta(hours=4)
            
            # Calculate the next Friday
            while start_date.weekday() != 4:  # 4=Friday
                start_date += datetime.timedelta(days=1)

        elif task.startswith('P'):
            # Task P starts every Friday at 9:24 AM
            start_time = datetime.time(9, 24)
            duration = datetime.timedelta(hours=62)
            
            # Calculate the next Friday
            while start_date.weekday() != 4:  # 4=Friday
                start_date += datetime.timedelta(days=1)

        # Combine date and time to create the start datetime
        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = start_datetime + duration

        # Calculate the actual start date (when the task is *available*)
        available_datetime = start_datetime  # Tasks are available from the start time

        # Calculate the submission deadline (36, 62, or 4 hours later)
        deadline_datetime = start_datetime + duration

        available_str = available_datetime.strftime("%Y-%m-%d %H:%M:%S")
        deadline_str = deadline_datetime.strftime("%Y-%m-%d %H:%M:%S")

        create_task(task, has_been_parsed, being_parsed, available_str, deadline_str)  # Store available and deadline times

        # Move to the next day after the current task's start date
        if task.startswith('E') or task.startswith('P'):
            # For E and P tasks, do not increment the date (they occur on the same Friday)
            pass
        else:
            # For T tasks, move to the next day
            start_date += datetime.timedelta(days=1)


def init_table_participants(campus, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS participants (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            student TEXT UNIQUE NOT NULL,
                            logtime INTEGER,
                            level INTEGER,
                            exp INTEGER,
                            exp_to_next_level INTEGER,
                            last_parced INTEGER
                        )''')

        conn.commit()
        print(f"Table 'participants' for {campus} created or already exists.")  
    except sqlite3.Error as e:
        raise Exception(f"An error occurred while creating the table. Error: {e}")
    finally:
        if conn: #Ensure conn is not None before closing
            conn.close()

def create_participant(db_path, campus, student, logtime=0, level=0, exp=0, exp_to_next_level=0, last_parced=0):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO participants (student, logtime, level, exp, exp_to_next_level, last_parced) VALUES (?, ?, ?, ?, ?, ?)", (student, logtime, level, exp, exp_to_next_level, last_parced))
        conn.commit()
        print(f"Participant {student} created for {campus}.")
        return True # Indicate success

    except sqlite3.Error as e:
        conn.rollback()  # Rollback on error
        print(f"Error creating participant: {e}")
        return False # Indicate failure

    finally:
        if conn:
            conn.close()


def update_participant(db_path, student, logtime=None, level=None, exp=None, exp_to_next_level=None, last_parced=0):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if logtime is not None:
            updates.append("logtime = ?")
            values.append(logtime)
        if level is not None:
            updates.append("level = ?")
            values.append(level)
        if exp is not None:
            updates.append("exp = ?")
            values.append(exp)
        if exp_to_next_level is not None:
            updates.append("exp_to_next_level = ?")
            values.append(exp_to_next_level)

        updates.append("last_parced = ?")
        values.append(last_parced)

        if updates:  # Check if there are any updates to perform
            sql = f"UPDATE participants SET {', '.join(updates)} WHERE student = ?"
            values.append(student)
            cursor.execute(sql, tuple(values))
            conn.commit()
            updated = cursor.rowcount > 0
            return updated
        else:
            return False  # No updates to perform

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating participant: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_participant(db_path, campus, student):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT logtime, level, exp, exp_to_next_level FROM participants WHERE student = ?", (student,))
        participant_data = cursor.fetchone()

        if participant_data:
            logtime, level, exp, exp_to_next_level = participant_data
            return {"logtime": logtime, "level": level, "exp": exp, "exp_to_next_level": exp_to_next_level}  # Return as a dictionary
        else:
            return None  # Return None if participant not found

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_participants(campus):
    try:
        conn = sqlite3.connect(f"data_{intensive_month_selected}/participants/{campus}/participants.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM participants")
        participant_data = cursor.fetchone()

        if participant_data:
            logtime, level, exp, exp_to_next_level = participant_data
            return {"logtime": logtime, "level": level, "exp": exp, "exp_to_next_level": exp_to_next_level}  # Return as a dictionary
        else:
            return None  # Return None if participant not found

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_incompleted_participants(campus):
    try:
        conn = sqlite3.connect(f"data_{intensive_month_selected}/participants/{campus}/participants.db")
        cursor = conn.cursor()

        cursor.execute("SELECT student FROM participants WHERE logtime > 0")
        participant_data = cursor.fetchall()

        if participant_data:
            # Extract the student usernames from the list of tuples
            incompleted_students = [row[0] for row in participant_data]  # Important change
            return incompleted_students  # Return the list of usernames
        else:
            return []  # Return an empty list if no incompleted participants are found

    except sqlite3.Error as e:
        print(f"Error getting incompleted participants: {e}")
        return []  # Return an empty list in case of error
    finally:
        if conn:
            conn.close()

def get_best_student(db_path):
    import os
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT student, level, exp FROM participants WHERE exp = (SELECT MAX(exp) FROM participants)")
            participant_data = cursor.fetchone()

            if participant_data:
                student, level, exp = participant_data
                return [student, level,  exp] # Return as a dictionary
            else:
                return None  # Return None if participant not found

        except sqlite3.Error as e:
            print(f"Error getting participant: {e}")
            return None
    else:
        raise Exception(f"The database does not exist {db_path}")

def get_active_students(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT student FROM participants WHERE logtime > 0")
        participants_data = cursor.fetchall()

        if participants_data:
            return len(participants_data)  
        else:
            return None  

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()




def get_active_student_list(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT student FROM participants WHERE logtime > 0")
        participants_data = cursor.fetchall()

        if participants_data:
            return [participant[0] for participant in participants_data]
        else:
            return None  

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()



def get_all_students(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT student FROM participants")
        participants_data = cursor.fetchall()

        if participants_data:
            return [participant[0] for participant in participants_data]  # Return as a dictionary
        else:
            return None  # Return None if participant not found

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()



def populate_participants(db_path, campus, students):
    for student in students:
        if not get_participant(db_path, campus, student):  # Check if student already exists
            create_participant(db_path, campus, student)
        else:
            print(f"Student {student} already exists. Skipping.")


def set_last_parced_student(db_path, student, last_parced):
    try:
        result = update_participant(db_path=db_path, student=student, logtime=None, level=None, exp=None, exp_to_next_level=None, last_parced=last_parced)
        if result:
            return True
    except sqlite3.Error as e:
        return False


def get_last_parced_student(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        sql = f"SELECT student from participants WHERE last_parced = 1"
        cursor.execute(sql)
        student = cursor.fetchone()
        
        if student:
            return student[0]

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating last parced student: {e}")
        return ""
    finally:
        if conn:
            conn.close()




def drop_table(table):
    conn = sqlite3.connect(f'data_{intensive_month_selected}/participants/samarkand/{table}.db')
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


def init_table_for_task(db_path):
    if not os.path.exists(f"{db_path}"):
        db_directory = "/".join(db_path.split("/")[:-1])
        if not os.path.exists(db_directory):
            os.mkdir(db_directory)
        with open(db_path, "w") as file:
            pass

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        task = db_path.split("/")[-1].split(".")[0]
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {task} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student TEXT UNIQUE NOT NULL,
                            title TEXT,
                            type TEXT,
                            status TEXT,
                            final_score TEXT
                        )''')

        conn.commit()
        print(f"Table '{task}' created or already exists.")  
    except sqlite3.Error as e:
        raise Exception(f"An error occured while creating the table. Error: {e}")
    

def create_task_result(db_path, student, title, type, status, final_score=None):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        task = db_path.split("/")[-1].split(".")[0]
        cursor.execute(f"INSERT INTO {task} (student, title, type, status, final_score) VALUES (?, ?, ?, ?, ?)", (student, title, type, status, final_score))
        conn.commit()
        print(f"Task result has been created for student {student}")
        return True  # Indicate success
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error creating task result: {e}")
        return False  # Indicate failure
    finally:
        if conn:
            conn.close()

def update_task_result(db_path, student, title=None, type=None, status=None, final_score=None):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        task = db_path.split("/")[-1].split(".")[0]

        updates = []
        values = []

        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if type is not None:
            updates.append("type = ?")
            values.append(type)
        if status is not None:
            updates.append("status = ?")
            values.append(status)
        if final_score is not None:
            updates.append("final_score = ?")
            values.append(final_score)

        if updates:  # Check if there are any updates to perform
            sql = f"UPDATE {task} SET {', '.join(updates)} WHERE student = ?"  # Added title to WHERE clause
            values.extend([student,]) #Added student and title
            cursor.execute(sql, tuple(values))
            conn.commit()
            return cursor.rowcount > 0 #Return True if any row was updated
        else:
            return False  # No updates to perform

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating task result: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_student_task_result(db_path, student):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        task = db_path.split("/")[-1].split(".")[0]
        cursor.execute(f"SELECT type, status, final_score FROM {task} WHERE student = ?", (student,))
        result = cursor.fetchone()
        if result:
            return {"type": result[0], "status": result[1], "final_score": result[2]}
        else:
            return None
    except sqlite3.Error as e:
        print(f"Error getting task result: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_students_task_results(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        task = db_path.split("/")[-1].split(".")[0]

        # Use parameterization to prevent SQL injection and handle missing tables correctly
        cursor.execute(f"SELECT student, title, type, status, final_score FROM {task}")  # No parameters needed here

        results = cursor.fetchall()

        if results:
            task_results = []
            for row in results:
                task_results.append({
                    "student": row[0],
                    "title": row[1],
                    "type": row[2],
                    "status": row[3],
                    "final_score": row[4]
                })
            return task_results
        else:
            return []  # Return an empty list if no results or table not found

    except sqlite3.Error as e:
        print(f"Error getting task results: {e}")
        return []  # Return an empty list in case of error

    finally:
        if conn:
            conn.close()


def get_student_task_result_by_status(db_path, status):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        task = db_path.split("/")[-1].split(".")[0]  # Extract table name from db_path

        if status == "NULL":
            cursor.execute(f"SELECT student FROM {task} WHERE status is NULL")
        else:
            cursor.execute(f"SELECT student FROM {task} WHERE status = ?", (status,))
        students = [row[0] for row in cursor.fetchall()]  # Extract student usernames
        return students

    except sqlite3.Error as e:
        print(f"Error getting students with status '{status}': {e}")
        return []  # Return an empty list in case of error

    finally:
        if conn:
            conn.close()


def populate_task_results(db_path, students):  # Changed student_data to students
    for student in students:
        if not get_student_task_result(db_path, student): 
            create_task_result(db_path, student, None, None, None)  # Other fields are None by default
        else:
            print(f"Task result for {student} already exists. Skipping.")




def init_table_personal_stats(campus, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS personal_stats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            student TEXT UNIQUE NOT NULL,
                            logtime INTEGER,
                            exp INTEGER,
                            total_tasks_accepted INTEGER,
                            educational_events INTEGER,
                            entertainment INTEGER,
                            total_number_events INTEGER,
                            last_parced INTEGER
                        )''')

        conn.commit()
        print(f"Table 'personal_stats' for {campus} created or already exists.")  
    except sqlite3.Error as e:
        raise Exception(f"An error occurred while creating the table. Error: {e}")
    finally:
        if conn: 
            conn.close()



def get_personal_stats(campus, db_path, student):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT logtime, exp, total_tasks_accepted, educational_events, entertainment, total_number_events, last_parced FROM personal_stats WHERE student = ?", (student,))
        result = cursor.fetchone()
        if result:
            return {
                "logtime": result[0],
                "exp": result[1],
                "total_tasks_accepted": result[2],
                "educational_events": result[3],
                "entertainment": result[4],
                "total_number_events": result[5],
                "last_parced": result[6]
            }
        else:
            return None
    except sqlite3.Error as e:
        print(f"Error getting personal stats: {e}")
        return None
    finally:
        if conn:
            conn.close()



def create_personal_stats(campus, db_path, student, logtime=0, exp=0, total_tasks_accepted=0, educational_events=0, entertainment=0, total_number_events=0, last_parced=0):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personal_stats (student, logtime, exp, total_tasks_accepted, educational_events, entertainment, total_number_events, last_parced) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (student, logtime, exp, total_tasks_accepted, educational_events, entertainment, total_number_events, last_parced))
        conn.commit()
        print(f"Student {student} has been added to the database in campus {campus}")
        return True
    except sqlite3.Error as e:
        print(f"Error creating personal stats for campus {campus}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()



def update_personal_stats(campus, db_path, student, logtime=None, exp=None, total_tasks_accepted=None, educational_events=None, entertainment=None, total_number_events=None, last_parced=None):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if logtime is not None:
            updates.append("logtime = ?")
            values.append(logtime)
        if exp is not None:
            updates.append("exp = ?")
            values.append(exp)
        if total_tasks_accepted is not None:
            updates.append("total_tasks_accepted = ?")
            values.append(total_tasks_accepted)
        if educational_events is not None:
            updates.append("educational_events = ?")
            values.append(educational_events)
        if entertainment is not None:
            updates.append("entertainment = ?")
            values.append(entertainment)
        if total_number_events is not None:
            updates.append("total_number_events = ?")
            values.append(total_number_events)
        if last_parced is not None:
            updates.append("last_parced = ?")
            values.append(last_parced)

        if updates:
            sql = f"UPDATE personal_stats SET {', '.join(updates)} WHERE student = ?"
            values.append(student)
            cursor.execute(sql, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
        else:
            return False

    except sqlite3.Error as e:
        print(f"Error updating personal stats for campus {campus}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()



def populate_personal_stats(campus, db_path, students):
    for student in students:
        if not get_personal_stats(campus, db_path, student):
            create_personal_stats(campus, db_path, student)
        else:
            print(f"Student {student} already exists. Skipping")



def get_last_parced_student_personal_stats(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        sql = f"SELECT student FROM personal_stats WHERE last_parced = 1"  # Corrected table name
        cursor.execute(sql)
        student = cursor.fetchone()

        if student:
            return student[0]  # Return the student name (string), not a tuple
        else:
            return None # Return None if no student is found

    except sqlite3.Error as e:
        print(f"Error getting last parced student: {e}")
        return None
    finally:
        if conn:
            conn.close()

def set_all_last_parced(campus):
    try:
        conn = sqlite3.connect(f"data_{intensive_month_selected}/participants/{campus}/personal_stats.db")
        cursor = conn.cursor()

        cursor.execute("UPDATE personal_stats SET last_parced = 0 WHERE last_parced = 1")
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error updating personal stats for campus {campus}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def set_last_parced_student_personal_stats(campus, db_path, student, last_parced):
    try:
        return update_personal_stats(campus=campus, db_path=db_path, student=student, last_parced=last_parced) # Directly return the result of update_personal_stats
    except sqlite3.Error as e:
        print(f"Error setting last parced student: {e}")
        return False
    


def get_all_active_students_personal_stats(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT student, logtime, exp, total_tasks_accepted, educational_events, entertainment, total_number_events FROM personal_stats WHERE logtime > 0")
        students = cursor.fetchall()

        if students:
            return students  
        else:
            return None 

    except sqlite3.Error as e:
        print(f"Error getting active students: {e}")
        return None
    finally:
        if conn:
            conn.close()



def set_being_updated(db_path, campus, being_updated):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

       # Check if there are any updates to perform
        cursor.execute(f"UPDATE overall SET being_updated = ? WHERE campus = ?", (being_updated, campus))
        conn.commit()
        if cursor.rowcount > 0:
            return True #Return True if any row was updated
        else:
            print("There is no such campus")
            return False
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating overall campus: {e}")
        return False
    finally:
        if conn:
            conn.close()

def check_being_updated(db_path, campus):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT being_updated FROM overall WHERE campus = ?", (campus,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(f"Error getting overall state of the campus {campus}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_participants_for_overall(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT student, logtime, level, exp, exp_to_next_level FROM participants")
        participant_data = cursor.fetchall()

        if participant_data:
            return participant_data
        else:
            return None  # Return None if participant not found

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_personal_stats_for_overall(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT student, logtime, exp, total_tasks_accepted, educational_events, entertainment, total_number_events FROM personal_stats")
        result = cursor.fetchall()
        if result:
            return result
        else:
            return None
    except sqlite3.Error as e:
        print(f"Error getting personal stats: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_active_students_by_exp(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT student, exp FROM participants WHERE exp > 0")
        participants_data = cursor.fetchall()

        if participants_data:
            return participants_data  
        else:
            return None  

    except sqlite3.Error as e:
        print(f"Error getting participant: {e}")
        return None
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    # init_table_personal_stats("tashkent", "data/participants/tashkent/personal_stats.db")
    # init_table_personal_stats("samarkand", "data/participants/samarkand/personal_stats.db")

    populate_tasks()

    # print(get_all_active_students_by_exp(f"data_{intensive_month_selected}/participants/tashkent/participants.db"))

    # init_table_participants("tashkent", "data/participants/tashkent/participants.db")
    # init_table_participants("samarkand", "data/participants/samarkand/participants.db")


import sqlite3
from db_modules.db_api import *

def update_student_exam_progress(db_path, student_username, exam, score):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE exams_progress
        SET {exam} = ?
        WHERE student_username = ?""", (score, student_username))
    print(f"Updated {exam} score for student {student_username} to {score}")
    conn.commit()
    conn.close()


def populate_students_exam_progress(db_path, students):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for student in students:
        cursor.execute("""
            INSERT OR IGNORE INTO exams_progress (student_username)
            VALUES (?)""", (student,))
        print(f"Inserted student {student} into the database")
    conn.commit()
    conn.close()




def sort_students_exam_progress(db_path, campus):
    students = get_all_active_students_by_exp(db_path)

    if not students:
        print("No students found in the database.")
        return None

    exams = {"E01D05": "1_week", "E02D12": "2_week", "E03D19": "3_week"}
    student_progress = {}

    # Create database and table if not exists
    conn = sqlite3.connect(f"data/tasks/{campus}/exams_progress.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT UNIQUE,
            E01D05 INTEGER,
            E02D12 INTEGER,
            E03D19 INTEGER,
            E04D26 INTEGER
        )
    """)
    conn.commit()

    # Populate students in the database
    populate_students_exam_progress(f"data/tasks/{campus}/exams_progress.db", [student[0] for student in students])

    for exam, week in exams.items():
        for student in students:
            student_username = student[0]
            if os.path.exists(f"data/tasks/{campus}/{week}/{exam}/{exam}.db"):
                result = get_student_task_result(f"data/tasks/{campus}/{week}/{exam}/{exam}.db", student_username)
                if result is not None:
                    final_score = result['final_score']
                    if student_username not in student_progress:
                        student_progress[student_username] = {}
                    student_progress[student_username][exam] = final_score
                    print(f"{exam} final score for student {student_username} is {final_score}")

    for student, scores in student_progress.items():
        for exam, score in scores.items():
            update_student_exam_progress(f"data/tasks/{campus}/exams_progress.db", student, exam, score)

    conn.close()


def sort_personal_stats(db_path, campus, target_student):

    if check_being_updated(f"../api/data/participants_to_read/overall.db", campus) == 1:
        print("being updated")
        return "being updated"

    students = get_all_active_students_personal_stats(db_path)

    if not students:
        print("No students found in the database.")
        return None

    # Sort by different criteria
    sorted_students_logtime = sorted(students, key=lambda x: x[1], reverse=True)
    sorted_students_tasks = sorted(students, key=lambda x: x[3], reverse=True)
    sorted_students_edu_events = sorted(students, key=lambda x: x[4], reverse=True)
    sorted_students_ent_events = sorted(students, key=lambda x: x[5], reverse=True)
    sorted_students_total_events = sorted(students, key=lambda x: x[6], reverse=True)

    results = {}  # Store all the results

    # Process each sorted list
    for sorted_list, key_name in [
        (sorted_students_logtime, "logtime"),
        (sorted_students_tasks, "tasks"),
        (sorted_students_edu_events, "edu_events"),
        (sorted_students_ent_events, "ent_events"),
        (sorted_students_total_events, "total_events"),
    ]:
        try:
            student_index = next(i for i, (name, *rest) in enumerate(sorted_list) if name == target_student)
            student_rank = student_index + 1

        except StopIteration:
            return None

        # Calculate percentages
        target_value = None  # Generic name for the value we're comparing
        for name, value, *_ in sorted_list:  # Find target value in the current sorted list
            if name == target_student:
                target_value = value
                break

        if target_value is None:
            raise Exception(f"Ученик {target_student} не найден в списке.")

        percent = (student_rank / len(sorted_list)) * 100

        percent_less = float()
        percent_more = float()
        if percent < 50.0:
            percent_more = percent
            percent_less = 100.00 - percent
        elif percent > 50.0:
            percent_less = 100.00 - percent
            percent_more = percent
            

        

        results[key_name] = {  # Store results for each key
            "rank": student_rank,
            "percent_more": percent_more,
            "percent_less": percent_less,
            "total_students": len(sorted_list),
        }

    return results






def sort_task_data(filename):
    try:
        if not os.path.exists(filename) :
            raise Exception(f'There is no task file in this folder! {filename}')
        
        students = get_all_students_task_results(filename)

        registered = [students[i] for i in range(len(students)) if students[i]['status'] == 'REGISTERED']
        passed_students = [students[i] for i in range(len(students)) if students[i]['status'] == 'ACCEPTED']
        failed_students = [students[i] for i in range(len(students)) if students[i]['status'] == 'FAILED']
        in_progress = [students[i] for i in range(len(students)) if students[i]['status'] == 'IN_PROGRESS']
        in_reviews = [students[i] for i in range(len(students)) if students[i]['status'] == 'IN_REVIEWS']

        scored_didnt_pass = list()

        for student in students:
            score = student['final_score']
            status = student['status']
            if score != '0' and score != None:
                if int(score) < 50 and status != 'ACCEPTED':
                    scored_didnt_pass.append(student)

        scored_didnt_pass_result = sorted(scored_didnt_pass, key=lambda item: int(item['final_score']), reverse=True)

        scored_hundred_percent = [student for student in passed_students if int(student['final_score']) >= 100]

        acceptance_rate = (len(passed_students) / len(students)) * 100

        return passed_students, failed_students, scored_didnt_pass_result, scored_hundred_percent, len(students), acceptance_rate, in_progress, in_reviews, registered
    except Exception:
        raise Exception




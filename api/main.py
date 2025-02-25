#!/../venv/bin/python3
import os
import sys

sys.path.append("..")

import requests
import json
import time
from db_modules.db_api import * 
from configs.config_api import *
import sqlite3
import matplotlib.pyplot as plt
from report_helpers.report_helper import _process_report_type
from sorting_data.sort_helper import *
from db_modules.db_api import *
from configs.config_bot import *
from report_helpers.report_helper import *


def get_api_token():
    data = {
        'client_id':'s21-open-api',
        'username':'glassole',
        'password':'Sh7757723!',
        'grant_type':'password'
    }

    response_api = requests.post(AUTH_URL, data=data)

    with open("token.txt", "w+") as file:
        file.writelines(response_api.text)

    return response_api.json()['access_token']


def get_file_token():
    with open("token.txt", "r+") as file:
        line = file.readline()

    return json.loads(line)['access_token']

    

def get_list_of_campuses_api(access_token):
    HEADERS = {
    'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get(BASE_URL.format('/campuses'), headers=HEADERS)

    if response.status_code == 200:
        _return_value = response.text

        campuses_json = json.loads(_return_value)['campuses']

        with open(f"data_{intensive_month_selected}/campuses/campuses.csv", "w+") as file:
            file.write("id,shortName,fullName\n")
            for i in range(len(campuses_json)):
                id = campuses_json[i]['id']
                shortName = campuses_json[i]['shortName']
                fullName = campuses_json[i]['fullName']
                file.write(f"{id},{shortName},{fullName}\n")
    else:
        raise Exception(f"There was an error during parsing from the api {BASE_URL.BASE_URL.format('/campuses')}")


def get_specific_campus_id(campus_name, intensive_month_selected):
    _return_value = "None"
    with open(f"data_{intensive_month_selected}/campuses/campuses.csv", "r+") as file:
        line = file.readline()
        campuses = list()
        while line:
            line = file.readline()
            campuses.append(line.strip())

    for school in campuses[:len(campuses) - 1]:
        shortname = school.split(',')[1]
        if shortname.split()[0] == '21':
            if shortname.split()[1] == campus_name.capitalize():
                _return_value = school.split(',')[0]
                break

    if _return_value == "None":
        raise Exception(f"There is no campus named {campus_name} among all the campuses")

    return _return_value


def get_coalitions_api(access_token, campus_id, campus_name):
    HEADERS = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(BASE_URL.format(f"/campuses/{campus_id}/coalitions"), headers=HEADERS)

    if response.status_code == 200:
        coalitions = json.loads(response.text)['coalitions']
        intensiv_tribe_names = ['AYIQ', 'JAYRON', 'LAYLAK', 'QOPLON'] if campus_name == 'tashkent' else ['BO\'RI', 'HUMO', 'LOCHIN', 'TUYA']
        
        intensiv_coalitions = [c for c in coalitions if c['name'] in intensiv_tribe_names]
        main_education_coalitions = [c for c in coalitions if c['name'] not in intensiv_tribe_names]

        def write_to_file(filename, data):
            with open(filename, 'w+') as file:
                file.write('coalitionId,name\n')
                for coalition in data:
                    file.write(f"{coalition['coalitionId']},{coalition['name']}\n")

        write_to_file(f'data_{intensive_month_selected}/coalitions/{campus_name}/intensiv_coalitions.csv', intensiv_coalitions)
        write_to_file(f'data_{intensive_month_selected}/coalitions/{campus_name}/main_education_coalitions.csv', main_education_coalitions)


def get_all_intensiv_participants_api(access_token):
    def fetch_participants(campus):
        coalition_ids = []
        participants = []

        with open(f'data_{intensive_month_selected}/coalitions/{campus}/intensiv_coalitions.csv', 'r') as file:
            coalition_ids = [line.split(',')[0] for line in file.readlines()[1:]]

        for coalition_id in coalition_ids:
            HEADERS = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(BASE_URL.format(f"/coalitions/{coalition_id}/participants?limit=1000&offset=0"), headers=HEADERS)
            if response.status_code == 200:
                participants.extend(json.loads(response.text)['participants'])
                time.sleep(0.5)
            else:
                raise Exception(f"Error fetching participants: {response.status_code}\n{response.text}")

        with open(f'data_{intensive_month_selected}/participants/{campus}/intensiv_participants.csv', 'w') as file:
            file.write('USERNAME\n')
            for username in participants:
                file.write(f'{username}\n')

    fetch_participants('tashkent')
    fetch_participants('samarkand')


def get_info_participant_project_percent(access_token, username, projectId):
    _return = str()
    try: 
        HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
        }

        response = requests.get(BASE_URL.format(f"/participants/{username}/projects/{projectId}"), headers=HEADERS)

        _return = json.loads(response)['finalPercentage']

    except Exception:
        raise Exception

    return _return

def get_specific_project_complеtion_info(access_token, project_id, week, project_name, intensive_month_selected):
    HEADERS = {'Authorization': f'Bearer {access_token}'}

    def process_students(db_path, students):
        if not os.path.exists(db_path):
            init_table_for_task(db_path)
        populate_task_results(db_path, students)

        incompleted_students = []
        for status in ["NULL", "REGISTERED", "IN_PROGRESS", "IN_REVIEWS"]:
            incompleted_students.extend(get_student_task_result_by_status(db_path, status))

        for student in incompleted_students:
            response = requests.get(BASE_URL.format(f"/participants/{student}/projects/{project_id}"), headers=HEADERS)
            if response.status_code == 200:
                response_json = response.json()
                update_task_result(db_path, student, response_json['title'], response_json['type'], response_json['status'], response_json['finalPercentage'])
                print(f"{student},{response_json['title']},{response_json['type']},{response_json['status']},{response_json['finalPercentage']}")
                time.sleep(1)
            else:
                raise Exception(f"Error parsing scores from API!\n{response.status_code}\n{response.text}\nStudent: {student}")

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/participants.db") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/participants.db"):
        process_students(f"data_{intensive_month_selected}/tasks/tashkent/{week}/{project_name}/{project_name}.db", get_all_students(f"data_{intensive_month_selected}/participants/tashkent/participants.db"))
        process_students(f"data_{intensive_month_selected}/tasks/samarkand/{week}/{project_name}/{project_name}.db", get_all_students(f"data_{intensive_month_selected}/participants/samarkand/participants.db"))


def parse_student_info(access_token, intensive_month_selected):
    HEADERS = {'Authorization': f'Bearer {access_token}'}

    def fetch_students(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()[1:]]

    def update_students(campus, students):
        db_path = f"data_{intensive_month_selected}/participants/{campus}/participants.db"
        last_parsed = get_last_parced_student(db_path)
        if last_parsed in students:
            students = students[students.index(last_parsed):]

        for i, student in enumerate(students):
            response_basic_info = requests.get(BASE_URL.format(f"/participants/{student}"), headers=HEADERS)
            response_logtime = requests.get(BASE_URL.format(f"/participants/{student}/logtime?date={date_to_use}"), headers=HEADERS)
            if response_basic_info.status_code == 200 and response_logtime.status_code == 200:
                logtime = float(response_logtime.text)
                info = response_basic_info.json()
                update_participant(db_path, student, logtime, info['level'], info['expValue'], info['expToNextLevel'])
                set_last_parced_student(db_path, student, 1)
                if i > 0:
                    set_last_parced_student(db_path, students[i - 1], 0)
                time.sleep(1)

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv"):
        date_to_use = max(datetime.date.today() - datetime.timedelta(weeks=1), datetime.date(2025, 1, 27))
        tashkent_students = fetch_students(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv")
        samarkand_students = fetch_students(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv")
        update_students("tashkent", tashkent_students)
        update_students("samarkand", samarkand_students)
        

def parse_personal_stats(access_token, intensive_month_selected):
    HEADERS = {'Authorization': f'Bearer {access_token}'}

    def fetch_students(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()[1:]]

    def update_stats(campus, students):
        db_path = f"data_{intensive_month_selected}/participants/{campus}/personal_stats.db"
        last_parced = get_last_parced_student_personal_stats(db_path)
        if last_parced in students:
            students = students[students.index(last_parced):]

        for i, student in enumerate(students):
            response_basic_info = requests.get(BASE_URL.format(f"/participants/{student}"), headers=HEADERS)
            response_accepted_projects = requests.get(BASE_URL.format(f"/participants/{student}/projects?limit=50&offset=0&status=ACCEPTED"), headers=HEADERS)
            response_logtime = requests.get(BASE_URL.format(f"/participants/{student}/logtime?date={date_to_use}"), headers=HEADERS)
            response_badges = requests.get(BASE_URL.format(f"/participants/{student}/badges"), headers=HEADERS)

            if all(response.status_code == 200 for response in [response_basic_info, response_accepted_projects, response_logtime, response_badges]):
                info = response_basic_info.json()
                logtime = float(response_logtime.text)
                total_num_projects_accepted = len(response_accepted_projects.json()["projects"])
                badges = response_badges.json()["badges"]
                educational_events = len([badge for badge in badges if badge["name"] == "Educational event"])
                entertainment_events = len([badge for badge in badges if badge["name"] == "Entertainment event"])
                total_num_events = educational_events + entertainment_events

                update_personal_stats(campus, db_path, student, logtime, info['expValue'], total_num_projects_accepted, educational_events, entertainment_events, total_num_events)
                set_last_parced_student_personal_stats(campus, db_path, student, 1)
                if i > 0:
                    set_last_parced_student_personal_stats(campus, db_path, students[i - 1], 0)
                print(f"{student}, {logtime}, {info['expValue']}, {total_num_projects_accepted}, {educational_events}, {entertainment_events}, {total_num_events}")
                time.sleep(1)

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv"):
        date_to_use = max(datetime.date.today() - datetime.timedelta(weeks=1), datetime.date(2025, 1, 27))
        tashkent_students = fetch_students(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv")
        samarkand_students = fetch_students(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv")
        update_stats("tashkent", tashkent_students)
        update_stats("samarkand", samarkand_students)



def update_read_databases():
    def update_participants(campus):
        students = get_all_participants_for_overall(f"data_{intensive_month_selected}/participants/{campus}/participants.db")
        set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", campus, 1)
        for student in students:
            update_participant(
                db_path=f"data_{intensive_month_selected}/participants_to_read/{campus}/participants.db",
                student=student[0], logtime=student[1], level=student[2], exp=student[3], exp_to_next_level=student[4]
            )
            print(f"The student {student[0]} has been updated in participants in {campus.capitalize()}")
        set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", campus, 0)

    def update_personal_stats_db(campus):
        stats = get_all_personal_stats_for_overall(f"data_{intensive_month_selected}/participants/{campus}/personal_stats.db")
        set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", campus, 1)
        for student in stats:
            update_personal_stats(
                campus=campus,
                db_path=f"data_{intensive_month_selected}/participants_to_read/{campus}/personal_stats.db",
                student=student[0], logtime=student[1], exp=student[2], total_tasks_accepted=student[3],
                educational_events=student[4], entertainment=student[5], total_number_events=student[6]
            )
            print(f"The student {student[0]} has been updated in personal_stats in {campus.capitalize()}")
        set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", campus, 0)

    for campus in ["tashkent", "samarkand"]:
        update_participants(campus)
        update_personal_stats_db(campus)


def plot_exam_progress(campus, intensive_month_selected):
    db_path = f"data_{intensive_month_selected}/tasks/{campus}/exams_progress.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT student_username, E01D05, E02D12, E03D19, E04D26 FROM exams_progress")
    data = cursor.fetchall()

    conn.close()

    unstable_students = []
    most_progress_students = []
    biggest_fall_students = []

    for student, e01d05, e02d12, e03d19, e04d26 in data:
        scores = [e01d05, e02d12, e03d19, e04d26]
        if None in scores:
            continue

        progress = e04d26 - e01d05
        fall = e01d05 - e04d26
        instability = max(scores) - min(scores)

        unstable_students.append((student, instability, scores))
        most_progress_students.append((student, progress, scores))
        biggest_fall_students.append((student, fall, scores))

    unstable_students = sorted(unstable_students, key=lambda x: x[1], reverse=True)[:5]
    most_progress_students = sorted(most_progress_students, key=lambda x: x[1], reverse=True)[:5]
    biggest_fall_students = sorted(biggest_fall_students, key=lambda x: x[1], reverse=True)[:5]

    def plot_students(students, title, filename):
        for student, _, scores in students:
            exams = ["E01D05", "E02D12", "E03D19", "E04D26"]
            plt.plot(exams, scores, marker='o', label=student)

        plt.xlabel('Exams')
        plt.ylabel('Scores')
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.savefig(f"data_{intensive_month_selected}/images/{filename}.png")
        plt.clf()

    plot_students(unstable_students, f'Most Unstable Students in Exam Scores', f"{campus}_unstable_students")
    plot_students(most_progress_students, f'Students with Most Progress in Exam Scores', f"{campus}_most_progress_students")
    plot_students(biggest_fall_students, f'Students with Biggest Fall in Exam Scores', f"{campus}_biggest_fall_students")




def update_posts_db(task, intensive_month_selected):
    campuses = ["tashkent", "samarkand"]
    task_id, _ = INTENSIVE[task]

    titles = {
        'english': {
            'passed': "List of students who passed the project:",
            'hundred': "List of students who scored 100%:",
            'didnt_pass': "List of students who didn't pass the project:",
            'in_progress': "List of students working on the project:",
            'in_reviews': "List of students waiting for review:",
            'registered': "List of registered students:"
        },
        'russian': {
            'passed': "Список учеников, сдавших проект:",
            'hundred': "Список учеников, набравших 100%:",
            'didnt_pass': "Список учеников, не сдавших проект:",
            'in_progress': "Список учеников, выполняющих проект:",
            'in_reviews': "Список учеников, ожидающих проверку:",
            'registered': "Список зарегистрированных учеников:"
        },
        'uzbek': {
            'passed': "Loyiha topshirgan talabalar ro'yxati:",
            'hundred': "100% ball olgan talabalar ro'yxati:",
            'didnt_pass': "Loyiha topshirmagan talabalar ro'yxati:",
            'in_progress': "Loyiha ustida ishlayotgan talabalar ro'yxati:",
            'in_reviews': "Tekshiruvni kutayotgan talabalar ro'yxati:",
            'registered': "Ro'yxatdan o'tgan talabalar ro'yxati:"
        }
    }

    for campus in campuses:
        report = make_report(task, "russian", campus, f"data_{intensive_month_selected}/tasks.db", 1)
        for language in ["russian", "english", "uzbek"]:
            for report_type in ['passed', 'hundred', 'scored_didnt_pass', 'in_progress', 'in_reviews', 'registered']:
                students = report.get(f'scored_{report_type}' if report_type != 'passed' else 'passed_students')
                if students:
                    campus_language_specified = "Ташкент" if campus == "tashkent" and language == "russian" else campus.capitalize()
                    post_url = create_telegraph_post(
                        TELEGRAPH_TOKEN, f"{titles[language][report_type]} ({task}) {campus_language_specified}",
                        make_content(students, task_id, language))['result']['url']
                    create_post(task, post_url, f'url_{report_type}_{language}_{campus}')
                    time.sleep(1)



def get_needed_data_stats(campus, intensive_month_selected):
    db_path = f"data_{intensive_month_selected}/participants/{campus}/personal_stats.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    queries = {
        "count_zero_educational_events": "SELECT COUNT(*) FROM personal_stats WHERE educational_events = 0 AND logtime > 0",
        "count_zero_to_five_educational_events": "SELECT COUNT(*) FROM personal_stats WHERE educational_events > 0 AND educational_events <= 5 AND logtime > 0",
        "count_five_to_ten_educational_events": "SELECT COUNT(*) FROM personal_stats WHERE educational_events > 5 AND educational_events <= 10 AND logtime > 0",
        "count_more_than_ten_educational_events": "SELECT COUNT(*) FROM personal_stats WHERE educational_events > 10 AND logtime > 0",
        "count_zero_entertainment_events": "SELECT COUNT(*) FROM personal_stats WHERE entertainment = 0 AND logtime > 0",
        "count_zero_to_five_entertainment_events": "SELECT COUNT(*) FROM personal_stats WHERE entertainment > 0 AND entertainment <= 5 AND logtime > 0",
        "count_five_to_ten_entertainment_events": "SELECT COUNT(*) FROM personal_stats WHERE entertainment > 5 AND entertainment <= 10 AND logtime > 0",
        "count_more_than_ten_entertainment_events": "SELECT COUNT(*) FROM personal_stats WHERE entertainment > 10 AND logtime > 0",
        "average_total_events": "SELECT AVG(total_number_events) FROM personal_stats WHERE logtime > 0",
        "count_zero_events": "SELECT COUNT(*) FROM personal_stats WHERE total_number_events = 0 AND logtime > 0",
        "count_zero_to_five_events": "SELECT COUNT(*) FROM personal_stats WHERE total_number_events > 0 AND total_number_events <= 5 AND logtime > 0",
        "count_five_to_ten_events": "SELECT COUNT(*) FROM personal_stats WHERE total_number_events > 5 AND total_number_events <= 10 AND logtime > 0",
        "count_more_than_ten_events": "SELECT COUNT(*) FROM personal_stats WHERE total_number_events > 10 AND logtime > 0",
        "count_zero_tasks": "SELECT COUNT(*) FROM personal_stats WHERE total_tasks_accepted = 0 AND logtime > 0",
        "count_zero_to_five_tasks": "SELECT COUNT(*) FROM personal_stats WHERE total_tasks_accepted > 0 AND total_tasks_accepted <= 5 AND logtime > 0",
        "count_more_than_ten_tasks": "SELECT COUNT(*) FROM personal_stats WHERE total_tasks_accepted > 10 AND logtime > 0",
        "count_zero_to_five_logtime": "SELECT COUNT(*) FROM personal_stats WHERE logtime > 0 AND logtime <= 5",
        "count_five_to_ten_logtime": "SELECT COUNT(*) FROM personal_stats WHERE logtime > 5 AND logtime <= 10",
        "count_more_than_ten_logtime": "SELECT COUNT(*) FROM personal_stats WHERE logtime > 10"
    }

    results = {key: cursor.execute(query).fetchone()[0] for key, query in queries.items()}
    conn.close()


    def plot_pie_chart(data, labels, title, filename):
        plt.figure(figsize=(8, 8))
        plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(title)
        plt.axis('equal')
        plt.savefig(f"data_{intensive_month_selected}/images/{filename}.png")
        plt.clf()


    educational_events_data = [
        results["count_zero_educational_events"],
        results["count_zero_to_five_educational_events"],
        results["count_five_to_ten_educational_events"],
        results["count_more_than_ten_educational_events"]
    ]
    educational_events_labels = ["0 events", "1-5 events", "6-10 events", ">10 events"]
    plot_pie_chart(educational_events_data, educational_events_labels, f"{campus.capitalize()} Educational Events", f"{campus}_educational_events")


    entertainment_events_data = [
        results["count_zero_entertainment_events"],
        results["count_zero_to_five_entertainment_events"],
        results["count_five_to_ten_entertainment_events"],
        results["count_more_than_ten_entertainment_events"]
    ]
    entertainment_events_labels = ["0 events", "1-5 events", "6-10 events", ">10 events"]
    plot_pie_chart(entertainment_events_data, entertainment_events_labels, f"{campus.capitalize()} Entertainment Events", f"{campus}_entertainment_events")


    total_events_data = [
        results["count_zero_events"],
        results["count_zero_to_five_events"],
        results["count_five_to_ten_events"],
        results["count_more_than_ten_events"]
    ]
    total_events_labels = ["0 events", "1-5 events", "6-10 events", ">10 events"]
    plot_pie_chart(total_events_data, total_events_labels, f"{campus.capitalize()} Total Events", f"{campus}_total_events")


    total_tasks_data = [
        results["count_zero_tasks"],
        results["count_zero_to_five_tasks"],
        results["count_more_than_ten_tasks"]
    ]
    total_tasks_labels = ["0 tasks", "1-5 tasks", ">10 tasks"]
    plot_pie_chart(total_tasks_data, total_tasks_labels, f"{campus.capitalize()} Total Tasks", f"{campus}_total_tasks")


    logtime_data = [
        results["count_zero_to_five_logtime"],
        results["count_five_to_ten_logtime"],
        results["count_more_than_ten_logtime"]
    ]
    logtime_labels = ["0-5 hours", "6-10 hours", ">10 hours"]
    plot_pie_chart(logtime_data, logtime_labels, f"{campus.capitalize()} Logtime", f"{campus}_logtime")

    return results



def main():
    if len(sys.argv) == 3:
        if sys.argv[2] not in INTENSIVE_MONTHS:
            raise Exception(f"The entered month is not among the intensive months")
        
        intensive_month_selected = sys.argv[2]

        if sys.argv[1] == "parse_students":
            get_api_token()
            token = get_file_token()

            parse_student_info(token, intensive_month_selected)
            parse_personal_stats(token, intensive_month_selected)
            update_read_databases()

        elif sys.argv[1] == "sum_up":
            stats_tashkent = get_needed_data_stats("tashkent", intensive_month_selected)
            stats_samarkand = get_needed_data_stats("samarkand", intensive_month_selected)

            print("Tashkent Stats:")
            for key, value in stats_tashkent.items():
                print(f"{key}: {value}\n")

            print("\n\nSamarkand Stats:")
            for key, value in stats_samarkand.items():
                print(f"{key}: {value}\n")


        elif sys.argv[1] == "parse_exam_progress":
        
            sort_students_exam_progress(f"data_{intensive_month_selected}/participants/tashkent/participants.db", "tashkent")
            sort_students_exam_progress(f"data_{intensive_month_selected}/participants/samarkand/participants.db", "samarkand")
            plot_exam_progress("tashkent", intensive_month_selected)
            plot_exam_progress("samarkand", intensive_month_selected)

        if sys.argv[1] not in ("parse_students", "parse_exam_progress"):
            if sys.argv[1] not in INTENSIVE:
                raise Exception(f"The entered task is not among the intensive tasks")

            task = sys.argv[1]

            update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=1)

            get_api_token()
            token = get_file_token()
        
            project_id, week = INTENSIVE[f'{task}']

            if not os.path.exists(f'data_{intensive_month_selected}/campuses/campuses.csv'):
                get_list_of_campuses_api(token)
            
            tashkent_id = get_specific_campus_id("tashkent", intensive_month_selected)
            samarkand_id = get_specific_campus_id("samarkand", intensive_month_selected)
                

            if not os.path.exists(f'data_{intensive_month_selected}/coalitions/tashkent/intensiv_coalitions.csv') or not os.path.exists(f'data_{intensive_month_selected}/coalitions/samarkand/intensiv_coalitions.csv') :
                get_coalitions_api(token, tashkent_id, 'tashkent')
                get_coalitions_api(token, samarkand_id, 'samarkand')

            if not os.path.exists(f'data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv') or not os.path.exists(f'data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv'):
                get_all_intensiv_participants_api(token)


            get_specific_project_complеtion_info(token, str(project_id), week, task, intensive_month_selected)
            update_posts_db(task, intensive_month_selected)

            update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=0)





if __name__ == '__main__':
    main()
import sys

sys.path.append("..")

import os
import requests
import time
import json
import datetime
from configs.config_api import INTENSIVE # type: ignore
from main import get_api_token, get_file_token, get_list_of_campuses_api, get_specific_campus_id, get_coalitions_api, get_specific_project_complеtion_info, parse_personal_stats
from configs.config_api import BASE_URL
from db_modules.db_api import *
import sqlite3



def get_old_intensiv_participants_api(access_token, intensive_month_selected):
    all_participants = list()
    intensiv_coalitions_ids = list()

    for campus in ["tashkent", "samarkand"]:
        print(f"{campus.capitalize()} is being parsed right now!")
        with open(f'data_{intensive_month_selected}/coalitions/{campus}/main_education_coalitions.csv', 'r+') as file:
            lines = file.readlines()
            intensiv_coalitions_ids = [id.strip().split(",")[0] for id in lines[1:-1]]


        for i in range(len(intensiv_coalitions_ids)):
            try: 
                HEADERS = {
                'Authorization': 'Bearer {}'.format(access_token),
                }

                print(f"Coalition {intensiv_coalitions_ids[i]}")

                response_participants = requests.get(BASE_URL.format(f"/coalitions/{intensiv_coalitions_ids[i]}/participants?limit=1000&offset=0"), headers=HEADERS)

                if response_participants.status_code == 200:
                    for student in json.loads(response_participants.text)['participants']:
                        response_first_participant_task = requests.get(BASE_URL.format(f"/participants/{student}/projects/19153"), headers=HEADERS)

                        if response_first_participant_task.status_code == 200:
                            response_first_participant_task_json = json.loads(response_first_participant_task.text)

                            completion_date_time = response_first_participant_task_json['completionDateTime']
                            try:
                                completion_date = datetime.datetime.strptime(completion_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                            except ValueError:
                                try:
                                    completion_date = datetime.datetime.strptime(completion_date_time, "%Y-%m-%dT%H:%M:%SZ")
                                except ValueError as e:
                                    raise Exception(f"Failed to parse date: {completion_date_time}") from e

                            num_value_intensive_month = 9 if intensive_month_selected == "september" else 11

                            if completion_date.month in [9, 11] and completion_date.month == num_value_intensive_month:  
                                all_participants.append(student)
                                print(student)
                                time.sleep(1)
                else:
                    raise Exception(f"There was a mistake while parcing participants from the API\n{response_participants.status_code}\n{response_participants.text}")
            except Exception:
                raise Exception
            
        with open(f'data_{intensive_month_selected}/participants/{campus}/main_education_participants.csv', 'w+') as file:
            file.write('USERNAME\n')
            for username in all_participants:
                file.write(f'{username}\n')


# def sort_samarkand_participants(access_token, task, intensive_month_selected):
#     students = list()

#     with open(f'data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv', 'r+') as file:
#         line = file.readline()
#         while line:
#             line = file.readline()
#             students.append(line.strip())

#     new_studetns = students[:-1]

#     students_samarkand = list()

#     for student in new_studetns:
#         HEADERS = {
#             'Authorization': 'Bearer {}'.format(access_token),
#         }

#         task_id, _ = INTENSIVE[task]

#         response = requests.get(BASE_URL.format(f"/participants/{student}/projects/{task_id}"), headers=HEADERS)
        
#         if response.status_code == 200:
#             response_json = json.loads(response.text)

#             completion_date_time = response_json['completionDateTime']

#             completion_date = datetime.datetime.strptime(completion_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")

#             if completion_date >= datetime.datetime(2024, 9, 20):
#                 students_samarkand.append(student)
#                 print(f"{student}: {completion_date_time}")
#             else:
#                 print(f"The student {student} was not from the september or november intensives")

#             time.sleep(1)

#     with open(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv", 'w+') as file:
#         file.write('USERNAME\n')
#         for student in students_samarkand:
#             file.write(f'{student}\n')


def parse_old_student_info(access_token, intensive_month_selected):
    HEADERS = {'Authorization': 'Bearer {}'.format(access_token)}

    def parse_city(city):
        students = []
        with open(f"data_{intensive_month_selected}/participants/{city}/main_education_participants.csv", 'r') as file:
            students = [line.strip() for line in file.readlines()[1:-1]]
        populate_participants(f"data_{intensive_month_selected}/participants/{city}/participants.db", city, students)
        return students

    def update_students(city, students, date_to_use):
        db_path = f"data_{intensive_month_selected}/participants/{city}/participants.db"
        last_parced_student = get_last_parced_student(db_path)
        if last_parced_student and last_parced_student in students:
            students = students[students.index(last_parced_student):]

        for i, student in enumerate(students):
            response_basic_info = requests.get(BASE_URL.format(f"/participants/{student}"), headers=HEADERS)
            time.sleep(0.5)
            response_logtime = requests.get(BASE_URL.format(f"/participants/{student}/logtime?date={date_to_use}"), headers=HEADERS)
            if response_logtime.status_code == 200 and response_basic_info.status_code == 200:
                logtime = float(response_logtime.text)
                response_basic_info_json = response_basic_info.json()
                update_participant(db_path, student, logtime=logtime, level=response_basic_info_json['level'], exp=response_basic_info_json['expValue'], exp_to_next_level=response_basic_info_json['expToNextLevel'])
                print(f"{student}, {logtime}, {response_basic_info_json['level']}, {response_basic_info_json['expValue']}, {response_basic_info_json['expToNextLevel']}")
                if i > 0:
                    set_last_parced_student(db_path, students[i - 1], 0)
                set_last_parced_student(db_path, student, 1)
                time.sleep(1)

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/main_education_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv"):
        datetime_date = datetime.date(2024, 9, 23) if intensive_month_selected == "september" else datetime.date(2024, 11, 5)
        
        date_to_use = max(datetime.date.today() - datetime.timedelta(weeks=1), datetime_date)
        for city in ["tashkent", "samarkand"]:
            students = parse_city(city)
            update_students(city, students, date_to_use)


def get_count_projects_accepted(access_token, participant):
    HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    num_tasks_accepted = 0
    for task, (id, _) in INTENSIVE.items():
        try:
            response = requests.get(BASE_URL.format(f"/participants/{participant}/projects/{id}"), headers=HEADERS)

            if response.status_code == 200:
                response_json = json.loads(response.text)
                status = response_json['status']
                print(f"{participant}, {task} = {status}")

                if status == "ACCEPTED":
                    num_tasks_accepted += 1
                time.sleep(1)
            else:
                raise Exception(f"There was a problem during parsing from API. {response.text}")
        except Exception:
            raise Exception(f"There was a problem during parsing from API. {response.text}")
    return num_tasks_accepted




def parse_old_students_personal_stats(access_token, intensive_month_selected):
    HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
    }
                                                                                   
    for city in ["tashkent", "samarkand"]:
        students = []
        if os.path.exists(f"data_{intensive_month_selected}/participants/{city}/main_education_participants.csv"):
            with open(f"data_{intensive_month_selected}/participants/{city}/main_education_participants.csv", 'r') as file:
                students = [line.strip() for line in file.readlines()[1:-1]]
            populate_personal_stats_old_participants(city, f"data_{intensive_month_selected}/participants/{city}/personal_stats.db", students)

        try:
            for city in ["tashkent", "samarkand"]:
                db_path = f"data_{intensive_month_selected}/participants/{city}/personal_stats.db"
                last_parced_student = get_last_parced_student_personal_stats(db_path)
                if last_parced_student and last_parced_student in students:
                    students = students[students.index(last_parced_student):]

                for i, participant in enumerate(students):
                    date_to_use = datetime.date(2024, 9, 23) if intensive_month_selected == "september" else datetime.date(2024, 11, 4)
                    response_logtime_first_week = requests.get(BASE_URL.format(f"/participants/{participant}/logtime?date={date_to_use}"), headers=HEADERS)
                    print(f"{participant}: response_logtime_first_week {response_logtime_first_week.text}")
                    time.sleep(1)
                    response_logtime_second_week = requests.get(BASE_URL.format(f"/participants/{participant}/logtime?date={date_to_use + datetime.timedelta(weeks=1)}"), headers=HEADERS)
                    print(f"response_logtime_second_week {response_logtime_second_week.text}")
                    time.sleep(1)
                    response_logtime_third_week = requests.get(BASE_URL.format(f"/participants/{participant}/logtime?date={date_to_use + datetime.timedelta(weeks=2)}"), headers=HEADERS)
                    print(f"response_logtime_third_week {response_logtime_third_week.text}")
                    time.sleep(1)
                    response_logtime_fourth_week = requests.get(BASE_URL.format(f"/participants/{participant}/logtime?date={date_to_use + datetime.timedelta(weeks=3)}"), headers=HEADERS)
                    print(f"response_logtime_fourth_week {response_logtime_fourth_week.text}")
                    time.sleep(1)
                    response_badges = requests.get(BASE_URL.format(f"/participants/{participant}/badges"), headers=HEADERS)
                    time.sleep(0.5)
                    response_exp = requests.get(BASE_URL.format(f"/participants/{participant}/experience-history?limit=500&offset=0"), headers=HEADERS)


                    if all(response.status_code == 200 for response in [response_logtime_first_week, response_logtime_second_week, response_logtime_third_week, response_logtime_fourth_week, response_badges, response_exp]):
                        total_num_projects_accepted = get_count_projects_accepted(access_token, participant)
                        logtime_first_week = float(response_logtime_first_week.text)
                        logtime_second_week = float(response_logtime_second_week.text)
                        logtime_third_week = float(response_logtime_third_week.text)
                        logtime_fourth_week = float(response_logtime_fourth_week.text)
                        badges = response_badges.json()["badges"]
                        educational_events = len([badge for badge in badges if badge["name"] == "Educational event"])
                        entertainment_events = len([badge for badge in badges if badge["name"] == "Entertainment event"])
                        total_num_events = educational_events + entertainment_events

                        respose_exp_json = json.loads(response_exp.text)
                        exp_value = 0
                        for exp in respose_exp_json['expHistory']:
                            accrual_date = exp['accrualDateTime']
                            try:
                                accrual_date_datetime = datetime.datetime.strptime(accrual_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                            except ValueError:
                                try:
                                    accrual_date_datetime = datetime.datetime.strptime(accrual_date, "%Y-%m-%dT%H:%M:%SZ")
                                except ValueError as e:
                                    raise Exception(f"Failed to parse date: {accrual_date}") from e
                                
                            months = [9, 10] if intensive_month_selected == "september" else [11, 12]

                            if accrual_date_datetime.month in months:
                                exp_value += exp['expValue']
                        

                        update_personal_stats_old_participants(city, db_path, participant, exp_value, logtime_first_week, logtime_second_week, logtime_third_week, logtime_fourth_week, total_num_projects_accepted, educational_events, entertainment_events, total_num_events)
                        if i > 0:
                            set_last_parced_student_personal_stats(city, db_path, students[i - 1], 0)
                        set_last_parced_student_personal_stats(city, db_path, participant, 1)
                        print(f"{participant}, {logtime_first_week}, {logtime_second_week}, {logtime_third_week}, {logtime_fourth_week}, {total_num_projects_accepted}, {educational_events}, {entertainment_events}, {total_num_events}")

                        time.sleep(1)

                set_all_last_parced("tashkent")
                set_all_last_parced("samarkand")
        except Exception as e:
            raise Exception(f"There was a problem during parsing from the api {e}")



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
    return results



def main():
    if len(sys.argv) == 3:
        get_api_token()
        token = get_file_token()

        intensive_month_selected = sys.argv[2]

        if sys.argv[1] == "parse_students":
            parse_old_student_info(token, intensive_month_selected)
            parse_old_students_personal_stats(token, intensive_month_selected)
        
        else:
            task = sys.argv[1]

            project_id, week = INTENSIVE[task]

            if not os.path.exists(f'data_{intensive_month_selected}/campuses/campuses.csv'):
                get_list_of_campuses_api(token)

            tashkent_id = get_specific_campus_id("tashkent", intensive_month_selected)
            samarkand_id = get_specific_campus_id("samarkand", intensive_month_selected)

            if not os.path.exists(f'data_{intensive_month_selected}/coalitions/tashkent/intensiv_coalitions.csv') or not os.path.exists(f'data_{intensive_month_selected}/coalitions/samarkand/intensiv_coalitions.csv') :
                get_coalitions_api(token, tashkent_id, 'tashkent')
                get_coalitions_api(token, samarkand_id, 'samarkand')

            if not os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/main_education_participants.csv") or not os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv"):
                get_old_intensiv_participants_api(token, intensive_month_selected)

            # if not os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv"):
            #     sort_samarkand_participants(token, task, intensive_month_selected)

            # get_specific_project_complеtion_info(token, str(project_id), week, task, intensive_month_selected)
        

# Сколько в среднем заданий сдало большинство прошедших






# Example usage:





# Сколько в среднем экзаменов сдало большинство прошедших



# Читеров поймано

# Топ-1 по лвлу за интенсив
# Топ-1 по среднему времени в кампусе за интенсив
# Топ-1 по количеству ивентов за интенсив

if __name__ == "__main__":
    main()


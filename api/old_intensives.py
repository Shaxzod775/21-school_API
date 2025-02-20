import sys

sys.path.append("..")

import os
import requests
import time
import json
import datetime
from configs.config_api import INTENSIVE # type: ignore
from main import get_api_token, get_file_token, get_list_of_campuses_api, get_specific_campus_id, get_coatlitions_api, get_specific_project_complеtion_info
from configs.config_api import BASE_URL
from db_modules.db_api import get_last_parced_student, set_last_parced_student, get_incompleted_participants, update_participant, populate_participants



def get_old_intensiv_participants_api(access_token, intensive_month_selected):
    all_participants_tashkent = list()
    tashkent_intensiv_coalitions_ids = list()

    #Tashkent
    with open(f'data_{intensive_month_selected}/coalitions/tashkent/main_education_coalitions.csv', 'r+') as file:
        line = file.readline()
        while line:
            line = file.readline()
            tashkent_intensiv_coalitions_ids.append(line.split(',')[0])

    new_intensiv_coalitions_ids = tashkent_intensiv_coalitions_ids[:-1]

    # print(new_intensiv_coalitions_ids)

    for i in range(len(new_intensiv_coalitions_ids)):
        try: 
            HEADERS = {
            'Authorization': 'Bearer {}'.format(access_token),
            }

            response = requests.get(BASE_URL.format(f"/coalitions/{new_intensiv_coalitions_ids[i]}/participants?limit=1000&offset=0"), headers=HEADERS)

            if response.status_code == 200:
                for student in json.loads(response.text)['participants']:
                    all_participants_tashkent.append(student)
                    print(student)
                    time.sleep(0.5)
            else:
                raise Exception(f"There was a mistake while parcing participants from the API\n{response.status_code}\n{response.text}")
        except Exception:
            raise Exception
        
    with open(f'data_{intensive_month_selected}/participants/tashkent/main_education_participants.csv', 'w+') as file:
        file.write('USERNAME\n')
        for username in all_participants_tashkent:
            file.write(f'{username}\n')


    #Samarkand

    samarkand_intensiv_coalitions_ids = list()
    all_participants_samarkand = list()

    with open(f'data_{intensive_month_selected}/coalitions/samarkand/main_education_coalitions.csv', 'r+') as file:
        line = file.readline()
        while line:
            line = file.readline()
            samarkand_intensiv_coalitions_ids.append(line.split(',')[0])

    new_samarkand_intensiv_coalitions_ids = samarkand_intensiv_coalitions_ids[:-1]

    for i in range(len(new_samarkand_intensiv_coalitions_ids)):
        time.sleep(0.5)
        try: 
            HEADERS = {
            'Authorization': 'Bearer {}'.format(access_token),
            }

            response = requests.get(BASE_URL.format(f"/coalitions/{new_samarkand_intensiv_coalitions_ids[i]}/participants?limit=1000&offset=0"), headers=HEADERS)

            if response.status_code == 200:
                for student in json.loads(response.text)['participants']:
                    all_participants_samarkand.append(student)
            else:
                raise Exception(f"There was a mistake while parcing participants from the API\n{response.status_code}\n{response.text}")
        except Exception:
            raise Exception
        
    with open(f'data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv', 'w+') as file_samarkand:
        file_samarkand.write('USERNAME\n')
        for username in all_participants_samarkand:
            file_samarkand.write(f'{username}\n')



def sort_samarkand_participants(access_token, task, intensive_month_selected):
    students = list()

    with open(f'data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv', 'r+') as file:
        line = file.readline()
        while line:
            line = file.readline()
            students.append(line.strip())

    new_studetns = students[:-1]

    students_samarkand = list()

    for student in new_studetns:
        HEADERS = {
            'Authorization': 'Bearer {}'.format(access_token),
        }

        task_id, _ = INTENSIVE[task]

        response = requests.get(BASE_URL.format(f"/participants/{student}/projects/{task_id}"), headers=HEADERS)
        
        if response.status_code == 200:
            response_json = json.loads(response.text)

            completion_date_time = response_json['completionDateTime']

            completion_date = datetime.datetime.strptime(completion_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")

            if completion_date >= datetime.datetime(2024, 9, 20):
                students_samarkand.append(student)
                print(f"{student}: {completion_date_time}")
            else:
                print(f"The student {student} was not from the september or november intensives")

            time.sleep(1)

    with open(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv", 'w+') as file:
        file.write('USERNAME\n')
        for student in students_samarkand:
            file.write(f'{student}\n')


def parse_old_student_info(access_token, intensive_month_selected):
    HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/main_education_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv"):
        students_tashkent = list()
        with open(f"data_{intensive_month_selected}/participants/tashkent/main_education_participants.csv", 'r') as file_tashkent:
            student = file_tashkent.readline()
            while student:
                student = file_tashkent.readline()
                students_tashkent.append(student.strip())

        new_students_tashkent = students_tashkent[:len(students_tashkent) - 1]
        tashkent_students_usernames = [student.strip() for student in new_students_tashkent]
        populate_participants("tashkent", tashkent_students_usernames)

        students_samarkand = list()
        with open(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv", 'r') as file_samarkand:
            student = file_samarkand.readline()
            while student:
                student = file_samarkand.readline()
                students_samarkand.append(student.strip())

        new_students_samarkand = students_samarkand[:len(students_samarkand) - 1]
        samarkand_students_usernames = [student.strip() for student in new_students_samarkand]
        populate_participants("samarkand", samarkand_students_usernames)


        try:
            intensive_start_date = datetime.date(2025, 1, 27)
            today = datetime.date.today()
            one_week_ago = today - datetime.timedelta(weeks=1)
            date_to_use = one_week_ago if one_week_ago - datetime.timedelta(weeks=1) > intensive_start_date else intensive_start_date

            incompleted_participants_tashkent = get_incompleted_participants("tashkent")

            if not incompleted_participants_tashkent:
                incompleted_participants_tashkent = tashkent_students_usernames

            db_path_tashkent = f"data_{intensive_month_selected}/participants/tashkent/participants.db"
            last_parced_student = get_last_parced_student(db_path_tashkent)
            if last_parced_student and last_parced_student in incompleted_participants_tashkent: 
                index = incompleted_participants_tashkent.index(last_parced_student)
                incompleted_participants_tashkent = incompleted_participants_tashkent[index:]

            print("Parsing participants info in Tashkent")
            for i in range(len(incompleted_participants_tashkent)):  
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_tashkent[i]}"), headers=HEADERS)
                time.sleep(0.5)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_tashkent[i]}/logtime?date={date_to_use}"), headers=HEADERS)

                print(f"Response for student {incompleted_participants_tashkent[i]} is {response_basic_info.status_code} and {response_logtime.status_code}")

                if response_logtime.status_code == 200 and response_basic_info.status_code == 200:
                    logtime = float(response_logtime.text)


                    response_basic_info_json = json.loads(response_basic_info.text)
                    level = response_basic_info_json['level']
                    exp_value = response_basic_info_json['expValue']
                    exp_to_next_level = response_basic_info_json['expToNextLevel']

                    db_path_tashkent
                    # Update the database
                    update_participant(db_path_tashkent, incompleted_participants_tashkent[i], logtime=logtime, level=level, exp=exp_value, exp_to_next_level=exp_to_next_level)
                    print(f"Student {incompleted_participants_tashkent[i]} has been updated in Tashkent")
                    if i > 0:
                        set_last_parced_student(db_path_tashkent, incompleted_participants_tashkent[i - 1], 0)
                    
                    set_last_parced_student(db_path_tashkent, incompleted_participants_tashkent[i], 1)
                    print(f'{incompleted_participants_tashkent[i]}, {logtime}, {level}, {exp_value}, {exp_to_next_level}')

                    time.sleep(1)

            incompleted_participants_samarkand = get_incompleted_participants("samarkand")

            if not incompleted_participants_samarkand:
                incompleted_participants_samarkand = samarkand_students_usernames


            db_path_samarkand = f"data_{intensive_month_selected}/participants/samarkand/participants.db"
            last_parced_student = get_last_parced_student(db_path_samarkand)

            if last_parced_student and last_parced_student in incompleted_participants_samarkand:  
                index = incompleted_participants_samarkand.index(last_parced_student)
                incompleted_participants_samarkand = incompleted_participants_samarkand[index:]

            print("Parsing participants info in Samarkand")
            for i in range(len(incompleted_participants_samarkand)):  
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_samarkand[i]}"), headers=HEADERS)
                time.sleep(0.5)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_samarkand[i]}/logtime?date={date_to_use}"), headers=HEADERS)

                if response_logtime.status_code == 200 and response_basic_info.status_code == 200:
                    logtime = float(response_logtime.text)

                    response_basic_info_json = json.loads(response_basic_info.text)
                    level = response_basic_info_json['level']
                    exp_value = response_basic_info_json['expValue']
                    exp_to_next_level = response_basic_info_json['expToNextLevel']

                    # Update the database
                    update_participant(db_path_samarkand, incompleted_participants_samarkand[i], logtime=logtime, level=level, exp=exp_value, exp_to_next_level=exp_to_next_level)
                    print(f"Student {incompleted_participants_tashkent[i]} has been updated in Samarkand")
                    if i > 0:
                        set_last_parced_student(db_path_samarkand, incompleted_participants_samarkand[i - 1], 0)

                    set_last_parced_student(db_path_samarkand, incompleted_participants_samarkand[i], 1)
                    print(f'{incompleted_participants_samarkand[i]}, {logtime}, {level}, {exp_value}, {exp_to_next_level}')

                    time.sleep(1)
            
            last_parced_student = get_last_parced_student(db_path_tashkent)
            if last_parced_student == incompleted_participants_tashkent[-1]:
                set_last_parced_student(db_path_tashkent, last_parced_student, 0)
            
            last_parced_student = get_last_parced_student(db_path_samarkand)
            if last_parced_student == incompleted_participants_samarkand[-1]:
                set_last_parced_student(db_path_samarkand, last_parced_student, 0)
            

        except Exception as e:
            raise Exception(f"There was a problem during parsing from the api {e}")




def main():
    if len(sys.argv) > 1:
        get_api_token()
        token = get_file_token()

        intensive_month_selected = "september_november"

        task = sys.argv[1]

        project_id, week = INTENSIVE[task]

        if not os.path.exists(f'data_{intensive_month_selected}/campuses/campuses.csv'):
            get_list_of_campuses_api(token)

        tashkent_id = get_specific_campus_id("tashkent", intensive_month_selected)
        samarkand_id = get_specific_campus_id("samarkand", intensive_month_selected)

        if not os.path.exists(f'data_{intensive_month_selected}/coalitions/tashkent/intensiv_coalitions.csv') or not os.path.exists(f'data_{intensive_month_selected}/coalitions/samarkand/intensiv_coalitions.csv') :
            get_coatlitions_api(token, tashkent_id, 'tashkent')
            get_coatlitions_api(token, samarkand_id, 'samarkand')

        if not os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/main_education_participants.csv") or not os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv"):
            get_old_intensiv_participants_api(token, intensive_month_selected)

        if not os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/main_education_participants.csv"):
            sort_samarkand_participants(token, task, intensive_month_selected)

        parse_old_student_info(token, intensive_month_selected)

        get_specific_project_complеtion_info(token, str(project_id), week, task, intensive_month_selected)


if __name__ == "__main__":
    main()

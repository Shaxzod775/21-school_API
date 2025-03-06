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


def get_coatlitions_api(access_token, campus_id, campus_name):
    HEADERS = {
    'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get(BASE_URL.format(f"/campuses/{campus_id}/coalitions"), headers=HEADERS)

    if response.status_code == 200:
        coalitions = json.loads(response.text)['coalitions']

        intensiv_tribe_names = ['AYIQ', 'JAYRON', 'LAYLAK', 'QOPLON']

        if campus_name == 'samarkand':
            intensiv_tribe_names = ['BO\'RI', 'HUMO', 'LOCHIN', 'TUYA']

        intensiv_coalitions = list()
        main_education_coalitions = list()
        for i in range(len(coalitions)):
            if coalitions[i]['name'] in intensiv_tribe_names:
                intensiv_coalitions.append(coalitions[i])
            else:
                main_education_coalitions.append(coalitions[i])

        with open(f'data_{intensive_month_selected}/coalitions/{campus_name}/intensiv_coalitions.csv', 'w+') as int_file:
            int_file.write('coalitionId,name\n')
            for i in range(len(intensiv_coalitions)):
                if i == (len(intensiv_coalitions)):
                    coalitionId, name = intensiv_coalitions[i]['coalitionId'], intensiv_coalitions[i]['name']
                    int_file.write(f'{coalitionId},{name}')
                coalitionId, name = intensiv_coalitions[i]['coalitionId'], intensiv_coalitions[i]['name']
                int_file.write(f'{coalitionId},{name}\n')

        
        with open(f'data_{intensive_month_selected}/coalitions/{campus_name}/main_education_coalitions.csv', 'w+') as int_file:
            int_file.write('coalitionId,name\n')
            for i in range(len(main_education_coalitions)):
                coalitionId, name = main_education_coalitions[i]['coalitionId'], main_education_coalitions[i]['name']
                int_file.write(f'{coalitionId},{name}\n')


def get_all_intensiv_participants_api(access_token):
    all_participants_tashkent = list()
    tashkent_intensiv_coalitions_ids = list()

    #Tashkent
    with open(f'data_{intensive_month_selected}/coalitions/tashkent/intensiv_coalitions.csv', 'r+') as file:
        line = file.readline()
        while line:
            line = file.readline()
            tashkent_intensiv_coalitions_ids.append(line.split(',')[0])

    new_intensiv_coalitions_ids = tashkent_intensiv_coalitions_ids[:-1]

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
        
    with open(f'data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv', 'w+') as file:
        file.write('USERNAME\n')
        for username in all_participants_tashkent:
            file.write(f'{username}\n')


    #Samarkand

    samarkand_intensiv_coalitions_ids = list()
    all_participants_samarkand = list()

    with open(f'data_{intensive_month_selected}/coalitions/samarkand/intensiv_coalitions.csv', 'r+') as file:
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
                    print(student)
            else:
                raise Exception(f"There was a mistake while parcing participants from the API\n{response.status_code}\n{response.text}")
        except Exception:
            raise Exception
        
    with open(f'data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv', 'w+') as file:
        file.write('USERNAME\n')
        for username in all_participants_samarkand:
            file.write(f'{username}\n')


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
        HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
        }

        if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/participants.db") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/participants.db"):
            db_path_tashkent = f"data_{intensive_month_selected}/tasks/tashkent/{week}/{project_name}/{project_name}.db"
            students_tashkent = get_all_students(f"data_{intensive_month_selected}/participants/tashkent/participants.db")

            if not os.path.exists(db_path_tashkent):
                init_table_for_task(db_path_tashkent)
            populate_task_results(db_path_tashkent, students_tashkent)
            

            db_path_samarkand = f"data_{intensive_month_selected}/tasks/samarkand/{week}/{project_name}/{project_name}.db"
            students_samarkand = get_all_students(f"data_{intensive_month_selected}/participants/samarkand/participants.db")

            if not os.path.exists(db_path_samarkand):
                init_table_for_task(db_path_samarkand)
            populate_task_results(db_path_samarkand, students_samarkand)

            
            incompleted_students_tashkent = list()
            null = get_student_task_result_by_status(db_path_tashkent, "NULL")
            # registered = get_student_task_result_by_status(db_path_tashkent, "REGISTERED")
            in_progress = get_student_task_result_by_status(db_path_tashkent, "IN_PROGRESS")
            in_reviews = get_student_task_result_by_status(db_path_tashkent, "IN_REVIEWS")

            if null:
                for student in null:
                    incompleted_students_tashkent.append(student)
            # elif registered:
            #     for student in registered:
            #         incompleted_students_tashkent.append(student)
            elif in_progress:
                for student in in_progress:
                    incompleted_students_tashkent.append(student)
            elif in_reviews:
                for student in in_reviews:
                    incompleted_students_tashkent.append(student)

            if incompleted_students_tashkent:
                for i in range(len(incompleted_students_tashkent)):
                        response = requests.get(BASE_URL.format(f"/participants/{incompleted_students_tashkent[i]}/projects/{project_id}"), headers=HEADERS)
                        if response.status_code == 200:
                            response_json = json.loads(response.text)
                            title = response_json['title']
                            type = response_json['type']
                            status = response_json['status']
                            final_percentage = response_json['finalPercentage']
                            task_updated = update_task_result(db_path=db_path_tashkent, student=incompleted_students_tashkent[i], title=title, type=type, status=status, final_score=final_percentage)
                            if task_updated:
                                print(f'{incompleted_students_tashkent[i]},{title},{type},{status},{final_percentage}')
                            time.sleep(1)
                        else:
                            raise Exception(f"There was a problem during parsing scores from the api!\n{response.status_code}\n{response.text}\nStudent username: {incompleted_students_tashkent[i]}")
            

            incompleted_students_samarkand = list()
            null = get_student_task_result_by_status(db_path_samarkand, "NULL")
            registered = get_student_task_result_by_status(db_path_samarkand, "REGISTERED")
            in_progress = get_student_task_result_by_status(db_path_samarkand, "IN_PROGRESS")
            in_reviews = get_student_task_result_by_status(db_path_samarkand, "IN_REVIEWS")

            if null:
                for student in null:
                    incompleted_students_samarkand.append(student)
            elif registered:
                for student in registered:
                    incompleted_students_samarkand.append(student)
            elif in_progress:
                for student in in_progress:
                    incompleted_students_samarkand.append(student)
            elif in_reviews:
                for student in in_reviews:
                    incompleted_students_samarkand.append(student)
            
            if incompleted_students_samarkand:
                for i in range(len(incompleted_students_samarkand)):
                        response = requests.get(BASE_URL.format(f"/participants/{incompleted_students_samarkand[i]}/projects/{project_id}"), headers=HEADERS)
                        if response.status_code == 200:
                            response_json = json.loads(response.text)
                            title = response_json['title']
                            type = response_json['type']
                            status = response_json['status']
                            final_percentage = response_json['finalPercentage']
                            update_task_result(db_path_samarkand, incompleted_students_samarkand[i], title, type, status, final_percentage)
                            print(f'{incompleted_students_samarkand[i]},{title},{type},{status},{final_percentage}')
                            time.sleep(1)
                        else:
                            raise Exception(f"There was a problem during parsing scores from the api!\n{response.status_code}\n{response.text}") 


def parse_student_info(access_token, intensive_month_selected):
    HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv"):
        students_tashkent = list()
        with open(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv", 'r') as file_tashkent:
            student = file_tashkent.readline()
            while student:
                student = file_tashkent.readline()
                students_tashkent.append(student.strip())

        new_students_tashkent = students_tashkent[:len(students_tashkent) - 1]
        tashkent_students_usernames = [student.strip() for student in new_students_tashkent]
        populate_participants(f"data_{intensive_month_selected}/participants/tashkent/participants.db","tashkent", tashkent_students_usernames)

        students_samarkand = list()
        with open(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv", 'r') as file_samarkand:
            student = file_samarkand.readline()
            while student:
                student = file_samarkand.readline()
                students_samarkand.append(student.strip())

        new_students_samarkand = students_samarkand[:len(students_samarkand) - 1]
        samarkand_students_usernames = [student.strip() for student in new_students_samarkand]
        populate_participants(f"data_{intensive_month_selected}/participants/samarkand/participants.db", "samarkand", samarkand_students_usernames)


        try:
            intensive_start_date = datetime.date(2025, 3, 3)
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
            for i in range(len(incompleted_participants_tashkent)):  # Iterate through students (usernames)
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_tashkent[i]}"), headers=HEADERS)
                time.sleep(0.5)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_tashkent[i]}/logtime?date={date_to_use}"), headers=HEADERS)

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

                    update_participant(db_path_samarkand, incompleted_participants_samarkand[i], logtime=logtime, level=level, exp=exp_value, exp_to_next_level=exp_to_next_level)
                    print(f"Student {incompleted_participants_samarkand[i]} has been updated in Samarkand")
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
        

def parse_personal_stats(access_token, intensive_month_selected):
    HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv"):
        students_tashkent = list()
        with open(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv", 'r') as file_tashkent:
            student = file_tashkent.readline()
            while student:
                student = file_tashkent.readline()
                students_tashkent.append(student.strip())

        new_students_tashkent = students_tashkent[:len(students_tashkent) - 1]
        tashkent_students_usernames = [student.strip() for student in new_students_tashkent]
        populate_personal_stats("tashkent", f"data_{intensive_month_selected}/participants/tashkent/personal_stats.db",  tashkent_students_usernames)

        students_samarkand = list()
        with open(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv", 'r') as file_samarkand:
            student = file_samarkand.readline()
            while student:
                student = file_samarkand.readline()
                students_samarkand.append(student.strip())

        new_students_samarkand = students_samarkand[:len(students_samarkand) - 1]
        samarkand_students_usernames = [student.strip() for student in new_students_samarkand]
        populate_personal_stats("samarkand", f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db",  samarkand_students_usernames)

        try:
            intensive_start_date = datetime.date(2025, 3, 3)
            today = datetime.date.today()
            one_week_ago = today - datetime.timedelta(weeks=1)
            date_to_use = one_week_ago if one_week_ago - datetime.timedelta(weeks=1) > intensive_start_date else intensive_start_date

            active_participants_tashkent = get_active_student_list(f"data_{intensive_month_selected}/participants/tashkent/participants.db")

            if not active_participants_tashkent:
                active_participants_tashkent = tashkent_students_usernames

            db_path_tashkent = f"data_{intensive_month_selected}/participants/tashkent/personal_stats.db"
            last_parced_student = get_last_parced_student_personal_stats(db_path_tashkent)

            if last_parced_student and last_parced_student in active_participants_tashkent:  
                index = active_participants_tashkent.index(last_parced_student)
                active_participants_tashkent = active_participants_tashkent[index:]

            for i in range(len(active_participants_tashkent)): 
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{active_participants_tashkent[i]}"), headers=HEADERS) 
                time.sleep(0.5)
                response_accepted_projects = requests.get(BASE_URL.format(f"/participants/{active_participants_tashkent[i]}/projects?limit=50&offset=0&status=ACCEPTED"), headers=HEADERS)
                time.sleep(0.5)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{active_participants_tashkent[i]}/logtime?date={date_to_use}"), headers=HEADERS)
                time.sleep(0.5)
                response_badges = requests.get(BASE_URL.format(f"/participants/{active_participants_tashkent[i]}/badges"), headers=HEADERS)


                if response_basic_info.status_code == 200 and response_logtime.status_code == 200 and response_accepted_projects.status_code == 200 and response_badges.status_code == 200:
                    response_basic_info_json = json.loads(response_basic_info.text)
                    exp_value = response_basic_info_json['expValue']

                    logtime = float(response_logtime.text)

                    response_accepted_projects_json = json.loads(response_accepted_projects.text)
                    total_num_projects_accepted = len(response_accepted_projects_json["projects"])

                    response_badges_json = json.loads(response_badges.text)
                    educational_events = len([badge for badge in response_badges_json["badges"] if badge["name"] == "Educational event"])
                    entertainment_events = len([badge for badge in response_badges_json["badges"] if badge["name"] == "Entertainment event"])
                    total_num_events = educational_events + entertainment_events

                    update_personal_stats(campus="tashkent", db_path=f"data_{intensive_month_selected}/participants/tashkent/personal_stats.db", student=active_participants_tashkent[i], logtime=logtime, exp=exp_value, total_tasks_accepted=total_num_projects_accepted, educational_events=educational_events, entertainment=entertainment_events, total_number_events=total_num_events)
                    if i > 0:
                        set_last_parced_student_personal_stats("tashkent", f"data_{intensive_month_selected}/participants/tashkent/personal_stats.db", active_participants_tashkent[i - 1], 0)
                        
                    set_last_parced_student_personal_stats("tashkent", f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db", active_participants_tashkent[i], 1)
                    print(f"{active_participants_tashkent[i]}, {logtime}, {exp_value}, {total_num_projects_accepted}, {educational_events}, {entertainment_events}, {total_num_events}")

                    time.sleep(1)


            active_participants_samarkand = get_active_student_list(f"data_{intensive_month_selected}/participants/samarkand/participants.db")

            if not active_participants_samarkand:
                active_participants_samarkand = samarkand_students_usernames

            db_path_samarkand = f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db"
            last_parced_student = get_last_parced_student_personal_stats(db_path_samarkand)

            if last_parced_student and last_parced_student in active_participants_samarkand:  
                index = active_participants_samarkand.index(last_parced_student)
                active_participants_samarkand = active_participants_samarkand[index:]

            for i in range(len(active_participants_samarkand)): 
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{active_participants_samarkand[i]}"), headers=HEADERS) 
                time.sleep(0.5)
                response_accepted_projects = requests.get(BASE_URL.format(f"/participants/{active_participants_samarkand[i]}/projects?limit=50&offset=0&status=ACCEPTED"), headers=HEADERS)
                time.sleep(0.5)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{active_participants_samarkand[i]}/logtime?date={date_to_use}"), headers=HEADERS)
                time.sleep(0.5)
                response_badges = requests.get(BASE_URL.format(f"/participants/{active_participants_samarkand[i]}/badges"), headers=HEADERS)


                if response_basic_info.status_code == 200 and response_logtime.status_code == 200 and response_accepted_projects.status_code == 200 and response_badges.status_code == 200:
                    response_basic_info_json = json.loads(response_basic_info.text)
                    exp_value = response_basic_info_json['expValue']

                    logtime = float(response_logtime.text)

                    response_accepted_projects_json = json.loads(response_accepted_projects.text)
                    total_num_projects_accepted = len(response_accepted_projects_json["projects"])

                    response_badges_json = json.loads(response_badges.text)
                    educational_events = len([badge for badge in response_badges_json["badges"] if badge["name"] == "Educational event"])
                    entertainment_events = len([badge for badge in response_badges_json["badges"] if badge["name"] == "Entertainment event"])
                    total_num_events = educational_events + entertainment_events

                    update_personal_stats(campus="samarkand", db_path=f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db", student=active_participants_samarkand[i], logtime=logtime, exp=exp_value, total_tasks_accepted=total_num_projects_accepted, educational_events=educational_events, entertainment=entertainment_events, total_number_events=total_num_events)
                    if i > 0:
                        set_last_parced_student_personal_stats("samarkand", f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db", active_participants_samarkand[i - 1], 0)

                    set_last_parced_student_personal_stats("samarkand", f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db", active_participants_samarkand[i], 1)
                    print(f"{active_participants_samarkand[i]}, {logtime}, {exp_value}, {total_num_projects_accepted}, {educational_events}, {entertainment_events}, {total_num_events}")

                    time.sleep(1)

            set_all_last_parced("tashkent")
            set_all_last_parced("samarkand")
            
        except Exception as e:
            raise Exception(f"There was a problem during parsing from the api {e}")



def update_read_databases():
    # UPDATING PARTICIPANTS 
    students_tashkent = get_all_participants_for_overall(f"data_{intensive_month_selected}/participants/tashkent/participants.db")
    students_samarkand = get_all_participants_for_overall(f"data_{intensive_month_selected}/participants/samarkand/participants.db")


    #set being updated 1 for tashkent
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "tashkent", 1)
    for student in students_tashkent:
        username = student[0]
        logtime = student[1]
        level = student[2]
        exp = student[3]
        exp_to_next_level = student[4]

        update_participant(db_path=f"data_{intensive_month_selected}/participants_to_read/tashkent/participants.db", student=username, logtime=logtime, level=level, exp=exp, exp_to_next_level=exp_to_next_level)
        print(f"The student {username} has been updated in particiapants in Tashkent")
    
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "tashkent", 0)

    #set being updated 1 for samarkand
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "samarkand", 1)
    for student in students_samarkand:
        username = student[0]
        logtime = student[1]
        level = student[2]
        exp = student[3]
        exp_to_next_level = student[4]

        update_participant(db_path=f"data_{intensive_month_selected}/participants_to_read/samarkand/participants.db", student=username, logtime=logtime, level=level, exp=exp, exp_to_next_level=exp_to_next_level)
        print(f"The student {username} has been updated in participants in Tashkent")
    
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "samarkand", 0)

    # UPDATING PERSONAL STATS 

    personal_stats_tashkent = get_all_personal_stats_for_overall(f"data_{intensive_month_selected}/participants/tashkent/personal_stats.db")
    personal_stats_samarkand = get_all_personal_stats_for_overall(f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db")

    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "tashkent", 1)
    for student in personal_stats_tashkent:
        username = student[0]
        logtime = student[1]
        exp = student[2]
        total_tasks_accepted = student[3]
        educational_events = student[4]
        entertainment = student[5]
        total_number_events = student[6]

        update_personal_stats(campus="tashkent", db_path=f"data_{intensive_month_selected}/participants_to_read/tashkent/personal_stats.db", student=username, logtime=logtime, exp=exp, total_tasks_accepted=total_tasks_accepted, educational_events=educational_events, entertainment=entertainment, total_number_events=total_number_events)
        print(f"The student {username} has been updated in personal_stats in Tashkent")
    
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "tashkent", 0)



    #set being updated 1 for samarkand
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "samarkand", 1)
    for student in personal_stats_samarkand:
        username = student[0]
        logtime = student[1]
        exp = student[2]
        total_tasks_accepted = student[3]
        educational_events = student[4]
        entertainment = student[5]
        total_number_events = student[6]

        update_personal_stats(campus="samarkand", db_path=f"data_{intensive_month_selected}/participants_to_read/samarkand/personal_stats.db", student=username, logtime=logtime, exp=exp, total_tasks_accepted=total_tasks_accepted, educational_events=educational_events, entertainment=entertainment, total_number_events=total_number_events)
        print(f"The student {username} has been updated in personal_stats in Samarkand")
    
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "samarkand", 0)



def plot_exam_progress(campus):
    db_path = f"data_{intensive_month_selected}/tasks/{campus}/exams_progress.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT student_username, E01D05, E02D12, E03D19 FROM exams_progress")
    data = cursor.fetchall()

    conn.close()

    unstable_students = []
    most_progress_students = []
    biggest_fall_students = []

    for student, e01d05, e02d12, e03d19 in data:
        scores = [e01d05, e02d12, e03d19]
        if None in scores:
            continue

        # Calculate differences
        progress = e03d19 - e01d05
        fall = e01d05 - e03d19
        instability = max(scores) - min(scores)

        unstable_students.append((student, instability, scores))
        most_progress_students.append((student, progress, scores))
        biggest_fall_students.append((student, fall, scores))

    # Sort and select top 5 students for each category
    unstable_students = sorted(unstable_students, key=lambda x: x[1], reverse=True)[:10]
    most_progress_students = sorted(most_progress_students, key=lambda x: x[1], reverse=True)[:10]
    biggest_fall_students = sorted(biggest_fall_students, key=lambda x: x[1], reverse=True)[:10]

    def plot_students(students, title, filename):
        for student, _, scores in students:
            exams = ["E01D05", "E02D12", "E03D19"]
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

    for campus in campuses:
        report = make_report(task, "russian", campus, f"data_{intensive_month_selected}/tasks.db", 1)
        result = [report['report']]

        for language in ["russian", "english", "uzbek"]:
            for report_type in ['passed', 'hundred', 'scored_didnt_pass', 'in_progress', 'in_reviews', 'registered']:
                students = report.get(f'scored_{report_type}' if report_type != 'passed' else 'passed_students')

                if students:

                    for lang in ['english', 'russian', 'uzbek']:
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

                        if language == "russian": 
                                campus_language_specified = "Ташкент" if campus == "tashkent" else "Самарканд"
                        else:
                            campus_language_specified = campus.capitalize()

                            post_url = create_telegraph_post(
                                TELEGRAPH_TOKEN, f"{titles[lang][report_type]} ({task}) {campus_language_specified.capitalize()}",
                                make_content(students, task_id, lang))['result']['url']
                            create_post(task, post_url, f'url_{report_type}_{lang}_{campus}')
                            time.sleep(1)



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

        elif sys.argv[1] == "parse_exam_progress":
        
            sort_students_exam_progress(f"data_{intensive_month_selected}/participants/tashkent/participants.db", "tashkent")
            sort_students_exam_progress(f"data_{intensive_month_selected}/participants/samarkand/participants.db", "samarkand")
            plot_exam_progress("tashkent")
            plot_exam_progress("samarkand")

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
                get_coatlitions_api(token, tashkent_id, 'tashkent')
                get_coatlitions_api(token, samarkand_id, 'samarkand')

            if not os.path.exists(f'data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv') or not os.path.exists(f'data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv'):
                get_all_intensiv_participants_api(token)

            


            get_specific_project_complеtion_info(token, str(project_id), week, task, intensive_month_selected)
            update_posts_db(task, intensive_month_selected)

            update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=0)





if __name__ == '__main__':
    main()
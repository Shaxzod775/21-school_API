#!/../venv/bin/python3
import os
import sys

sys.path.append("..")

import requests
import json
import time
from db_modules.db_api import *
from config_api import *


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

        with open("data/campuses/campuses.csv", "w+") as file:
            file.write("id,shortName,fullName\n")
            for i in range(len(campuses_json)):
                id = campuses_json[i]['id']
                shortName = campuses_json[i]['shortName']
                fullName = campuses_json[i]['fullName']
                file.write(f"{id},{shortName},{fullName}\n")
    else:
        raise Exception(f"There was an error during parsing from the api {BASE_URL.BASE_URL.format('/campuses')}")


def get_specific_campus_id(campus_name):
    _return_value = "None"
    with open("data/campuses/campuses.csv", "r+") as file:
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

        with open(f'data/coalitions/{campus_name}/intensiv_coalitions.csv', 'w+') as int_file:
            int_file.write('coalitionId,name\n')
            for i in range(len(intensiv_coalitions)):
                if i == (len(intensiv_coalitions)):
                    coalitionId, name = intensiv_coalitions[i]['coalitionId'], intensiv_coalitions[i]['name']
                    int_file.write(f'{coalitionId},{name}')
                coalitionId, name = intensiv_coalitions[i]['coalitionId'], intensiv_coalitions[i]['name']
                int_file.write(f'{coalitionId},{name}\n')

        
        with open(f'data/coalitions/{campus_name}/main_education_coalitions.csv', 'w+') as int_file:
            int_file.write('coalitionId,name\n')
            for i in range(len(main_education_coalitions)):
                coalitionId, name = main_education_coalitions[i]['coalitionId'], main_education_coalitions[i]['name']
                int_file.write(f'{coalitionId},{name}\n')


def get_all_intensiv_participants_api(access_token):
    all_participants_tashkent = list()
    tashkent_intensiv_coalitions_ids = list()

    #Tashkent
    with open('data/coalitions/tashkent/intensiv_coalitions.csv', 'r+') as file:
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
        
    with open('data/participants/tashkent/intensiv_participants.csv', 'w+') as file:
        file.write('USERNAME\n')
        for username in all_participants_tashkent:
            file.write(f'{username}\n')


    #Samarkand

    samarkand_intensiv_coalitions_ids = list()
    all_participants_samarkand = list()

    with open('data/coalitions/samarkand/intensiv_coalitions.csv', 'r+') as file:
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
        
    with open('data/participants/samarkand/intensiv_participants.csv', 'w+') as file:
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

def get_specific_project_complеtion_info(access_token, project_id, week, project_name):
        HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
        }

        if os.path.exists(f"data/participants/tashkent/participants.db") and os.path.exists(f"data/participants/samarkand/participants.db"):
            db_path_tashkent = f"data/tasks/tashkent/{week}/{project_name}/{project_name}.db"
            students_tashkent = get_all_students("data/participants/tashkent/participants.db")

            if not os.path.exists(db_path_tashkent):
                init_table_for_task(db_path_tashkent)
            populate_task_results(db_path_tashkent, students_tashkent)
            

            db_path_samarkand = f"data/tasks/samarkand/{week}/{project_name}/{project_name}.db"
            students_samarkand = get_all_students("data/participants/samarkand/participants.db")

            if not os.path.exists(db_path_samarkand):
                init_table_for_task(db_path_samarkand)
            populate_task_results(db_path_samarkand, students_samarkand)

            
            incompleted_students_tashkent = list()
            null = get_student_task_result_by_status(db_path_tashkent, "NULL")
            registered = get_student_task_result_by_status(db_path_tashkent, "REGISTERED")
            in_progress = get_student_task_result_by_status(db_path_tashkent, "IN_PROGRESS")
            in_reviews = get_student_task_result_by_status(db_path_tashkent, "IN_REVIEWS")

            if null:
                for student in null:
                    incompleted_students_tashkent.append(student)
            elif registered:
                for student in registered:
                    incompleted_students_tashkent.append(student)
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


def task_report(task, filepath):
        _, week = INTENSIVE[task]
        passed_students, _, scored_didnt_pass, scored_hundred_percent, num_of_students, acceptance_rate, in_progress, in_reviews, registered = sort_task_data(filepath)

        passed_students_usernames = [student.split(',')[0] for student in passed_students]
        scored_hundred_percent_usernames = [student.split(',')[0] for student in scored_hundred_percent]
        scored_didnt_pass_usernames = [student.split(',')[0] for student in scored_didnt_pass] 
        in_progress_usernames = [student.split(',')[0] for student in in_progress] 
        in_reviews_usernames = [student.split(',')[0] for student in in_reviews] 
        registered_usernames = [student.split(',')[0] for student in registered] 

        with open(f"data/tasks/tashkent/{week}/{task}/task_report.txt", "w+") as file_tashkent:
            file_tashkent.write(f"Репорт:\n\n")
            if len(in_progress) != 0:
                file_tashkent.write(f"{len(in_reviews)} записались на проэкт\n")
            if len(in_progress) != 0:
                file_tashkent.write(f"{len(in_reviews)} сейчас делают проэкт\n")
            if len(in_reviews) != 0:
                file_tashkent.write(f"{len(in_reviews)} завершили проэкт и сейчас проходят проверку\n")
            if len(passed_students) != 0:
                file_tashkent.write(f"Из {num_of_students} учеников только {len(passed_students)} смогли сдать этот проэкт!\n\n")
            if len(scored_didnt_pass) != 0:
                file_tashkent.write(f"{len(scored_didnt_pass)} сделали хотя бы одно задание, но не смогли сдать проэкт\n\n")
            if len(passed_students) != 0:
                file_tashkent.write("Поздравления всем сдавшим ребятам!\n\n")


        with open(f"data/tasks/samarkand/{week}/{task}/task_report.txt", "w+") as file_samarkand:
            file_samarkand.write(f"Репорт:\n\n")
            if len(in_progress) != 0:
                file_samarkand.write(f"{len(in_reviews)} записались на проэкт\n")
            if len(in_progress) != 0:
                file_samarkand.write(f"{len(in_reviews)} сейчас делают проэкт\n")
            if len(in_reviews) != 0:
                file_samarkand.write(f"{len(in_reviews)} завершили проэкт и сейчас проходят проверку\n")
            if len(passed_students) != 0:
                file_samarkand.write(f"Из {num_of_students} учеников только {len(passed_students)} смогли сдать этот проэкт!\n\n")
            if len(scored_didnt_pass) != 0:
                file_samarkand.write(f"{len(scored_didnt_pass)} сделали хотя бы одно задание, но не смогли сдать проэкт\n\n")
            if len(passed_students) != 0:
                file_samarkand.write("Поздравления всем сдавшим ребятам!\n\n")

        if len(passed_students) != 0:
            with open(f"data/tasks/tashkent/{week}/{task}/details/passed_students.csv", "w+") as file1_tashkent:
                file1_tashkent.write(f"USERNAMES,TOTAL NUMBER: {len(passed_students)},ACCEPTANCE RATE: {acceptance_rate:.2f}%\n")
                for student in passed_students_usernames:
                    file1_tashkent.write(f"{student}\n")

            with open(f"data/tasks/samarkand/{week}/{task}/details/passed_students.csv", "w+") as file1_samarkand:
                file1_samarkand.write(f"USERNAMES,TOTAL NUMBER: {len(passed_students)},ACCEPTANCE RATE: {acceptance_rate:.2f}%\n")
                for student in passed_students_usernames:
                    file1_samarkand.write(f"{student}\n")



        if len(scored_hundred_percent) != 0:
            with open(f"data/tasks/tashkent/{week}/{task}/details/scored_hundred.csv", "w+") as file1_tashkent:
                file1_tashkent.write(f"USERNAMES,TOTAL NUMBER: {len(scored_hundred_percent)}\n")
                for student in scored_hundred_percent_usernames:
                    file1_tashkent.write(f"{student}\n")

            with open(f"data/tasks/samarkand/{week}/{task}/details/scored_hundred.csv", "w+") as file1_samarkand:
                file1_samarkand.write(f"USERNAMES,TOTAL NUMBER: {len(scored_hundred_percent)}\n")
                for student in scored_hundred_percent_usernames:
                    file1_samarkand.write(f"{student}\n")



        if len(scored_didnt_pass) != 0:
            with open(f"data/tasks/tashkent/{week}/{task}/details/scored_didnt_pass.csv", "w+") as file1_tashkent:
                file1_tashkent.write(f"USERNAMES,TOTAL NUMBER: {len(scored_didnt_pass)}\n")
                for student in scored_didnt_pass_usernames:
                    file1_tashkent.write(f"{student}\n")

            with open(f"data/tasks/samarkand/{week}/{task}/details/scored_didnt_pass.csv", "w+") as file1_samarkand:
                file1_samarkand.write(f"USERNAMES,TOTAL NUMBER: {len(scored_didnt_pass)}\n")
                for student in scored_didnt_pass_usernames:
                    file1_samarkand.write(f"{student}\n")


        if len(in_progress) != 0:
            with open(f"data/tasks/tashkent/{week}/{task}/details/in_progress.csv", "w+") as file1_tashkent:
                file1_tashkent.write(f"USERNAMES,TOTAL NUMBER: {len(in_progress_usernames)}\n")
                for student in in_progress_usernames:
                    file1_tashkent.write(f"{student}\n")

            with open(f"data/tasks/samarkand/{week}/{task}/details/in_progress.csv", "w+") as file1_samarkand:
                file1_samarkand.write(f"USERNAMES,TOTAL NUMBER: {len(in_progress_usernames)}\n")
                for student in in_progress_usernames:
                    file1_samarkand.write(f"{student}\n")



        if len(in_reviews) != 0:
            with open(f"data/tasks/tashkent/{week}/{task}/details/in_reviews.csv", "w+") as file1_tashkent:
                file1_tashkent.write(f"USERNAMES,TOTAL NUMBER: {len(in_reviews_usernames)}\n")
                for student in in_reviews_usernames:
                    file1_tashkent.write(f"{student}\n")

            with open(f"data/tasks/samarkand/{week}/{task}/details/in_reviews.csv", "w+") as file1_samarkand:
                file1_samarkand.write(f"USERNAMES,TOTAL NUMBER: {len(in_reviews_usernames)}\n")
                for student in in_reviews_usernames:
                    file1_samarkand.write(f"{student}\n")



        if len(registered) != 0:
            with open(f"data/tasks/tashkent/{week}/{task}/details/registered.csv", "w+") as file1_tashkent:
                file1_tashkent.write(f"USERNAMES,,TOTAL NUMBER: {len(registered_usernames)}\n")
                for student in registered_usernames:
                    file1_tashkent.write(f"{student}\n")


            with open(f"data/tasks/samarkand/{week}/{task}/details/registered.csv", "w+") as file1_samarkand:
                file1_samarkand.write(f"USERNAMES,,TOTAL NUMBER: {len(registered_usernames)}\n")
                for student in registered_usernames:
                    file1_samarkand.write(f"{student}\n")



def sort_exam_data_before(task):
    try:
        if os.path.exists(task) == False:
            raise Exception(f'There is no task file in this folder! {task}')
        
        students = list()
        
        with open(task, 'r') as file:
            line = file.readline()
            while line:
                line = file.readline()
                students.append(line.strip())

        new_students = students[:len(students) - 1]

        task_name = task.split('/')[-1].split('.')[0]

        _, week  = INTENSIVE[task_name]

        registered = [new_students[i] for i in range(len(new_students)) if new_students[i].split(',')[3] == 'REGISTERED']

        registered_needed_data = [[student.split(",")[0], student.split(",")[1], student.split(",")[2]] for student in registered]

        with open(f"data/tasks/{week}/{task_name}/details/registered.csv", "w+") as file1:
            file1.write(f"student,title,status,total registered: {len(registered_needed_data)}\n")
            for student in registered_needed_data:
                username, title, status = student
                file1.write(f"{username},{title},{status}\n")

        return tuple(registered)
    except Exception:
        raise Exception


def parse_student_info(access_token):
    HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    if os.path.exists(f"data/participants/tashkent/intensiv_participants.csv") and os.path.exists(f"data/participants/samarkand/intensiv_participants.csv"):
        students_tashkent = list()
        with open(f"data/participants/tashkent/intensiv_participants.csv", 'r') as file_tashkent:
            student = file_tashkent.readline()
            while student:
                student = file_tashkent.readline()
                students_tashkent.append(student.strip())

        new_students_tashkent = students_tashkent[:len(students_tashkent) - 1]
        tashkent_students_usernames = [student.strip() for student in new_students_tashkent]
        populate_participants("tashkent", tashkent_students_usernames)

        students_samarkand = list()
        with open(f"data/participants/samarkand/intensiv_participants.csv", 'r') as file_samarkand:
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

            tashkent_active_students = 0

            incompleted_participants_tashkent = get_incompleted_participants("tashkent")

            if not incompleted_participants_tashkent:
                incompleted_participants_tashkent = tashkent_students_usernames

            db_path_tashkent = "data/participants/samarkand/participants.db"
            last_parced_student = get_last_parced_student(db_path_tashkent)
            if last_parced_student and last_parced_student in incompleted_participants_tashkent: 
                index = incompleted_participants_tashkent.index(last_parced_student)
                incompleted_participants_tashkent = incompleted_participants_tashkent[index:]

            for i in range(len(incompleted_participants_tashkent)):  # Iterate through students (usernames)
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_tashkent[i]}"), headers=HEADERS)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_tashkent[i]}/logtime?date={date_to_use}"), headers=HEADERS)

                if response_logtime.status_code == 200 and response_basic_info.status_code == 200:
                    logtime = float(response_logtime.text)

                    if logtime > 0.0:
                        tashkent_active_students += 1

                    response_basic_info_json = json.loads(response_basic_info.text)
                    level = response_basic_info_json['level']
                    exp_value = response_basic_info_json['expValue']
                    exp_to_next_level = response_basic_info_json['expToNextLevel']


                    # Update the database
                    update_participant("tashkent", incompleted_participants_tashkent[i], logtime=logtime, level=level, exp=exp_value, exp_to_next_level=exp_to_next_level)
                    if i > 0:
                        set_last_parced_student("tashkent", incompleted_participants_tashkent[i - 1], 0)
                    
                    set_last_parced_student("tashkent", incompleted_participants_tashkent[i], 1)
                    print(f'{incompleted_participants_tashkent[i]}, {logtime}, {level}, {exp_value}, {exp_to_next_level}')

                    time.sleep(1)

            incompleted_participants_samarkand = get_incompleted_participants("samarkand")

            if not incompleted_participants_samarkand:
                incompleted_participants_samarkand = samarkand_students_usernames


            db_path_samarkand = "data/participants/samarkand/participants.db"
            last_parced_student = get_last_parced_student(db_path_samarkand)

            if last_parced_student and last_parced_student in incompleted_participants_samarkand:  
                index = incompleted_participants_samarkand.index(last_parced_student)
                incompleted_participants_samarkand = incompleted_participants_samarkand[index:]

            for i in range(len(incompleted_participants_samarkand)):  
                response_basic_info = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_samarkand[i]}"), headers=HEADERS)
                response_logtime = requests.get(BASE_URL.format(f"/participants/{incompleted_participants_samarkand[i]}/logtime?date={date_to_use}"), headers=HEADERS)

                if response_logtime.status_code == 200 and response_basic_info.status_code == 200:
                    logtime = float(response_logtime.text)

                    if logtime > 0.0:
                        tashkent_active_students += 1

                    response_basic_info_json = json.loads(response_basic_info.text)
                    level = response_basic_info_json['level']
                    exp_value = response_basic_info_json['expValue']
                    exp_to_next_level = response_basic_info_json['expToNextLevel']

                    # Update the database
                    update_participant("samarkand", incompleted_participants_samarkand[i], logtime=logtime, level=level, exp=exp_value, exp_to_next_level=exp_to_next_level)
                    if i > 0:
                        set_last_parced_student("samarkand", incompleted_participants_samarkand[i - 1], 0)

                    set_last_parced_student("samarkand", incompleted_participants_samarkand[i], 1)
                    print(f'{incompleted_participants_samarkand[i]}, {logtime}, {level}, {exp_value}, {exp_to_next_level}')

                    time.sleep(1)
            
            last_parced_student = get_last_parced_student(db_path_tashkent)
            if last_parced_student == incompleted_participants_tashkent[-1]:
                set_last_parced_student("tashkent", last_parced_student, 0)
            
            last_parced_student = get_last_parced_student(db_path_samarkand)
            if last_parced_student == incompleted_participants_samarkand[-1]:
                set_last_parced_student("samarkand", last_parced_student, 0)
            



        except Exception as e:
            raise Exception(f"There was a problem during parsing from the api {e}")
        
def sort_students_data():
    if os.path.exists("data/participants/tashkent/small_info.csv"):
        with open("data/participants/tashkent/small_info.csv", 'r') as file:
            line = file.readline()
            students = list()
            while line:
                line = file.readline()
                students.append(line.strip())
            
            top_student = str()
            top_student_score = 0
            for student in students[:len(students) - 1]:
                if top_student_score <= int(student.split(",")[-1]):
                    top_student = student
                    top_student_score = int(student.split(",")[-1])

            print(top_student)
            

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] not in INTENSIVE:
            raise Exception(f"The entered tasks is not among the intensive tasks")

        task = sys.argv[1]


        update_task(db_path="./data/tasks.db", task=task, being_parsed=1)

        get_api_token()
        token = get_file_token()
    
        project_id, week = INTENSIVE[f'{task}']

        if not os.path.exists('data/campuses/campuses.csv'):
            get_list_of_campuses_api(token)
            tashkent_id = get_specific_campus_id("tashkent")
            samarkand_id = get_specific_campus_id("samarkand")
        else:
            tashkent_id = get_specific_campus_id("tashkent")
            samarkand_id = get_specific_campus_id("samarkand")
            

        if not os.path.exists('data/coalitions/tashkent/intensiv_coalitions.csv') or not os.path.exists('data/coalitions/samarkand/intensiv_coalitions.csv') :
            get_coatlitions_api(token, tashkent_id, 'tashkent')
            get_coatlitions_api(token, samarkand_id, 'samarkand')

        if not os.path.exists('data/participants/tashkent/intensiv_participants.csv') or not os.path.exists('data/participants/samarkand/intensiv_participants.csv'):
            get_all_intensiv_participants_api(token)


        get_specific_project_complеtion_info(token, str(project_id), week, task)
        # parse_student_info(token)
        update_task(db_path="./data/tasks.db", task=task, being_parsed=0)


        if sys.argv[1].startswith('P') or sys.argv[1].startswith('T'):
            if not os.path.exists(f'data/tasks/tashkent/{week}/{task}/task_report.txt') or not os.path.exists(f'data/tasks/samarkand/{week}/{task}/task_report.txt'):
                task_report(task, f'data/tasks/tashkent/{week}/{task}/{task}.csv')
                task_report(task, f'data/tasks/samarkand/{week}/{task}/{task}.csv')
        else:
            # exam_report(task)
            update_task(db_path="./data/tasks.db", task=task, being_parsed=0)





if __name__ == '__main__':
    main()
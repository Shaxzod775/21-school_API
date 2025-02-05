#!/../venv/bin/python3
import os
import sys
import requests
import json
import time
from config import *


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
        while line:
            line = file.readline()
            id, shortName, school, fullName = line.split(',')
            if campus_name.capitalize() in shortName.split():
                _return_value = id
                break
    
    if _return_value == "None":
        raise Exception(f"There is no campus named {campus_name} among all the campuses")

    return _return_value


def get_coatlitions_api(access_token, campus_id):
    _return_value = str()

    HEADERS = {
    'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get(BASE_URL.format(f"/campuses/{campus_id}/coalitions"), headers=HEADERS)

    if response.status_code == 200:
        coalitions = json.loads(response.text)['coalitions']

        _return_value = coalitions

        intensiv_tribe_names = ['AYIQ', 'JAYRON', 'LAYLAK', 'QOPLON']

        intensiv_coalitions = list()
        main_education_coalitions = list()
        for i in range(len(coalitions)):
            if coalitions[i]['name'] in intensiv_tribe_names:
                intensiv_coalitions.append(coalitions[i])
            else:
                main_education_coalitions.append(coalitions[i])

        with open('data/coalitions/intensiv_coalitions.csv', 'w+') as int_file:
            int_file.write('coalitionId,name\n')
            for i in range(len(intensiv_coalitions)):
                if i == (len(intensiv_coalitions)):
                    coalitionId, name = intensiv_coalitions[i]['coalitionId'], intensiv_coalitions[i]['name']
                    int_file.write(f'{coalitionId},{name}')
                coalitionId, name = intensiv_coalitions[i]['coalitionId'], intensiv_coalitions[i]['name']
                int_file.write(f'{coalitionId},{name}\n')

        
        with open('data/coalitions/main_education_coalitions.csv', 'w+') as int_file:
            int_file.write('coalitionId,name\n')
            for i in range(len(main_education_coalitions)):
                coalitionId, name = main_education_coalitions[i]['coalitionId'], main_education_coalitions[i]['name']
                int_file.write(f'{coalitionId},{name}\n')

    return _return_value

def get_all_intensiv_participants_api(access_token):
    all_participants = list()
    intensiv_coalitions_ids = list()

    with open('data/coalitions/intensiv_coalitions.csv', 'r+') as file:
        line = file.readline()
        while line:
            line = file.readline()
            intensiv_coalitions_ids.append(line.split(',')[0])

    new_intensiv_coalitions_ids = intensiv_coalitions_ids[:-1]

    for i in range(len(new_intensiv_coalitions_ids)):
        try: 
            HEADERS = {
            'Authorization': 'Bearer {}'.format(access_token),
            }

            response = requests.get(BASE_URL.format(f"/coalitions/{new_intensiv_coalitions_ids[i]}/participants?limit=1000&offset=0"), headers=HEADERS)

            if response.status_code == 200:
                for student in json.loads(response.text)['participants']:
                    all_participants.append(student)
                    print(student)
            else:
                raise Exception(f"There was a mistake while parcing participants from the API\n{response.status_code}\n{response.text}")
        except Exception:
            raise Exception
        
    with open('data/participants/intensiv_participants.csv', 'w+') as file:
        file.write('USERNAME\n')
        for username in all_participants:
            file.write(f'{username}\n')

    return all_participants


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

def get_specific_project_complеtion_info(access_token, project_id, project_name):
    try:
        HEADERS = {
        'Authorization': 'Bearer {}'.format(access_token),
        }
                    
        filename = 'data/participants/intensiv_participants.csv'
        

        if os.path.exists(filename) == True:
            students = list()
            with open(filename, 'r') as file:
                student = file.readline()
                while student:
                    student = file.readline()
                    students.append(student.strip())

            new_students = students[:len(students) - 1]

            try:
                with open(f'data/tasks/{project_name}/{project_name}.csv', 'w+') as file:
                    file.write('student,title,type,status,final score\n')
                    for i in range(len(new_students)):
                            response = requests.get(BASE_URL.format(f"/participants/{new_students[i]}/projects/{project_id}"), headers=HEADERS)
                            if response.status_code == 200:
                                response_json = json.loads(response.text)
                                title = response_json['title']
                                type = response_json['type']
                                status = response_json['status']
                                final_percentage = response_json['finalPercentage']
                                file.write(f'{new_students[i]},{title},{type},{status},{final_percentage}\n')
                                print(f'{new_students[i]},{title},{type},{status},{final_percentage}')
                                time.sleep(1)
                            else:
                                raise Exception(f"There was a problem during parsing scores from the api!\n{response.status_code}\n{response.text}")
            except Exception:
                raise Exception

    except Exception:
        raise Exception
    
def sort_task_data(filename):
    try:
        if os.path.exists(filename) == False:
            raise Exception(f'There is no task file in this folder! {filename}')
        
        students = list()
        
        with open(filename, 'r') as file:
            line = file.readline()
            while line:
                line = file.readline()
                students.append(line.strip())

        new_students = students[:len(students) - 1]

        registered = [new_students[i] for i in range(len(new_students)) if new_students[i].split(',')[3] == 'REGISTERED']
        passed_students = [new_students[i] for i in range(len(new_students)) if new_students[i].split(',')[3] == 'ACCEPTED']
        failed_students = [new_students[i] for i in range(len(new_students)) if new_students[i].split(',')[3] == 'FAILED']
        in_progress = [new_students[i] for i in range(len(new_students)) if new_students[i].split(',')[3] == 'IN_PROGRESS']
        in_reviews = [new_students[i] for i in range(len(new_students)) if new_students[i].split(',')[3] == 'IN_REVIEWS']

        scored_didnt_pass = list()

        for i in range(len(new_students)):
            score = new_students[i].split(',')[-1]
            status = new_students[i].split(',')[3]
            if score != '0' and score != 'None':
                if int(score) < 50 and status != 'ACCEPTED':
                    scored_didnt_pass.append(new_students[i])


        scored_didnt_pass_result = sorted(scored_didnt_pass, key=lambda item: int(item.split(',')[-1]), reverse=True)

        scored_hundred_percent = [student for student in passed_students if int(student.split(',')[-1]) == 100]

        acceptance_rate = (len(passed_students) / len(new_students)) * 100

        return passed_students, failed_students, scored_didnt_pass_result, scored_hundred_percent, len(new_students), acceptance_rate, in_progress, in_reviews, registered
    except Exception:
        raise Exception

# def report_during_exam():

def task_report(task):
        passed_students, _, scored_didnt_pass, scored_hundred_percent, num_of_students, acceptance_rate, in_progress, in_reviews, registered = sort_task_data(f'data/tasks/{task}/{task}.csv')

        passed_students_usernames = [student.split(',')[0] for student in passed_students]
        scored_hundred_percent_usernames = [student.split(',')[0] for student in scored_hundred_percent]
        scored_didnt_pass_usernames = [student.split(',')[0] for student in scored_didnt_pass] 
        in_progress_usernames = [student.split(',')[0] for student in in_progress] 
        in_reviews_usernames = [student.split(',')[0] for student in in_reviews] 
        registered_usernames = [student.split(',')[0] for student in registered] 

        with open(f"data/tasks/{task}/task_report.txt", "w+") as file:
            file.write(f"Репорт:\n\n")
            if len(in_progress) != 0:
                file.write(f"{len(in_reviews)} записались на проэкт\n")
            if len(in_progress) != 0:
                file.write(f"{len(in_reviews)} сейчас делают проэкт\n")
            if len(in_reviews) != 0:
                file.write(f"{len(in_reviews)} завершили проэкт и сейчас проходят проверку\n")
            if len(passed_students) != 0:
                file.write(f"Из {num_of_students} учеников только {len(passed_students)} смогли сдать этот проэкт!\n\n")
            if len(scored_didnt_pass) != 0:
                file.write(f"{len(scored_didnt_pass)} сделали хотя бы одно задание, но не смогли сдать проэкт\n\n")
            if len(passed_students) != 0:
                file.write("Поздравления всем сдавшим ребятам!\n\n")

        with open(f"data/tasks/{task}/details/passed_students.csv", "w+") as file1:
            file1.write(f"USERNAMES,TOTAL NUMBER: {len(passed_students)},ACCEPTANCE RATE: {acceptance_rate:.2f}%\n")
            for student in passed_students_usernames:
                file1.write(f"{student}\n")

        with open(f"data/tasks/{task}/details/scored_hundred.csv", "w+") as file1:
            file1.write(f"USERNAMES,TOTAL NUMBER: {len(scored_hundred_percent)}\n")
            for student in scored_hundred_percent_usernames:
                file1.write(f"{student}\n")

        with open(f"data/tasks/{task}/details/scored_didnt_pass.csv", "w+") as file1:
            file1.write(f"USERNAMES,TOTAL NUMBER: {len(scored_didnt_pass)}\n")
            for student in scored_didnt_pass_usernames:
                file1.write(f"{student}\n")

        with open(f"data/tasks/{task}/details/in_progress.csv", "w+") as file1:
            file1.write(f"USERNAMES,TOTAL NUMBER: {len(in_progress)}\n")
            for student in in_progress_usernames:
                file1.write(f"{student}\n")

        with open(f"data/tasks/{task}/details/in_reviews.csv", "w+") as file1:
            file1.write(f"USERNAMES,TOTAL NUMBER: {len(in_reviews)}\n")
            for student in in_reviews_usernames:
                file1.write(f"{student}\n")

        with open(f"data/tasks/{task}/details/registered.csv", "w+") as file1:
            file1.write(f"USERNAMES,,TOTAL NUMBER: {len(registered)}\n")
            for student in registered_usernames:
                file1.write(f"{student}\n")

            # file.write(f"""Детали:\n\nCдавшие проэкт: {", ".join(passed_students_usernames)}\n\nНабравшие 100 из 100 баллов: {", ".join(scored_hundred_percent_usernames)}\n\nРешившие хотя-бу одну проблему, но не смогли пройти: {", ".join(scored_didnt_pass_usernames)}\n\nПроцент проходимости экзамена: {acceptance_rate:.2f}%""")


# def report_after_exam(task):
#         passed_students, _, scored_didnt_pass, scored_hundred_percent, num_of_students, acceptance_rate, in_progress, in_reviews, registered = sort_task_data(f'data/tasks/{task}/{task}.csv')

#         passed_students_usernames = [student.split(',')[0] for student in passed_students]
#         scored_hundred_percent_usernames = [student.split(',')[0] for student in scored_hundred_percent]
#         scored_didnt_pass_usernames = [student.split(',')[0] for student in scored_didnt_pass] 

#         with open(f"data/tasks/{task}/report_after_exam.txt", "w+") as file:

#             file.write(f"""Репорт:\n\nИз {num_of_students} учеников только {len(passed_students)} смогли пройти экзамен!\n\n{len(scored_didnt_pass)} человек получили больше 0, но не смогли пройти экзамен\n\nПоздравления всем сдавшим ребятам!\n\n\n""")

#             file.write(f"""Детали:\n\nCдавшие экзамен: {", ".join(passed_students_usernames)}\n\nНабравшие 100 из 100 баллов: {", ".join(scored_hundred_percent_usernames)}\n\nРешившие хотя-бу одну проблему, но не смогли пройти: {", ".join(scored_didnt_pass_usernames)}\n\nПроцент проходимости экзамена: {acceptance_rate:.2f}%""")



def main():
    if len(sys.argv) > 1:
        if sys.argv[1] not in TASKS_INTENSIVE:
            raise Exception(f"The entered tasks is not among the intensive tasks")

        task = sys.argv[1]

        get_api_token()
        token = get_file_token()

        if os.path.exists('data/campuses/campuses.csv') == False:
            get_list_of_campuses_api(token)
            tashkent_id = get_specific_campus_id("tashkent")
        else:
            tashkent_id = get_specific_campus_id("tashkent")

        if os.path.exists('data/coalitions/intensiv_coalitions.csv') == False or os.path.exists('data/coalitions/main_education_coalitions.csv') == False:
            get_coatlitions_api(token, tashkent_id)

        if os.path.exists('data/participants/intensiv_participants.csv') == False:
            get_all_intensiv_participants_api(token)

        if os.path.exists(f'data/tasks/{task}/{task}.csv') == False:
            project_id = TASKS_INTENSIVE[f'{task}']
            get_specific_project_complеtion_info(token, str(project_id), task)

        if sys.argv[1].startswith('P') or sys.argv[1].startswith('T'):
            if os.path.exists(f'data/tasks/{task}/task_report.txt') == False:
                project_id = TASKS_INTENSIVE[f'{task}']
                task_report(task)




if __name__ == '__main__':
    main()
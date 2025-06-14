import os
import sys

sys.path.append("..")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv
from test_bot.posts import *
from report_helpers.report_helper import *

from db_modules.db_api import * 

import matplotlib.pyplot as plt

from collections import Counter
import numpy as np

import time
from configs.config_api import *
import re

def fetch_students(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()[1:]]

def parse_student_info(url, username, password, auth_code, intensive_month_selected):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        time.sleep(5)
        if driver.current_url.startswith("https://auth.sberclass.ru"):
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                password_field = driver.find_element(By.NAME, "password")
                button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

                username_field.send_keys(username)
                password_field.send_keys(password)
                button.click()

                # WebDriverWait(driver, 10).until(
                #     EC.url_contains("https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/login-actions/authenticate?execution")
                # )

                # print(driver.current_url)
               
                # code_field = WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, "//input[@name='otp' and @type='text']"))
                # )

                # code_field.click()

                # code_field.send_keys(auth_code)

                # button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

                # button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_to_be("https://edu.21-school.ru/")
                )

                print("Login successful.")


            except (TimeoutException, NoSuchElementException) as e:
                print(f"Login failed: {e.msg}")
                return
        
        try:
            for city in ["tashkent", "samarkand"]:
                if os.path.exists(f"data_{intensive_month_selected}/participants/{city}/intensiv_participants.csv"):
                    students = []
                    with open(f"data_{intensive_month_selected}/participants/{city}/intensiv_participants.csv", 'r') as file:
                        lines = file.readlines()
                        students = [line.strip() for line in lines[1:] if line.strip()]
                    populate_participants(f"data_{intensive_month_selected}/participants/{city}/participants.db", city, students)
            
                    incompleted_participants = []

                    if not incompleted_participants:
                        incompleted_participants = students

                    db_path = f"data_{intensive_month_selected}/participants/{city}/participants.db"
                    last_parced_student = get_last_parced_student(db_path)
                    if last_parced_student and last_parced_student in incompleted_participants: 
                        index = incompleted_participants.index(last_parced_student)
                        incompleted_participants = incompleted_participants[index:]

                    print(f"Parsing participants info in {city.capitalize()}")
                    

                    for i, participant in enumerate(incompleted_participants):
                        driver.get(f"https://edu.21-school.ru/profile/{participant}/about")

                        level = WebDriverWait(driver, 120).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='personalInfo.levelCode']"))
                        ).text[-1]

                        lvl_percent = driver.find_element(By.XPATH, "//div[@data-testid='personalInfo.experiencePercent']").text.replace("%", "")
                        exp = driver.find_element(By.XPATH, "//*[@data-testid='personalInfo.xp']").text.replace("XP", "")
                        logtime = WebDriverWait(driver, 60).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='attendanceWidget']"))
                        ).find_elements(By.XPATH, "./*")[1].find_elements(By.XPATH, "./*")[0].find_elements(By.XPATH, "./*")[-1].text

                        update_participant(db_path, participant, logtime, level, exp, lvl_percent, 0)
                        if i > 0:
                            set_last_parced_student(db_path, incompleted_participants[i - 1], 0)
                        set_last_parced_student(db_path, participant, 1)

                        # print(f"PRINTING HERE: {participant}, level: {level}, lvl_percent: {lvl_percent}%, exp: {exp} XP, logtime: {logtime}")




        except (TimeoutException, NoSuchElementException) as e:
            print(f"Login failed: {e}")
            return


    except (TimeoutException, NoSuchElementException) as e:
        print(f"Failed to login\n{e.msg}")
        return



def parse_personal_stats(url, username, password, auth_code, intensive_month_selected):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        time.sleep(5)
        if driver.current_url.startswith("https://auth.sberclass.ru"):
            try:
                username_field = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                password_field = driver.find_element(By.NAME, "password")
                button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

                username_field.send_keys(username)
                password_field.send_keys(password)
                button.click()

                # WebDriverWait(driver, 60).until(
                #     EC.url_contains("https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/login-actions/authenticate?execution")
                # )

                # print(driver.current_url)
               
                # code_field = WebDriverWait(driver, 60).until(
                #     EC.presence_of_element_located((By.XPATH, "//input[@name='otp' and @type='text']"))
                # )

                # code_field.click()

                # code_field.send_keys(auth_code)

                # button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

                # button.click()

                WebDriverWait(driver, 30).until(
                    EC.url_to_be("https://edu.21-school.ru/")
                )

                print("Login successful.")

            except Exception as e:
                print(f"Login failed: {e.msg}")
                return
            
            try:                
                def update_stats(campus, usernames):
                    db_path = f"data_{intensive_month_selected}/participants/{campus}/personal_stats.db"
                    # active_participants = get_active_student_list(f"data_{intensive_month_selected}/participants/{campus}/participants.db") or usernames
                    active_participants = usernames
                    last_parced_student = get_last_parced_student_personal_stats(db_path)
                    print("Last parsed student:", last_parced_student)
                    if last_parced_student in active_participants:
                        active_participants = active_participants[active_participants.index(last_parced_student):]



                    for i, participant in enumerate(active_participants):
                        driver.get(f"https://edu.21-school.ru/profile/{participant}/about")

                        level = WebDriverWait(driver, 120).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='personalInfo.levelCode']"))
                        ).text[-1]

                        lvl_percent = driver.find_element(By.XPATH, "//div[@data-testid='personalInfo.experiencePercent']").text.replace("%", "")
                        exp = driver.find_element(By.XPATH, "//*[@data-testid='personalInfo.xp']").text.replace("XP", "")

                        logtime = WebDriverWait(driver, 120).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='attendanceWidget']"))
                        ).find_elements(By.XPATH, "./*")[1].find_elements(By.XPATH, "./*")[0].find_elements(By.XPATH, "./*")[-1].text


                        see_all_projects_button = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//p[text()='See all projects']"))
                        )

                        see_all_projects_button.click()

                        time.sleep(3)

                        tasks_statuses = [element.text for element in driver.find_elements(By.XPATH, "//span[@data-testid='projects.projectItem.status']")]

                        accepted_projects = 0

                        for status in tasks_statuses:
                            if status.split()[0] == "Completed":
                                accepted_projects += 1

                        entertainment_events = 0
                        educational_events = 0

                        driver.get(f"https://edu.21-school.ru/profile/{participant}/achievements")

                        try:
                            education_event = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Educational event')]"))
                            )

                            if education_event:
                                educational_events = 1
                                try:
                                    parent_element = education_event.find_element(By.XPATH, "./..")
                                    needed_child = parent_element.find_element(By.CLASS_NAME, "jss595")
                                    if needed_child:
                                        needed_grandchildren = needed_child.find_elements(By.XPATH, './*')

                                        educational_events = int(needed_grandchildren[1].text)

                                except Exception:
                                    pass


                        except Exception:
                            pass
                            
                        try:
                            entertainment = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Entertainment event')]"))
                            )
                            if entertainment:
                                entertainment_events = 1
                                try:
                                    parent_element = entertainment.find_element(By.XPATH, "./..")
                                    needed_child = parent_element.find_element(By.CLASS_NAME, "jss595")
                                    if needed_child:
                                        needed_grandchildren = needed_child.find_elements(By.XPATH, './*')

                                    entertainment_events = int(needed_grandchildren[1].text)

                                except Exception:
                                    pass

                        except Exception:
                            pass

                        total_number_events = educational_events + entertainment_events

                        update_personal_stats(campus=campus, db_path=db_path, student=participant, logtime=float(logtime), exp=exp, total_tasks_accepted=accepted_projects, educational_events=educational_events, entertainment=entertainment_events, total_number_events=total_number_events)

                        if i > 0:
                            set_last_parced_student_personal_stats(campus, db_path, active_participants[i - 1], 0)
                        set_last_parced_student_personal_stats(campus, db_path, participant, 1)

                    
                        print(f"{participant}, logtime: {logtime}, lvl: {level} ({lvl_percent}%), exp: {exp} XP, accepted_projects: {accepted_projects}, educational events: {educational_events}, entertainment: {entertainment_events}, total num events: {total_number_events}")

                if os.path.exists(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv") and os.path.exists(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv"):
                    tashkent_students = fetch_students(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv")
                    samarkand_students = fetch_students(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv")
                    populate_personal_stats("tashkent", f"data_{intensive_month_selected}/participants/tashkent/personal_stats.db", tashkent_students)
                    populate_personal_stats("samarkand", f"data_{intensive_month_selected}/participants/samarkand/personal_stats.db", samarkand_students)

                    update_stats("tashkent", tashkent_students)
                    update_stats("samarkand", samarkand_students)
                    set_all_last_parced("tashkent")
                    set_all_last_parced("samarkand")


            except Exception as e:
                print(f"Failed to parse personal stats\n{e.msg}")
                return

            


    except (TimeoutException, NoSuchElementException) as e:
        print(f"Login failed: {e.msg}")
        return



def get_specific_project_complеtion_info(url, username, password, intensive_month_selected, auth_code, task):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)

    taskId, week = INTENSIVE[task]

    try:
        driver.get(url)
        time.sleep(5)

        if driver.current_url.startswith("https://auth.sberclass.ru"):
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                password_field = driver.find_element(By.NAME, "password")
                button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

                username_field.send_keys(username)
                password_field.send_keys(password)
                button.click()

                # WebDriverWait(driver, 10).until(
                #     EC.url_contains("https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/login-actions/authenticate?execution")
                # )

                # print(driver.current_url)

                # code_field = WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, "//input[@name='otp' and @type='text']"))
                # )
                # code_field.click()
                # code_field.send_keys(auth_code)

                # button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")
                # button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_to_be("https://edu.21-school.ru/")
                )

                print("Login successful.")

            except Exception as e:
                print(f"Login failed: {str(e)}") 
                return
            
        # for campus in ["tashkent", "samarkand"]:
        for campus in ["tashkent"]:
            db_path = f"data_{intensive_month_selected}/tasks/{campus}/{week}/{task}/{task}.db"
            all_students = get_all_students(f"data_{intensive_month_selected}/participants/{campus}/participants.db")

            print(len(all_students))

            if not os.path.exists(db_path):
                style_mem_table = None
                if task not in NO_STYLE_TASKS:
                    style_mem_table = 1
                init_table_for_task(db_path, style_mem_table=style_mem_table)
            populate_task_results(db_path, all_students)

            clang_format_failed = 0
            valgrind_failed = 0

            def clang_format_valgrind_results():
                clang_format_failed = 0
                valgrind_failed = 0
                try:
                    reviews_link = WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/nav/div/div/section[2]/div[2]/div/div/div[2]/div/a"))
                    )
                    if reviews_link.tag_name == 'a':
                        reviews_link.click()

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Could not find or click Reviews: {str(e)}") 
                    return

                try:
                    div_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='components.hint']"))
                    )
                    if div_elements:
                        last_div_element = div_elements[-1]
                        children = last_div_element.find_elements(By.XPATH, "./*")
                        full_text = ""
                        for child in children:
                            full_text += child.text + "\n"

                        style_test_results = re.findall(r"Style test: (.+)", full_text)
                        tests_failed = 0
                        for result in style_test_results:
                            print(f"Style test result: {result}")
                            if "FAIL" in result:
                                tests_failed += 1

                        if tests_failed > 0:
                            clang_format_failed += 1

                        memory_test_results = re.findall(r"Memory test: (.+)", full_text)
                        tests_failed = 0
                        for result in memory_test_results:
                            print(f"Memory test result: {result}")
                            if "FAIL" in result:
                                tests_failed += 1

                        if tests_failed > 0:
                            valgrind_failed += 1

                    return clang_format_failed, valgrind_failed

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Could not find the div with data-testid 'components.hint' of the student {student}: {str(e)}") 

            incompleted_students = list()
            null = get_student_task_result_by_status(db_path, "NULL")
            registered = get_student_task_result_by_status(db_path, "REGISTERED")
            assigned = get_student_task_result_by_status(db_path, "ASSIGNED")
            in_progress = get_student_task_result_by_status(db_path, "IN_PROGRESS")
            in_reviews = get_student_task_result_by_status(db_path, "IN_REVIEWS")

            if null:
                for student in null:
                    incompleted_students.append(student)
            elif registered:
                for student in registered:
                    incompleted_students.append(student)
            elif in_progress:
                for student in in_progress:
                    incompleted_students.append(student)
            elif in_reviews:
                for student in in_reviews:
                    incompleted_students.append(student)
            elif assigned:
                for student in assigned:
                    incompleted_students.append(student)


            for student in incompleted_students:
                driver.get(f"https://edu.21-school.ru/profile/{student}")

                try:
                    see_all_projects_button = WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, "//*[text()='See all projects']"))
                    )
                    see_all_projects_button.click()

                    time.sleep(3)

                    task_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//*[text()='{task}']"))
                    )
                    parent_div = task_button.find_element(By.XPATH, "./..")
                    status_line = parent_div.find_element(By.XPATH, "./span[@data-testid='projects.projectItem.status']").text

                    status = ""
                    if status_line.strip().split()[0] in ("Completed", "Failed"):
                        status_line = status_line.replace("(", "").replace(")", "").replace(",", "").replace("%", "").split()
                        status = status_line[0]
                    else:
                        status = status_line



                    title = task.upper()
                    line_to_print = f"student: {student}, title: {title}, status: {status}"

                    statuses = {
                        "Subscription is not available yet": "ASSIGNED",
                        "Subscription is open": "ASSIGNED",
                        "In progress": "IN_PROGRESS",
                        "Completed": "ACCEPTED",
                        "Failed": "FAILED",
                        "Ready to start": "REGISTERED"
                    }

                    
                    if status.startswith("Peer review"):
                        status = "IN_REVIEWS"
                    else:
                        status = statuses.get(status)
                        
                    reason = None
                    given_exp = None
                    final_percentage = None

                    if status in ("ACCEPTED", "FAILED"):
                        task_button.click()

                        try:
                            status_line = ""
                            reason = ""
                            if task.startswith('E'):
                                status_line = WebDriverWait(driver, 120).until(
                                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/aside/div[1]/div/span"))
                                ).text.replace("(", "").replace(")", "").replace(",", "").replace("%", "").split()
                                
                                reason = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/aside/div[1]/h4").text
                            else:
                                status_line = WebDriverWait(driver, 120).until(
                                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/aside/div[1]/div/div/span"))
                                ).text.replace("(", "").replace(")", "").replace(",", "").replace("%", "").split()
                
                                reason = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/aside/div[1]/div/h4").text

                            given_exp = status_line[1]
                            final_percentage = status_line[-1]

                            if reason == "Project failed" and task not in NO_STYLE_TASKS:
                                result = clang_format_valgrind_results()
                                if result[0] > 0 or result[1] > 0:
                                    if result[0] > 0 and result[1] > 0:
                                        clang_format_failed += result[0] 
                                    else:
                                        clang_format_failed += result[0]
                                        valgrind_failed += result[1]
                                    print(f"Total clang-format failures: {clang_format_failed}\nTotal valgrind failures: {valgrind_failed}")

                            line_to_print = f"student: {student}, title: {title}, status: {status}, reason: {reason}, given_exp: {given_exp} XP, final_percentage: {final_percentage}%"

                        except Exception as e:
                            print(f"Could not find the project: {str(e)}")
                    print(status)
                    update_task_result(db_path, student, title=title, status=status, reason=reason, given_exp=given_exp, final_score=final_percentage)
                    print(line_to_print)

                except Exception as e:
                    print(f"Could not find the project: {str(e)}")
            
            if task not in NO_STYLE_TASKS:
                update_styleValgrind(db_path=db_path, clang_format=clang_format_failed, valgrind=valgrind_failed)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()


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

def plot_failed_students(intensive_month_selected, task):
    _, week = INTENSIVE[task]


    for campus in ['tashkent', 'samarkand']:
        reasons = []
        db_path = f"data_{intensive_month_selected}/tasks/{campus}/{week}/{task}/{task}.db"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(f"SELECT reason FROM {task} WHERE status = 'FAILED'")
            reasons = [row[0] for row in cursor.fetchall()] 
        except sqlite3.Error as e:
            print(f"There was an error during parsing from task database {e}")

        reasons_variations = ['The project period has passed', 'Project failed', 'The project has been completed by surrender', 'Subscription for the project is already unavailable']

        if task not in NO_STYLE_TASKS:
            reasons_variations.extend(["valgrind", "clang-format"])

        reason_counts = Counter(reasons)
        labels = reason_counts.keys()
        sizes = reason_counts.values()

        translations = {
            'english': {
                'legend_title': 'Reasons',
                'title': "Reasons for Failed Students in",
                'failed tests title': 'Reasons for failed Verter autotests in',
                'The project period has passed': 'The project period has passed',
                'Project failed': 'Project was completed poorly',
                'The project has been completed by surrender': 'The project has been completed by surrender',
                'Subscription for the project is already unavailable': 'The students did not subscribe to the project',
                'You forgot to subscribe to the exam event': 'The students forgot to subscribe to the exam event',
                'You forgot to subscribe to the project and exam event': 'The students forgot to subscribe to the exam event',
                'You missed the exam': 'The students missed the exam',
                'The exam is failed': 'The exam is failed',
                'The exam is failed due to surrender': 'The exam is failed due to surrender',
                'valgrind': 'valgrind',
                'clang-format': 'clang-format'
            },
            'russian': {
                'legend_title': 'Причины',
                'title': "Причины провалов студентов в проекте",
                'failed tests title': 'Причины провалов в Verter автотесте в проекте',
                'The project period has passed': 'Срок сдачи проекта истек',
                'Project failed': 'Проект был плохо выполнен',
                'The project has been completed by surrender': 'Ученики нажали \'Give up project\'',
                'Subscription for the project is already unavailable': 'Ученики не подписались на проект',
                'You forgot to subscribe to the exam event': 'Не зарегистрировались на экзамен',
                'You forgot to subscribe to the project and exam event': 'Не зарегистрировались на экзамен',
                'You missed the exam': 'Пропустили экзамен',
                'The exam is failed': 'Экзамен провален',
                'The exam is failed due to surrender': 'Нажали \'Give up\' на экзамене',
                'valgrind': 'valgrind',
                'clang-format': 'clang-format'
            },
            'uzbek': {
                'legend_title': 'Sabablar',
                'title': "Talabalar muvaffaqiyatsizlik sabablar",
                'failed tests title': 'Verter autotestlarida muvaffaqiyatsizlik sabablar',
                'The project period has passed': 'Loyiha muddati tugadi',
                'Project failed': 'Loyiha yomon bajarildi',
                'The project has been completed by surrender': 'Loyiha topshirildi',
                'Subscription for the project is already unavailable': 'Talabalar loyihaga obuna bo\'lishmadi',
                'You forgot to subscribe to the exam event': 'Imtihonga registir kilinmagan',
                'You forgot to subscribe to the project and exam event': 'Imtihonga registir kilinmagan',
                'You missed the exam': 'Imtihonga kelmagan',
                'The exam is failed': 'Imtihondan otolmadi',
                'The exam is failed due to surrender': '\'Give up\' boskan',
                'valgrind': 'valgrind',
                'clang-format': 'clang-format'
            }
        }
        clang_format = 0
        valgrind = 0

        if task not in NO_STYLE_TASKS:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute(f"SELECT clang_format, valgrind FROM styleValgrind WHERE id = 1")
                result = cursor.fetchall()
                clang_format = result[0][0]
                valgrind = result[0][1]
            except sqlite3.Error as e:
                print(f"There was an error during parsing from task database {e}")

            print(f"Clang-format {clang_format}")
            print(f"Valgrind {valgrind}")

        for lang, translation in translations.items():
            translated_labels = [translation[label] for label in labels]
            plt.figure(figsize=(10, 7))
            wedges, _, autotexts = plt.pie(sizes, labels=None, autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title(f"{translation['title']} {task} ({campus.capitalize()})")

            # Add legend
            plt.legend(wedges, translated_labels, title=translations[lang]['legend_title'], loc="center left", bbox_to_anchor=(0.72, 0.5), fontsize='small')

            if not os.path.exists(f"data_{intensive_month_selected}/tasks/{campus}/{week}/{task}/images"):
                os.mkdir(f"data_{intensive_month_selected}/tasks/{campus}/{week}/{task}/images/")
                print("Directory has been created")

            plt.savefig(f"data_{intensive_month_selected}/tasks/{campus}/{week}/{task}/images/failed_reasons_{lang}.png")
            plt.clf()


            if task not in NO_STYLE_TASKS:
                # Plot clang_format and valgrind failed students
                project_failed_count = reason_counts.get('Project failed', 0)
                other_failed_count = project_failed_count - (clang_format + valgrind)
                failed_reasons = {
                translation['Project failed']: other_failed_count,
                'clang-format': clang_format,
                'valgrind': valgrind
                }

                plt.figure(figsize=(10, 7))
                wedges, _, autotexts = plt.pie(failed_reasons.values(), labels=None, autopct='%1.1f%%', startangle=140)
                plt.axis('equal')
                plt.title(f"{translation['failed tests title']} {task} ({campus.capitalize()})")

                plt.legend(wedges, failed_reasons.keys(), title=translations[lang]['legend_title'], loc="center left", bbox_to_anchor=(0.72, 0.5), fontsize='small')

                plt.savefig(f"data_{intensive_month_selected}/tasks/{campus}/{week}/{task}/images/failed_tests_{lang}.png")
                plt.clf()


        
def update_read_databases():
    for city in ["tashkent", "samarkand"]:
        if os.path.exists(f"data_{intensive_month_selected}/participants/{city}/intensiv_participants.csv"):
            students = []
            with open(f"data_{intensive_month_selected}/participants/{city}/intensiv_participants.csv", 'r') as file:
                lines = file.readlines()
                students = [line.strip() for line in lines[1:] if line.strip()]
            populate_participants(f"data_{intensive_month_selected}/participants_to_read/{city}/participants.db", city, students)

    tashkent_students = fetch_students(f"data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv")
    samarkand_students = fetch_students(f"data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv")
    populate_personal_stats("tashkent", f"data_{intensive_month_selected}/participants_to_read/tashkent/personal_stats.db", tashkent_students)
    populate_personal_stats("samarkand", f"data_{intensive_month_selected}/participants_to_read/samarkand/personal_stats.db", samarkand_students)


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
        lvl_percent = student[4]

        update_participant(db_path=f"data_{intensive_month_selected}/participants_to_read/tashkent/participants.db", student=username, logtime=logtime, level=level, exp=exp, lvl_percent=lvl_percent)
        print(f"The student {username} has been updated in particiapants in Tashkent")
    
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "tashkent", 0)

    #set being updated 1 for samarkand
    set_being_updated(f"data_{intensive_month_selected}/participants_to_read/overall.db", "samarkand", 1)
    for student in students_samarkand:
        username = student[0]
        logtime = student[1]
        level = student[2]
        exp = student[3]
        lvl_percent = student[4]

        update_participant(db_path=f"data_{intensive_month_selected}/participants_to_read/samarkand/participants.db", student=username, logtime=logtime, level=level, exp=exp, lvl_percent=lvl_percent)
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




def plot_exam_progress(campus, intensive_month_selected):
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

        progress = e02d12 - e03d19
        fall = e03d19 - e02d12
        instability = max(scores) - min(scores)

        unstable_students.append((student, instability, scores))
        most_progress_students.append((student, progress, scores))
        biggest_fall_students.append((student, fall, scores))


    unstable_students = sorted(unstable_students, key=lambda x: x[1], reverse=True)[:5]
    most_progress_students = sorted(most_progress_students, key=lambda x: x[1], reverse=True)[:5]
    biggest_fall_students = sorted(biggest_fall_students, key=lambda x: x[1], reverse=True)[:5]

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




def main():
    if len(sys.argv) == 4:
        username = os.getenv('API_USERNAME')
        password = os.getenv('API_PASSWORD')

        website_url = "https://edu.21-school.ru"
        
        auth_code = sys.argv[3] 

        if sys.argv[2] not in INTENSIVE_MONTHS:
            raise Exception(f"The entered month is not among the intensive months")
        
        intensive_month_selected = sys.argv[2]

        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))



        if sys.argv[1] == "parse_students":
            # parse_student_info(website_url, username, password, auth_code, intensive_month_selected)
            parse_personal_stats(website_url, username, password, auth_code, intensive_month_selected)
            update_read_databases()

        elif sys.argv[1] == "parse_exam_progress":
        
            sort_students_exam_progress(f"data_{intensive_month_selected}/participants/tashkent/participants.db", "tashkent", intensive_month_selected)
            sort_students_exam_progress(f"data_{intensive_month_selected}/participants/samarkand/participants.db", "samarkand", intensive_month_selected)
            plot_exam_progress("tashkent", intensive_month_selected)
            plot_exam_progress("samarkand", intensive_month_selected)

        if sys.argv[1] not in ("parse_students", "parse_exam_progress"):
            task = sys.argv[1]
            if sys.argv[1] not in INTENSIVE:
                raise Exception(f"The entered task is not among the intensive tasks")


            update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=1)
            
            get_specific_project_complеtion_info(website_url, username, password, intensive_month_selected, auth_code, task)
            update_posts_db(task, intensive_month_selected)

            update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=0)
            plot_failed_students(intensive_month_selected, task)


if __name__ == "__main__":
    main()

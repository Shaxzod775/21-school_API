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

from db_modules.db_api import * 

import time
from configs.config_api import *

def parse_student_info(url, username, password, intensive_month_selected):
    auth_code = input("Пожалуйста введите пароль для двухэтапной аутентификации: ")
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

                WebDriverWait(driver, 10).until(
                    EC.url_contains("https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/login-actions/authenticate?execution")
                )

                print(driver.current_url)
               
                code_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='otp' and @type='text']"))
                )

                code_field.click()

                code_field.send_keys(auth_code)

                button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

                button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_to_be("https://edu.21-school.ru/")
                )

                print("Login successful.")


                # WebDriverWait(driver, 10).until(
                #     EC.url_to_be("https://edu.21-school.ru/")
                # )

                # print("Login successful.")

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Login failed: {e.msg}")
                return
        
        try:
            for city in ["tashkent", "samarkand"]:
                if os.path.exists(f"data_{intensive_month_selected}/participants/{city}/intensiv_participants.csv"):
                    students = []
                    with open(f"data_{intensive_month_selected}/participants/{city}/intensiv_participants.csv", 'r') as file:
                        students = [line.strip() for line in file.readlines() if line.strip()]
                    populate_participants(f"data_{intensive_month_selected}/participants/{city}/participants.db", city, students)
            
                    incompleted_participants = get_incompleted_participants(city)

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

                        level = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='personalInfo.levelCode']"))
                        ).text[-1]

                        lvl_percent = driver.find_element(By.XPATH, "//div[@data-testid='personalInfo.experiencePercent']").text[0]
                        try:
                            exp = WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((By.XPATH, "//*[@data-testid='personalInfo.xp']"))
                            ).text
                        except TimeoutException:
                            exp = "N/A"


                        try:
                            svg_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//svg[@xmlns='http://www.w3.org/2000/svg']"))
                            )
                            svg_text = svg_element.text
                        except TimeoutException:
                            svg_text = "N/A"

                        print("SVG svg_text: ", svg_text)

                        print(f"{participant}, level: {level, lvl_percent}%, exp: {exp}")

                    #     response_basic_info = requests.get(BASE_URL.format(f"/participants/{participant}"), headers=HEADERS)
                    #     time.sleep(0.5)
                    #     response_logtime = requests.get(BASE_URL.format(f"/participants/{participant}/logtime?date={date_to_use}"), headers=HEADERS)

                    #     if response_logtime.status_code == 200 and response_basic_info.status_code == 200:
                    #         logtime = float(response_logtime.text)
                    #         info = json.loads(response_basic_info.text)
                    #         update_participant(db_path, participant, logtime=logtime, level=info['level'], exp=info['expValue'], exp_to_next_level=info['expToNextLevel'])
                    #         print(f"Student {participant} has been updated in {campus.capitalize()}")
                    #         if i > 0:
                    #             set_last_parced_student(db_path, incompleted_participants[i - 1], 0)
                    #         set_last_parced_student(db_path, participant, 1)
                    #         print(f'{participant}, {logtime}, {info["level"]}, {info["expValue"]}, {info["expToNextLevel"]}')
                    #         time.sleep(1)

                    # if get_last_parced_student(db_path) == incompleted_participants[-1]:
                    #     set_last_parced_student(db_path, incompleted_participants[-1], 0)

                    # parse_participants("tashkent", tashkent_students_usernames)
                    # parse_participants("samarkand", samarkand_students_usernames)





        #     username_field = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.NAME, "username"))
        #     )
        #     password_field = driver.find_element(By.NAME, "password")
        #     button = driver.find_element(By.CLASS_NAME, "jss22").find_element(By.TAG_NAME, "button")

        #     username_field.send_keys(username)
        #     password_field.send_keys(password)
        #     button.click()

        #     WebDriverWait(driver, 10).until(
        #         EC.url_to_be("https://edu.21-school.ru/")
        #     )

        #     print("Login successful.")

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Login failed: {e}")
            return



    except (TimeoutException, NoSuchElementException) as e:
        print(f"Failed to login\n{e.msg}")
        return





def main():
    if len(sys.argv) == 3:
        if sys.argv[2] not in INTENSIVE_MONTHS:
            raise Exception(f"The entered month is not among the intensive months")
        
        intensive_month_selected = sys.argv[2]

        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

        username = os.getenv('API_USERNAME')
        password = os.getenv('API_PASSWORD')

        website_url = "https://edu.21-school.ru"


        if sys.argv[1] == "parse_students":
            parse_student_info(website_url, username, password, intensive_month_selected)
        #     parse_personal_stats(token, intensive_month_selected)
        #     update_read_databases()

        # elif sys.argv[1] == "parse_exam_progress":
        
        #     sort_students_exam_progress(f"data_{intensive_month_selected}/participants/tashkent/participants.db", "tashkent")
        #     sort_students_exam_progress(f"data_{intensive_month_selected}/participants/samarkand/participants.db", "samarkand")
        #     plot_exam_progress("tashkent")
        #     plot_exam_progress("samarkand")

        # if sys.argv[1] not in ("parse_students", "parse_exam_progress"):
        #     if sys.argv[1] not in INTENSIVE:
        #         raise Exception(f"The entered task is not among the intensive tasks")

        #     task = sys.argv[1]

        #     update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=1)

        #     get_api_token()
        #     token = get_file_token()
        
        #     if not os.path.exists(f'data_{intensive_month_selected}/campuses/campuses.csv'):
        #         get_list_of_campuses_api(token)
            
        #     tashkent_id = get_specific_campus_id("tashkent", intensive_month_selected)
        #     samarkand_id = get_specific_campus_id("samarkand", intensive_month_selected)
                

        #     if not os.path.exists(f'data_{intensive_month_selected}/coalitions/tashkent/intensiv_coalitions.csv') or not os.path.exists(f'data_{intensive_month_selected}/coalitions/samarkand/intensiv_coalitions.csv') :
        #         get_coatlitions_api(token, tashkent_id, 'tashkent')
        #         get_coatlitions_api(token, samarkand_id, 'samarkand')

        #     if not os.path.exists(f'data_{intensive_month_selected}/participants/tashkent/intensiv_participants.csv') or not os.path.exists(f'data_{intensive_month_selected}/participants/samarkand/intensiv_participants.csv'):
        #         get_all_intensiv_participants_api(token)

            


        #     get_specific_project_complеtion_info(token, str(project_id), week, task, intensive_month_selected)
        #     update_posts_db(task, intensive_month_selected)

            # update_task(db_path=f"data_{intensive_month_selected}/tasks.db", task=task, being_parsed=0)


if __name__ == "__main__":
    main()

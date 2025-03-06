from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import re

def load_edu_page(url, username, password, students):
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)

    couldnt_find_reviews = []

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
                    EC.url_to_be("https://edu.21-school.ru/")
                )

                print("Login successful.")

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Login failed: {e}")
                return

        clang_format_failed = 0
        valgrind_failed = 0


        for student in students:
            driver.get(f"https://edu.21-school.ru/profile/{student}/project/19162/evaluations")

            try:
                reviews_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[text()='Reviews']"))
                )

                if reviews_link.tag_name == 'a':
                    reviews_link.click()

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Could not find or click Reviews: {e}")
                return

            print("'a' reviews is found!")

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

                    # Extract style test results
                    style_test_results = re.findall(r"Style test: (.+)", full_text)
                    tests_failed = 0
                    for result in style_test_results:
                        print(f"Style test result: {result}")
                        if "FAIL" in result:
                            tests_failed += 1

                    if tests_failed == 5:
                        clang_format_failed += 1
                    print(f"Total style test failures: {clang_format_failed}")


                    # Extract memory test results
                    memory_test_results = re.findall(r"Memory test: (.+)", full_text)
                    tests_failed = 0
                    for result in memory_test_results:
                        print(f"Memory test result: {result}")
                        if "FAIL" in result:
                            tests_failed += 1


                    if tests_failed == 5:
                        valgrind_failed += 1

                    print(f"Total memory test failures: {valgrind_failed}")

            except (TimeoutException, NoSuchElementException) as e:
                couldnt_find_reviews.append(student)
                print(f"Could not find the div with data-testid 'components.hint' of the student {student}: {e}")

        print(f"Total clang-format failures: {clang_format_failed}")
        print(f"Total valgrind failures: {valgrind_failed}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print(couldnt_find_reviews)
        driver.quit()

def main():
    website_url = "https://edu.21-school.ru"
    your_username = "glassole"
    your_password = "Sh7757723!"

    students = [
    'abbiehil',
    'ahaivida',
    'antioned',
    'aristotl',
    'arthormi',
    'bagshotk',
    'bambithe',
    'belaquoa',
    'binkscha',
    'bluesdan',
    'bobbicel',
    'breaadvi',
    'builderm',
    'bullockk',
    'bullrodr',
    'bumpdiam',
    'calebsou',
    'changspi',
    'cherrira',
    'cleorame',
    'collioka',
    'cordiaho',
    'daceyhaz',
    'dafynqyb',
    'dameronm',
    'darcieje',
    'darciekr',
    'davidach',
    'davossti',
    'dejaswyf',
    'dillyjad',
    'dodriocu',
    'drummshe',
    'endadean',
    'eufemiaz',
    'eusebiof',
    'exienore',
    'farrowro',
    'fixiefal',
    'floriadi',
    'friarear',
    'fringshi',
    'furstana',
    'garnetjo',
    'garrettg',
    'gaytejan',
    'gazlowed',
    'gerrerat',
    'ghishybr',
    'ghulbets',
    'gilldenn',
    'grasslim',
    'greggjos',
    'grootism',
    'gurneyhe',
    'halinalu',
    'harethch',
    'headburl',
    'hermanpo',
    'hildadea',
    'hosmanvi',
    'ildanyst',
    'imeldasa',
    'iraidaar',
    'jaleesar',
    'josethla',
    'kalacaro',
    'kegswife',
    'knightbu',
    'kudzumor',
    'laborlis',
    'larkcord',
    'latinaco',
    'lavellen',
    'lawannas',
    'leotasna',
    'leroykel',
    'levelmyr',
    'lisafert',
    'lorenesu',
    'lorimers',
    'luyaione',
    'mallieva',
    'maokaisa',
    'marleens',
    'marqrosa',
    'marthmaj',
    'marxfior',
    'mellydae',
    'melvinap',
    'meterryt',
    'mireille',
    'mirianhi',
    'monteala',
    'moroamer',
    'murkyqui',
    'myrnamag',
    'narcissa',
    'nidiabea',
    'nutethin',
    'offalsun',
    'olliewhi',
    'orivelam',
    'orvillej',
    'ossiemar',
    'palmerth',
    'pepperlu',
    'petyrman',
    'pizzajel',
    'poochieb',
    'procyonh',
    'profitjo',
    'quincymi',
    'rashadle',
    'roadfral',
    'rockkohl',
    'roggoson',
    'rosyophe',
    'rudolphf',
    'sallyale',
    'sallyarc',
    'sandiebl',
    'sandiesh',
    'satanele',
    'scarbsil',
    'sewerele',
    'shaddamh',
    'shanelau',
    'sharanma',
    'silvanah',
    'silvialu',
    'simmonsc',
    'sindyalq',
    'skyrimsi',
    'smokedsi',
    'snowbabi',
    'solebenn',
    'stanleyj',
    'stridere',
    'strongty',
    'sulusamu',
    'syriohal',
    'tandyvip',
    'teodorab',
    'teraxiom',
    'teresaap',
    'thattfro',
    'thelmati',
    'theyregi',
    'tigrarub',
    'tildache',
    'toombezh',
    'torrigri',
    'torwoldf',
    'tracerci',
    'traceref',
    'ultrabor',
    'veezardo',
    'velmagar',
    'velvetap',
    'venettad',
    'vipirnet',
    'waitemal',
    'whitneys',
    'xochitlb',
    'zarquonb'
]

    load_edu_page(website_url, your_username, your_password, students)

if __name__ == "__main__":
    main()
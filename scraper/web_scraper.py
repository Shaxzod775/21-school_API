from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import re

def load_edu_page(url, username, password, students, task):
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
            driver.get(f"https://edu.21-school.ru/profile/{student}")

            try:
                see_all_projects_button = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//*[text()='See all projects']"))
                )

                see_all_projects_button.click()

                task_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[text()='{task}']"))
                )

                task_button.click()


            except Exception:
                print(f"Could not find the project: {e}")

            try:
                

                reviews_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[text()='Reviews']"))
                )

                if reviews_link.tag_name == 'a':
                    reviews_link.click()

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Could not find or click Reviews: {e}")
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

# aemonsig
# alliseet
# annattoa
# audreajo
# beckioph
# bethannl
# boothjae
# bowendar
# breannav
# brenetts
# burtinga
# carisayo
# carmahan
# carrowek
# caryearn
# chancech
# cheddarn
# cherishd
# chingunc
# cieraarg
# clydemai
# cobbleri
# collineg
# correyer
# cousinch
# creolaca
# cyndiwil
# dancerlu
# danutael
# deadrato


def main():
    website_url = "https://edu.21-school.ru"
    your_username = "glassole"
    your_password = "Sh7757723!"

    students = [
    "alvinaaz",
    "annattoa",
    "annikagy",
    "armandow",
    "beckioph",
    "bodecoll",
    "burtinga",
    "caroleii",
    "caryearn",
    "celindag",
    "cherishd",
    "corellab",
    "coriejal",
    "cousinch",
    "creenwen",
    "deanncla",
    "dennetfr",
    "dianatan",
    "dookumur",
    "eldriena",
    "gengarma",
    "gerrehel",
    "goblinpo",
    "goylesea",
    "hortonjo",
    "jarredwa",
    "jazminis",
    "jenicece",
    "jinnysor",
    "leighahe",
    "lomokraz",
    "lottnorb",
    "lyannafe",
    "mackhors",
    "magaretm",
    "mainesmy",
    "malonehi",
    "manceste",
    "manilowa",
    "margartd",
    "marianaj",
    "marlineb",
    "marrygle",
    "martacha",
    "masakopo",
    "maximest",
    "medeaali",
    "mellaraa",
    "merrybri",
    "metapodk",
    "metapodp",
    "michaerm",
    "michealc",
    "migashir",
    "milissat",
    "mitziebr",
    "moffmoro",
    "moltenvi",
    "moranmjo",
    "morganni",
    "mornecam",
    "mycahvec",
    "myunggro",
    "naidaarm",
    "nailstou",
    "nancidou",
    "natoshaw",
    "needfule",
    "nievesma",
    "nikitael",
    "nikolear",
    "niranyes",
    "nordervo",
    "nyotawar",
    "oberynpy",
    "odessalo",
    "olincomm",
    "oliveslu",
    "ollidore",
    "orgnarda",
    "orlandsp",
    "oswellas",
    "owenmorw",
    "oystersf",
    "paprikho",
    "peanutsc",
    "pearseta",
    "pecorink",
    "pemfordj",
    "pibblesc",
    "pigeonpo",
    "pingrhod",
    "pintofau",
    "plackgan",
    "pontusjo",
    "ponytapi",
    "profitbo",
    "qothoyae",
    "quenceza",
    "quentonl",
    "quincyse",
    "raisaemm",
    "rambtoco",
    "raneyhun",
    "raynejig",
    "redwynsw",
    "renfredm",
    "rexxarwi",
    "rhaellac",
    "rhodesla",
    "robbyjab",
    "roellevo",
    "rosalbal",
    "rosannem",
    "rosbykat",
    "roseypib",
    "rowangra",
    "roxannwi",
    "ruittgir",
    "ruthabea",
    "ruthelma",
    "ryannwin",
    "ryzearge",
    "sandserr",
    "sanjayjo",
    "sarabath",
    "saranoth",
    "scarypip",
    "schauerq",
    "septicli",
    "seymourt",
    "shalager",
    "shanarat",
    "shanekam",
    "shanikaw",
    "sharellt",
    "sharilye",
    "shawnase",
    "shazamel",
    "sheilahf",
    "shellawa",
    "shireisu",
    "shperezo",
    "sklueang",
    "soldtoma",
    "sophieau",
    "spectref",
    "staceyfe",
    "staciero",
    "stephenr",
    "stooploc",
    "sybellek",
    "sybillcl",
    "systemme",
    "tainacat",
    "takeruka",
    "tamalaca",
    "tammyyol",
    "tarberel",
    "tarentom",
    "tashiaob",
    "teenyjai",
    "thersami",
    "thoraher",
    "thormorc",
    "thorossa",
    "thuyfera",
    "tierrawa",
    "tildeele",
    "timothyv",
    "toadfile",
    "todricch",
    "tomikach",
    "toppingp",
    "toppingy",
    "toshikod",
    "tracieme",
    "trundler",
    "tuvokron",
    "urgotkur",
    "venitaco",
    "vinitase",
    "vronemer",
    "wadeadal",
    "waspdaug",
    "weirdlan",
    "wifebike",
    "wileyoni",
    "winkywar",
    "woodensh",
    "wraithlo",
    "wynchulm",
    "xayahtho",
    "ygrittem",
    "yingcleg",
    "yingurri",
    "youtaoly",
    "ytramsgu",
    "yucciena",
    "zapelhug",
    "zarquonk",
    "zellashi",
    "zenzthem",
    "zoltanal",
    "zucchinr"]

    load_edu_page(website_url, your_username, your_password, students, "T03D03")

if __name__ == "__main__":
    main()
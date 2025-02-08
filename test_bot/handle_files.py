import sys
sys.path.append("..")

from api.main import *
from config_api import *

from config import *
from telegram.helpers import escape_markdown
from posts import *
from db import *

def read_main_csv(filepath):
    with open(filepath, "r+") as file:
        line = file.readline()
        lines = list()
        while line:
            line = file.readline()
            lines.append(line.strip())

    return lines[:len(lines) - 1]

def make_report(task):
    _return = dict()
    _, week = INTENSIVE[task]

    if os.path.exists(f'../api/data/tasks/{week}/{task}/{task}.csv') == False:
        return "Репорт ещё не готов"

    passed_students, _, scored_didnt_pass, scored_hundred_percent, num_of_students, acceptance_rate, in_progress, in_reviews, registered = sort_task_data(f'../api/data/tasks/{week}/{task}/{task}.csv')

    _return['passed_students'] = [[student.split(',')[0], student.split(',')[-1]] for student in passed_students]
    _return['scored_hundred'] = [[student.split(',')[0], student.split(',')[-1]] for student in scored_hundred_percent]
    _return['scored_didnt_pass'] = [[student.split(',')[0], student.split(',')[-1]] for student in scored_didnt_pass] 
    _return['in_progress'] = [[student.split(',')[0], student.split(',')[-1]] for student in in_progress] 
    _return['in_reviews'] = [[student.split(',')[0], student.split(',')[-1]] for student in in_reviews] 
    _return['registered'] = [[student.split(',')[0], student.split(',')[-1]] for student in registered] 


    report = list()
    report.append("Репорт:\n\n")
    if in_progress:
        report.append(f"{len(in_progress)} записались на проэкт\n")

    if in_reviews:
        report.append(f"{len(in_reviews)} завершили проэкт и сейчас проходят проверку\n")

    if passed_students:
        report.append(f"Из {num_of_students} учеников только {len(passed_students)} смогли сдать этот проэкт\n\n")

    if scored_didnt_pass:
        report.append(f"{len(scored_didnt_pass)} сделали хотя бы одно задание, но не смогли сдать проэкт\n\n")

    if acceptance_rate:
        report.append(f"Процент проходимости: {acceptance_rate:.2f}%\n\n")

    if passed_students:
        report.append("Поздравления всем сдавшим ребятам!\n\n")

    _return['report'] = "".join(report)
    

    return _return
        
        

# print(read_main_csv("../api/data/tasks/1_week/P01D06/P01D06.csv"))
# print(make_report("E01D05"))



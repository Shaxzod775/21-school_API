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

def make_report(task, language):
    if language not in ("english", "russian", "uzbek"):
        raise Exception(f"The report cannot be displayed in that language! {language}")

    _return = dict()
    _, week = INTENSIVE[task]

    filepath = f'../api/data/tasks/{week}/{task}/{task}.csv'
    if not os.path.exists(filepath):
        return "Report is not yet ready" if language == "english" else "Отчет еще не готов" if language == "russian" else "Hisobot hali tayyor emas"

    passed_students, _, scored_didnt_pass, scored_hundred_percent, num_of_students, acceptance_rate, in_progress, in_reviews, registered = sort_task_data(filepath)

    _return['passed_students'] = [[student.split(',')[0], student.split(',')[-1]] for student in passed_students]
    _return['scored_hundred'] = [[student.split(',')[0], student.split(',')[-1]] for student in scored_hundred_percent]
    _return['scored_didnt_pass'] = [[student.split(',')[0], student.split(',')[-1]] for student in scored_didnt_pass]
    _return['in_progress'] = [[student.split(',')[0], student.split(',')[-1]] for student in in_progress]
    _return['in_reviews'] = [[student.split(',')[0], student.split(',')[-1]] for student in in_reviews]
    _return['registered'] = [[student.split(',')[0], student.split(',')[-1]] for student in registered]

    report = list()
    report.append({"english": "Report:\n\n", "russian": "Отчет:\n\n", "uzbek": "Hisobot:\n\n"}[language])

    if in_progress:
        report.append({
            "english": f"{len(in_progress)} students signed up for the project\n",
            "russian": f"{len(in_progress)} записались на проект\n",
            "uzbek": f"{len(in_progress)} talaba loyihaga yozildi\n"
        }[language])

    if in_reviews:
        report.append({
            "english": f"{len(in_reviews)} students completed the project and are now under review\n\n",
            "russian": f"{len(in_reviews)} завершили проект и сейчас проходят проверку\n\n",
            "uzbek": f"{len(in_reviews)} talaba loyihani yakunladi va hozir tekshiruvdan o'tmoqda\n\n"
        }[language])

    if passed_students:
        report.append({
            "english": f"Out of {num_of_students} students, only {len(passed_students)} were able to pass this project\n\n",
            "russian": f"Из {num_of_students} учеников только {len(passed_students)} смогли сдать этот проект\n\n",
            "uzbek": f"{num_of_students} talabadan faqat {len(passed_students)} tasi ushbu loyihani topshira oldi\n\n"
        }[language])

    if scored_didnt_pass:
        report.append({
            "english": f"{len(scored_didnt_pass)} students completed at least one task but could not pass the project\n\n",
            "russian": f"{len(scored_didnt_pass)} сделали хотя бы одно задание, но не смогли сдать проект\n\n",
            "uzbek": f"{len(scored_didnt_pass)} talaba kamida bitta topshiriqni bajardi, lekin loyihani topshira olmadi\n\n"
        }[language])

    if acceptance_rate:
        report.append({
            "english": f"Pass rate: {acceptance_rate:.2f}%\n\n",
            "russian": f"Процент проходимости: {acceptance_rate:.2f}%\n\n",
            "uzbek": f"O'tish koeffitsienti: {acceptance_rate:.2f}%\n\n"
        }[language])

    if passed_students:
        report.append({
            "english": "Congratulations to all the students who passed!\n\n",
            "russian": "Поздравления всем сдавшим ребятам!\n\n",
            "uzbek": "Barcha topshirgan talabalarni tabriklaymiz!\n\n"
        }[language])

    _return['report'] = "".join(report)

    return _return
        
        

# print(read_main_csv("../api/data/tasks/1_week/P01D06/P01D06.csv"))
# print(make_report("E01D05"))



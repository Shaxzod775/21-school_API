import sys
sys.path.append("..")

from api.main import *
from config_api import *

from config import *
from telegram.helpers import escape_markdown
from posts import *
from db import *
from db_modules.db_api import *

def read_main_csv(filepath):
    with open(filepath, "r+") as file:
        line = file.readline()
        lines = list()
        while line:
            line = file.readline()
            lines.append(line.strip())

    return lines[:len(lines) - 1]

def make_report(task, language, campus_arg):
    if language not in ("english", "russian", "uzbek"):
        raise Exception(f"The report cannot be displayed in that language! {language}")

    _return = dict()
    _, week = INTENSIVE[task]

    _return['campus'] = campus_arg

    _, being_parsed, start_date, _ = get_task(task, "../api/data/tasks.db")

    current_datetime = datetime.datetime.now()

    if start_date:
        start_datetime_converted = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        
        if start_datetime_converted > current_datetime:
            return {'report': {  
                "english": "The start time for the task has not come yet",
                "russian": "Время старта задание ещё не пришло",
                "uzbek": "Topshiriq boshlanish vaqti hali kelmadi"
            }[language], "report_ready": False}
    
        if bool(being_parsed):
            return {'report': {  
                "english": "The report is being made",
                "russian": "Отчет готовится",
                "uzbek": "Hisobot tayyorlanyapti"
            }[language], "report_ready": False}
            

    filepath = f'../api/data/tasks/{campus_arg}/{week}/{task}/{task}.db'
    if not os.path.exists(filepath):
        return {'report': {  
            "english": "Report is not yet ready",
            "russian": "Отчет еще не готов",
            "uzbek": "Hisobot hali tayyor emas"
        }[language], "report_ready": False}
    
    passed_students, _, scored_didnt_pass, scored_hundred_percent, num_of_students, acceptance_rate, in_progress, in_reviews, registered = sort_task_data(filepath)

    _return['passed_students'] = [[student['student'], student['final_score']] for student in passed_students]
    _return['scored_hundred'] = [[student['student'], student['final_score']] for student in scored_hundred_percent]
    _return['scored_didnt_pass'] = [[student['student'], student['final_score']] for student in scored_didnt_pass]
    _return['in_progress'] = [[student['student'], student['final_score']] for student in in_progress]
    _return['in_reviews'] = [[student['student'], student['final_score']] for student in in_reviews]
    _return['registered'] = [[student['student'], student['final_score']] for student in registered]

    if language == "russian": 
            campus_language_specified = "Ташкент" if campus_arg == "tashkent" else "Самарканд"
    else:
        campus_language_specified = campus_arg.capitalize()


    report = list()
    report.append({
        "english": f"Report ({task}) in {campus_language_specified}:\n\n",
        "russian": f"Отчет ({task}) в {campus_language_specified}e:\n\n",
        "uzbek": f"Hisobot ({task}) {campus_language_specified}da:\n\n"
    }[language])

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



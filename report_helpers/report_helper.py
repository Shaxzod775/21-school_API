import sys
sys.path.append("..")

import os
# from api.main import *
from test_bot.config_api import *

from telegram.helpers import escape_markdown
from test_bot.posts import *
from db_modules.db import *
from db_modules.db_api import *
from sorting_data.sort_helper import *


from db_modules.db import get_post, create_post 
from configs.config_bot import TELEGRAPH_TOKEN
import time

def read_main_csv(filepath):
    with open(filepath, "r+") as file:
        line = file.readline()
        lines = list()
        while line:
            line = file.readline()
            lines.append(line.strip())

    return lines[:len(lines) - 1]

def make_report(task, language, campus_arg, db_path, updating):
    if language not in ("english", "russian", "uzbek"):
        raise Exception(f"The report cannot be displayed in that language! {language}")

    _return = dict()
    _, week = INTENSIVE[task]

    _return['campus'] = campus_arg

    _, being_parsed, start_date, _ = get_task(task, db_path)

    current_datetime = datetime.datetime.now()

    if start_date:
        start_datetime_converted = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        
        if start_datetime_converted > current_datetime:
            return {'report': {  
                "english": "The start time for the task has not come yet",
                "russian": "Время старта задание ещё не пришло",
                "uzbek": "Topshiriq boshlanish vaqti hali kelmadi"
            }[language], "report_ready": False}
    
        if not bool(updating): 
            if bool(being_parsed):
                return {'report': {  
                    "english": "The report is being made",
                    "russian": "Отчет готовится",
                    "uzbek": "Hisobot tayyorlanyapti"
                }[language], "report_ready": False}
            

    filepath = f'../api/data_{intensive_month_selected}/tasks/{campus_arg}/{week}/{task}/{task}.db'
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
        
        
def make_profile_report(language, campus, db_path, student):
    result = sort_personal_stats(db_path, campus, student)

    if result is None:  # Handle the case where the student is not found
        return {
            "english": "❌ You are either not a intensive participant of the current intensive or you have chosen the wrong campus ❌",
            "russian": "❌ Вы либо участник не участник текущего интенсива, либо выбрали не свой кампус ❌",
            "uzbek": "❌ Siz yoki joriy intensiv ishtirokchisi emassiz, yoki o'z kampusizni tanlamadingiz ❌"
        }[language]
    
    if result == "being updated":
        return {
            "english": "The database is being updated. Please check your profile in a minute.",
            "russian": "База данных обновляется. Пожалуйста зайдите в профиль через минуту",
            "uzbek": "Ma'lumotlar bazasi yangilanmoqda. Iltimos, bir daqiqadan so'ng profilingizni tekshiring"
        }[language]

    _return = str()

    # Logtime section
    if result['logtime']['rank'] <= 10:
        _return += {
            "english": f"👑 You are in the top 10 for time spent at the {campus} campus! You are ranked {result['logtime']['rank']} out of 636 students. \nAre you inflating your hours?🤨\n\n",
            "russian": f"👑 Вы входите в топ-10 по провождению времени в кампусе {campus}! Вы на {result['logtime']['rank']} месте среди 636 учеников. \nНакручиваешь себе часы?🤨\n\n",
            "uzbek": f"👑 Siz {campus} kampusida vaqt o'tkazish bo'yicha eng yaxshi 10 talikadasiz! Siz {result['logtime']['rank']}-o'rindasiz 636 talaba orasida. \nSoatingizni o'ziyaptimi?🤨\n\n"
        }[language]
    elif result['logtime']['percent_more'] > 50.00:
        _return += {
            "english": f"❌ You spend less time on campus than {result['logtime']['percent_more']:.2f}% of participants. \n\n",
            "russian": f"❌ Вы проводите в кампусе меньше времени, чем {result['logtime']['percent_more']:.2f}% участников интенсива. \n\n",
            "uzbek": f"❌ Siz kampusda {result['logtime']['percent_more']:.2f}% ishtirokchilarga qaraganda kamroq vaqt o'tkazasiz \n\n."
        }[language]
    elif result['logtime']['percent_less'] > 50.00:
        _return += {
            "english": f"⏳ You spend more time on campus than {result['logtime']['percent_less']:.2f}% of participants. \n\n",
            "russian": f"⏳ Вы проводите в кампусе больше времени, чем {result['logtime']['percent_less']:.2f}% участников интенсива. \n\n",
            "uzbek": f"⏳ Siz kampusda {result['logtime']['percent_less']:.2f}% ishtirokchilarga qaraganda ko'proq vaqt o'tkazasiz. \n\n"
        }[language]

    # Tasks section
    if result['tasks']['rank'] <= 10:
        _return += {
            "english": f"👑✅ You are in the top 10 students for completed projects at the {campus} campus! You are ranked {result['tasks']['rank']} out of 636 students. \nAre you copying from ChatGPT?🤭\n\n",
            "russian": f"👑✅ Вы входите в топ-10 учеников по сданным проектам в кампусе {campus}! Вы на {result['tasks']['rank']} месте среди 636 учеников. \nСписываешь c ChatGpt?🤭\n\n",
            "uzbek": f"👑✅ Siz {campus} kampusida topshirilgan loyihalar bo'yicha eng yaxshi 10 talikadasiz! Siz {result['tasks']['rank']}-o'rindasiz 636 talaba orasida. \nChatGPTdan nusxalayapsizmi?🤭\n\n" 
        }[language]
    elif result['tasks']['percent_more'] < 50.00:
        _return += {
            "english": f"✅ You are in {result['tasks']['rank']}th place for project submissions out of 636 participants in the intensive course. \n\n",
            "russian": f"✅ Вы на {result['tasks']['rank']} месте по сдаче проэктов из 636 участников интенсива. \n\n",
            "uzbek": f"✅ Siz {result['tasks']['rank']}-o'rindasiz, intensiv kursda 636 ishtirokchi orasida loyihalarni topshirish bo'yicha \n\n" 
        }[language]
    elif result['tasks']['percent_less'] > 50.00:
        _return += {
            "english": f"❌ You have completed fewer projects than {result['tasks']['percent_more']:.2f}% of participants. \n\n",
            "russian": f"❌ Вы смогли сдать меньше проектов, чем {result['tasks']['percent_more']:.2f}% участников интенсива. \n\n",
            "uzbek": f"❌ Siz {result['tasks']['percent_more']:.2f}% ishtirokchilarga qaraganda kamroq loyihalarni topshirdingiz. \n\n" 
        }[language]

    # Edu events section
    if result['edu_events']['rank'] <= 10:
        _return += {
            "english": f"👑🤓 You are in the top 10 students for educational events at the {campus} campus! You are ranked {result['edu_events']['rank']} out of 636 students. \n\n",
            "russian": f"👑🤓 Вы входите в топ-10 учеников по количеству образовательных ивентов в кампусе {campus}! Вы на {result['edu_events']['rank']} месте среди 636 учеников. \n\n",
            "uzbek": f"👑🤓 Siz {campus} kampusida ta'lim tadbirlari bo'yicha eng yaxshi 10 talikadasiz! Siz {result['edu_events']['rank']}-o'rindasiz 636 talaba orasida. \n\n"
        }[language]
    elif result['edu_events']['percent_more'] < 50.00:
        _return += {
            "english": f"🤓 You have made more educational events than {result['edu_events']['percent_less']:.2f}% of participants. \n\n",
            "russian": f"🤓 Вы сделали больше образовательных ивентов, чем {result['edu_events']['percent_less']:.2f}% участников интенсива. \n\n",
            "uzbek": f"🤓 Siz {result['edu_events']['percent_less']:.2f}% ishtirokchilarga qaraganda ko'proq ta'lim tadbirlar kildingiz. \n\n" 
        }[language]
    # elif result['edu_events']['percent_less'] > 50.00:
    #     _return += {
    #         "english": f"❌ You have made fewer educational events than {result['edu_events']['percent_more']:.2f}% of participants. \n\n",
    #         "russian": f"❌ Вы сделали меньше образовательных ивентов, чем {result['edu_events']['percent_more']:.2f}% участников интенсива. \n\n" ,
    #         "uzbek": f"❌ Siz {result['edu_events']['percent_more']:.2f}% ishtirokchilarga qaraganda kamroq ta'lim tadbirlar kildingiz. \n\n"
    #     }[language]

    # Ent events section
    if result['ent_events']['rank'] <= 10:
        _return += {
            "english": f"👑🤡 You are in the top 10 students for entertainment events at the {campus} campus! You are ranked {result['ent_events']['rank']} out of 636 students. \n\n",
            "russian": f"👑🤡 Вы входите в топ-10 учеников по количеству развлекательных ивентов в кампусе {campus}! Вы на {result['ent_events']['rank']} месте среди 636 учеников. \n\n",
            "uzbek": f"👑🤡 Siz {campus} kampusida ko'ngilochar tadbirlar bo'yicha eng yaxshi 10 talikadasiz! Siz {result['ent_events']['rank']}-o'rindasiz 636 talaba orasida. \n\n"
        }[language]
    elif result['ent_events']['percent_more'] < 22.50:
        _return += {
            "english": f"🤡 You have made more entertainment events than {result['ent_events']['percent_less']:.2f}% of participants. \n\n",
            "russian": f"🤡 Вы сделали больше развлекательных ивентов, чем {result['ent_events']['percent_less']:.2f}% участников интенсива. \n\n",
            "uzbek": f"🤡 Siz {result['ent_events']['percent_less']:.2f}% ishtirokchilarga qaraganda ko'proq ko'ngilochar tadbirlar kildingiz. \n\n"
        }[language]
    # elif result['ent_events']['percent_less'] > 50.00:
    #     _return += {
    #         "english": f"❌ You have made fewer entertainment events than {result['ent_events']['percent_more']:.2f}% of participants. \n\n",
    #         "russian": f"❌ Вы сделали меньше развлекательных ивентов, чем {result['ent_events']['percent_more']:.2f}% участников интенсива. \n\n",
    #         "uzbek": f"❌ Siz {result['ent_events']['percent_more']:.2f}% ishtirokchilarga qaraganda kamroq ko'ngilochar tadbirlar kildingiz. \n\n"
    #     }[language]

    # Total events section
    if result['total_events']['rank'] <= 10:
        _return += {
            "english": f"👑😱 You are in the top 10 students for total events at the {campus} campus! ✨ You are ranked {result['total_events']['rank']} out of 636 students. \n\n",
            "russian": f"👑😱 Вы входите в топ-10 учеников по общему количеству ивентов в кампусе {campus}! ✨ Вы на {result['total_events']['rank']} месте среди 636 учеников. \n\n",
            "uzbek": f"👑😱 Siz {campus} kampusida umumiy tadbirlar bo'yicha eng yaxshi 10 talikadasiz! ✨ Siz {result['total_events']['rank']}-o'rindasiz 636 talaba orasida. \n\n"
        }[language]
    elif result['total_events']['percent_more'] < 22.50:
        _return += {
            "english": f"😱 You have made more events than {result['total_events']['percent_less']:.2f}% of participants. \n\n",
            "russian": f"😱 Вы сделали больше ивентов, чем {result['total_events']['percent_less']:.2f}% участников интенсива. \n\n",
            "uzbek": f"😱 Siz {result['total_events']['percent_less']:.2f}% ishtirokchilarga qaraganda ko'proq tadbirlar kildingiz. \n\n"
        }[language]
    # elif result['total_events']['percent_less'] > 50.00:
    #     _return += {
    #         "english": f"❌ You have made fewer events than {result['total_events']['percent_more']:.2f}% of participants. \n\n",
    #         "russian": f"❌ Вы посетили меньше ивентов, чем {result['total_events']['percent_more']:.2f}% участников интенсива. \n\n",
    #         "uzbek": f"❌ Siz {result['total_events']['percent_more']:.2f}% ishtirokchilarga qaraganda kamroq tadbirlar kildingiz. \n\n"
    #     }[language]

    return _return



async def _process_report_type(task, students, report_type, language, task_id, result, current_campus):
    for lang in ['english', 'russian', 'uzbek']:
        post_url = get_post(task, f'url_{report_type}_{lang}_{current_campus}')
        if not post_url:
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
                    campus_language_specified = "Ташкент" if current_campus == "tashkent" else "Самарканд"
            else:
                campus_language_specified = current_campus.capitalize()

            post_url = create_telegraph_post(
                            TELEGRAPH_TOKEN,
                            f"{titles[lang][report_type]} ({task}) {campus_language_specified.capitalize()}",
                            make_content(students, task_id, lang) #Make sure students are filtered by campus in make_content
                        )['result']['url']
            create_post(task, post_url, f'url_{report_type}_{lang}_{current_campus}')
            time.sleep(1)

        if lang == language:
            descriptions = {
                'english': {
                    'passed': "Passed the project",
                    'hundred': "Scored 100%",
                    'didnt_pass': "Didn't pass the project",
                    'in_progress': "Are working on the project",
                    'in_reviews': "Are waiting for review",
                    'registered': "Are registered"
                },
                'russian': {
                    'passed': "Cдали проект",
                    'hundred': "Набрали 100%",
                    'didnt_pass': "Не сдали проект",
                    'in_progress': "Выполняют проект",
                    'in_reviews': "Ожидают проверку",
                    'registered': "Зарегистрированы"
                },
                'uzbek': {
                    'passed': "Loyihani topshirgan",
                    'hundred': "100% ball olgan",
                    'didnt_pass': "Loyihani topshirmagan",
                    'in_progress': "Loyiha ustida ishlamoqda",
                    'in_reviews': "Tekshiruvni kutmoqda",
                    'registered': "Ro'yxatdan o'tgan"
                }
            }

            result.append("------------------------------------------------------------------------\n\n")
            result.append(f"{descriptions[lang][report_type]}: {post_url}\n\n")







if __name__ == "__main__":
    result = make_profile_report("russian", "tashkent", f"../api/data_{intensive_month_selected}/participants/tashkent/personal_stats.db", "oureadag")
    # result1 = sort_personal_stats("../api/data/participants/tashkent/personal_stats.db", "tashkent", "oureadag")


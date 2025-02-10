import sys
sys.path.append("..")

import telegram.constants
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, CallbackContext
from posts import create_telegraph_post, make_content
from db import *  
from config import *
from api.main import *
from handle_files import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    user = get_user(chat_id)
    if user:
        await show_main_options(update, context)
    else:
        context.user_data['chatId'] = chat_id
        await handle_authorization(update, context)


async def handle_authorization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_path = "./images/main.jpg"
    caption = "Добро пожаловать! Давайте начнем"
    try:
        with open(image_path, "rb") as image_file:
            await update.message.reply_photo(photo=InputFile(image_file), caption=caption)
    except FileNotFoundError:
        await update.message.reply_text("Image not found!")

    keyboard_language = [
        [InlineKeyboardButton("English", callback_data='lang_english')],
        [InlineKeyboardButton("Русский", callback_data='lang_russian')],
        [InlineKeyboardButton("O'zbek", callback_data='lang_uzbek')],
    ]
    reply_markup_language = InlineKeyboardMarkup(keyboard_language)

    await update.message.reply_text("Выберите язык:", reply_markup=reply_markup_language)


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language = query.data.split('_')[1] #get the language without lang_
    context.user_data["language"] = language #save the language in user_data

    keyboard_countries = [
        [InlineKeyboardButton(country, callback_data=f'country_uzb')] for country in KEYBOARDS['language_selected']['keyboard'][language]
    ]

    reply_markup_countries = InlineKeyboardMarkup(keyboard_countries)
    message = KEYBOARDS['language_selected']['message'][language]

    await query.edit_message_text(message, reply_markup=reply_markup_countries)


async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    country = query.data.split('_')[1]

    context.user_data['country'] = country
    language = context.user_data['language']

    campuses = KEYBOARDS['country_selected']['keyboard'][language]

    keyboard_campuses_uzb = [
        [InlineKeyboardButton(campuses[0], callback_data=f"campus_tashkent")], 
        [InlineKeyboardButton(campuses[1], callback_data=f"campus_samarkand")] 
    ]

    reply_markup_campuses = InlineKeyboardMarkup(keyboard_campuses_uzb)
    message = KEYBOARDS['country_selected']['message'][language]

    await query.edit_message_text(message, reply_markup=reply_markup_campuses)



async def campus_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language = context.user_data['language']
    campus = query.data.split('_')[1]
    context.user_data['campus'] = campus

    streams = KEYBOARDS['campus_selected']['keyboard'][language]

    keyboard_streams = [ 
        [InlineKeyboardButton(streams[0], callback_data='stream_intensive')],
    ]

    reply_markup_streams = InlineKeyboardMarkup(keyboard_streams)
    message = KEYBOARDS['campus_selected']['message'][language]

    await query.edit_message_text(message, reply_markup=reply_markup_streams)


async def stream_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    stream = query.data
    context.user_data['stream'] = stream

    create_user(context.user_data['chatId'], context.user_data['language'], context.user_data['campus'], stream)

    await show_main_options(update, context)


async def show_main_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    context.user_data['chatId'] = chat_id

    image_path = "./images/21_school_logo.jpg"

    try:
        language = get_data(chat_id, 'language')
        campus = get_data(chat_id, "campus")

        context.user_data['campus'] = campus
    except KeyError as e:
        raise KeyError(f"Wrong language has been entered {e}")

    caption = KEYBOARDS['show_main_options']['caption'][language[0]]

    keyboard = list()

    for item in KEYBOARDS['show_main_options']['keyboard'][language[0]]:
        keyboard.append([InlineKeyboardButton(item['text'], callback_data=item['callback_data'])])

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['previous_markup'] = reply_markup

    try:
        with open(image_path, "rb") as image_file:
            input_file = InputFile(image_file)  

            if update.callback_query:  
                chat_id = update.effective_chat.id
                await context.bot.send_photo(
                    chat_id=chat_id, 
                    photo=input_file, 
                    caption=caption, 
                    reply_markup=reply_markup, 
                    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
                )
            elif update.message: 
                await update.message.reply_photo(
                    photo=input_file, 
                    caption=caption, 
                    reply_markup=reply_markup, 
                    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
                )
            else:
                print("An error occurred. Please try again.")

    except FileNotFoundError:
        error_text = "Image not found!"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text)
        elif update.message:
            await update.message.reply_text(error_text)
        else:
            await context.bot.send_message(chat_id=chat_id, text=error_text)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query:
        return
    
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_user.id

    try:
        language = get_data(chat_id, 'language')
    except KeyError as e:
        raise KeyError(f"An error occured\n{e}")

    if query.data == 'stats':
        keyboard = list()

        for item in KEYBOARDS['button']['stats']['keyboard'][language[0]]:
            keyboard.append([InlineKeyboardButton(item['text'], callback_data=item['callback_data'])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_markup'] = query.message.reply_markup
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    elif query.data == "go_back":
        previous_markup = context.user_data.get('previous_markup')
        if previous_markup:
            chat_id = update.effective_chat.id
            message_id = update.effective_message.id
            await context.bot.delete_message(chat_id, message_id)
            await show_main_options(update, context)
    else:
        await query.edit_message_media(media=query.message.media, caption=query.message.caption, reply_markup=InlineKeyboardMarkup(keyboard)) 

    # elif query.data == 'change_language':
    #     # Show language options
    #     keyboard = [
    #         [InlineKeyboardButton("Русский", callback_data='lang_ru')],
    #         [InlineKeyboardButton("O'zbekcha", callback_data='lang_uz')],
    #         [InlineKeyboardButton("English", callback_data='lang_en')]
    #     ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     await query.edit_message_text(text="Выберите язык:", reply_markup=reply_markup)

    # elif query.data == 'change_campus':
    #     # Ask if the user wants to change the campus
    #     keyboard = [
    #         [InlineKeyboardButton("Да", callback_data='campus')],
    #         [InlineKeyboardButton("Нет", callback_data='main_options')]
    #     ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     await query.edit_message_text(text="Хотите выбрать другой кампус?", reply_markup=reply_markup)

    # elif query.data == 'change_stream':
    #     # Show the current stream and options to change it
    #     current_stream = context.user_data.get('stream', 'не выбран')
    #     keyboard = [
    #         [InlineKeyboardButton("Интенсис", callback_data='stream_intensiv')],
    #         [InlineKeyboardButton("Основа", callback_data='stream_osnova')]
    #     ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     await query.edit_message_text(text=f"Ваш текущий поток: {current_stream.capitalize()}. Хотите изменить?", reply_markup=reply_markup)

    # elif query.data == "go_back":
    #     await query.delete_message()
    #     await context.bot.send_message( chat_id=update.effective_chat.id, text="Выберите опцию:", reply_markup=reply_markup)
    #     await query.edit_message_text(await show_main_options(update, context))

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        language = get_data(update.effective_chat.id, 'language')
    except KeyError as e:
        raise KeyError(f"An error occured\n{e}")

    keyboard_language = [
        [InlineKeyboardButton("English", callback_data='changed_lang_english')],
        [InlineKeyboardButton("Русский", callback_data='changed_lang_russian')],
        [InlineKeyboardButton("O'zbek", callback_data='changed_lang_uzbek')],
    ]
    keyboard_language.append([KEYBOARDS['button']['stats']['keyboard'][language[0]][-1]])

    reply_markup_language = InlineKeyboardMarkup(keyboard_language)

    await query.edit_message_reply_markup(reply_markup=reply_markup_language)

async def language_changed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language = query.data.split('_')[2]
    context.user_data['language'] = language

    update_user(context.user_data['chatId'], language=language)

    chat_id = update.effective_chat.id
    message_id = update.effective_message.id

    await context.bot.delete_message(chat_id, message_id)
    await show_main_options(update, context)



async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        language = get_data(update.effective_chat.id, 'language')[0]
    except KeyError as e:
        raise KeyError(f"An error occured\n{e}")
    
    go_back = KEYBOARDS['button']['stats']['keyboard'][language][-1]['text']

    if query.data == "stats_intensive_week_1":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in FIRST_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton(go_back, callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_2":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in SECOND_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton(go_back, callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_3":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in THIRD_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton(go_back, callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_4":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in FOURTH_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)




async def show_specific_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language, campus = await _get_user_language_and_campus(update, context)
    the_other_campus = "samarkand" if campus == "tashkent" else "tashkent"

    task = str()
    task_id = str()
    report = dict()
    result = list()

    task = query.data  # Assign task if it's not the "show_other_campus" click
    context.user_data['task'] = task
    context.user_data['current_campus'] = campus # Store current campus
    task_id = TASKS_INTENSIVE_BOT[task]

    report = make_report(task, language, campus)
    result = [report['report']]

    for report_type in ['passed', 'hundred', 'scored_didnt_pass', 'in_progress', 'in_reviews', 'registered']:
        students = report.get(f'scored_{report_type}' if report_type != 'passed' else 'passed_students')
        if students:
            await _process_report_type(task, students, report_type, language, task_id, result)

    other_campus_stats_button = await _create_other_campus_button(the_other_campus, language)
    reply_markup = InlineKeyboardMarkup([other_campus_stats_button, [InlineKeyboardButton(KEYBOARDS['button']['stats']['keyboard'][language][-1]['text'], callback_data='go_back')]])

    await query.edit_message_caption("".join(result))
    await query.edit_message_reply_markup(reply_markup=reply_markup)



async def show_other_campus_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = context.user_data.get('task')
    language, campus = await _get_user_language_and_campus(update, context) 

    # Ensure 'campus' exists
    if 'campus' not in context.user_data:
        context.user_data['campus'] = campus  # Default

    current_campus = context.user_data['campus']

    if isinstance(context.user_data['campus'], tuple):
        current_campus = context.user_data['campus'][0]
    

    other_campus = str()

    if current_campus == "tashkent":
        other_campus = "samarkand"
        context.user_data['campus'] = "samarkand"
    elif current_campus == "samarkand":  # current_campus must be "samarkand"
        other_campus = "tashkent"
        context.user_data['campus'] = "tashkent"

    print(f"Switching from {current_campus} to {other_campus}")

    report_other = make_report(task, language, other_campus)
    # print(f"Generated Report for {other_campus}: {report_other}")

    result = [report_other['report']]
    task_id = TASKS_INTENSIVE_BOT[task]

    for report_type in ['passed', 'hundred', 'scored_didnt_pass', 'in_progress', 'in_reviews', 'registered']:
        students = report_other.get(f'scored_{report_type}' if report_type != 'passed' else 'passed_students')
        if students:
            await _process_report_type(task, students, report_type, language, task_id, result)

    combined_report = "".join(result)

    current_caption = update.effective_message.caption

    if not current_caption or combined_report.strip() != current_caption.strip():
        other_campus_stats_button = await _create_other_campus_button(other_campus, language)  # FIXED
        reply_markup = InlineKeyboardMarkup([
            other_campus_stats_button, 
            [InlineKeyboardButton(KEYBOARDS['button']['stats']['keyboard'][language][-1]['text'], callback_data='go_back')]
        ])
        await update.effective_message.edit_caption(combined_report, reply_markup=reply_markup)
    else:
        print("Caption is the same. Not updating.")


async def _get_students_string(students, report_type, language):
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
    students_str = "------------------------------------------------------------------------\n\n"
    for student in students:
        students_str += f"{descriptions[language][report_type]}: {student[0]} - {student[1]}\n" # Format the string as you want
    students_str += "\n"
    return students_str



async def _get_user_language_and_campus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    try:
        language = get_data(update.effective_chat.id, 'language')[0]
    except KeyError as e:
        raise KeyError(f"An error occurred\n{e}")

    try:
        campus = get_data(update.effective_chat.id, 'campus')[0]
    except KeyError as e:
        raise KeyError(f"An error occurred\n{e}")
    return language, campus




async def _process_report_type(task, students, report_type, language, task_id, result):
    for lang in ['english', 'russian', 'uzbek']:
        post_url = get_post(task, f'url_{report_type}_{lang}')
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

            post_url = create_telegraph_post(
                TELEGRAPH_TOKEN,
                f"{titles[lang][report_type]}",
                make_content(students, task_id, lang)
            )['result']['url']
            create_post(task, post_url, f'url_{report_type}_{lang}')

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


async def _create_other_campus_button(the_other_campus, language):
    if language == "russian":
        the_other_campus_language_specified = "Ташкент" if the_other_campus == "tashkent" else "Самарканд"
    else:
        the_other_campus_language_specified = "Tashkent" if the_other_campus == "tashkent" else "Samarkand"

    text_show_other_campus = KEYBOARDS['show_specific_task_info']['other_campus_stats_button'][language]['text'].format(
        the_other_campus_language_specified)
    callback_data = "show_other_campus_task_info"  # Consistent callback data

    return [InlineKeyboardButton(text_show_other_campus, callback_data=callback_data)]



async def change_campus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()


    campus = get_data(update.effective_chat.id, "campus")[0].capitalize()

    try:
        language = get_data(update.effective_chat.id, 'language')[0]
    except KeyError as e:
        raise KeyError(f"An error occured\n{e}")
    
    buttons = KEYBOARDS['change_campus']['keyboard'][language]
    campuses = buttons[0]['text']
    go_back = buttons[1]

    keyboard = [
       [InlineKeyboardButton(campuses[0], callback_data='changed_campus_tashkent')],
       [InlineKeyboardButton(campuses[1], callback_data='changed_campus_samarkand')],   
       [InlineKeyboardButton(go_back['text'], callback_data=go_back['callback_data'])]   
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = KEYBOARDS['change_campus']['caption'][language]

    await query.edit_message_caption(caption=f"{caption} {campus}")
    await query.edit_message_reply_markup(reply_markup=reply_markup)

async def campus_changed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    campus = query.data.split("_")[-1]

    update_user(update.effective_chat.id, campus=campus)

    previous_markup = context.user_data.get('previous_markup')
    if previous_markup:
        chat_id = update.effective_chat.id
        message_id = update.effective_message.id
        await context.bot.delete_message(chat_id, message_id)
        await show_main_options(update, context)





def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern=r"^lang_(english|russian|uzbek)$"))
    app.add_handler(CallbackQueryHandler(country_selected, pattern="country_uzb"))
    app.add_handler(CallbackQueryHandler(campus_selected, pattern=r"^campus_(tashkent|samarkand)$"))
    app.add_handler(CallbackQueryHandler(stream_selected, pattern="stream_intensive"))

    app.add_handler(CallbackQueryHandler(change_language, pattern=r"^change_language"))
    app.add_handler(CallbackQueryHandler(language_changed, pattern=r"^changed_lang_(english|russian|uzbek)$"))

    app.add_handler(CallbackQueryHandler(change_campus, pattern=r"^change_campus"))
    app.add_handler(CallbackQueryHandler(campus_changed, pattern=r"^changed_campus_(tashkent|samarkand)$"))


    app.add_handler(CallbackQueryHandler(button, pattern=r"(stats|go_back)$"))

    app.add_handler(CallbackQueryHandler(show_tasks, pattern=r"^stats_intensive_week_(1|2|3|4)$"))
    app.add_handler(CallbackQueryHandler(show_specific_task_info, pattern=r"^T\d{2}D\d{2}$|^E\d{2}D\d{2}$|^P\d{2}D\d{2}$"))
    app.add_handler(CallbackQueryHandler(show_other_campus_task_info, pattern=r"^show_other_campus_task_info"))



    app.run_polling()


if __name__ == '__main__':
    main()

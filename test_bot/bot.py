import sys
sys.path.append("..")

import telegram.constants
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, CallbackContext, MessageHandler, filters
from db_modules import *  
from configs.config_bot import *
from api.main import *
from api_helper import *
from encrypt import *
from report_helpers.report_helper import _process_report_type, make_report, make_profile_report
import random
import re


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

    language = query.data.split('_')[1] 
    context.user_data["language"] = language

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
    username = update.effective_user.username

    create_user(update.effective_chat.id, username, context.user_data['language'], context.user_data['campus'], stream)

    await show_main_options(update, context)


async def show_main_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    context.user_data['chatId'] = chat_id

    image_path = "./images/21_school_logo.jpg"

    try:
        language = get_data(chat_id, 'language')
        campus = get_data(chat_id, "campus")
    except KeyError as e:
        raise KeyError(f"Wrong language has been entered {e}")

    student, level, exp = get_best_student(f"../api/data_{intensive_month_selected}/participants/{campus}/participants.db")

    num_active_students = get_active_students(f"../api/data_{intensive_month_selected}/participants/{campus}/participants.db")
  
    num_students = 699 if campus == "tashkent" else 347

    if language == "russian":
        campus_language_specified = "Ташкент" if campus == "tashkent" else "Самарканд"
    else:
        campus_language_specified = campus.capitalize()

    student_link = f"https://edu.21-school.ru/profile/{student}/about"
    # Format the student part of the caption with Markdown link
    formatted_student = f"[{student}]({student_link})" #MarkdownV2 format

    out_of_intensive = False if datetime.datetime.now() >= datetime.datetime(year=2025,month=3, day=3) else True

    if not out_of_intensive:
        caption = KEYBOARDS['show_main_options']['caption_during_intensive'][language].format(
            campus=campus_language_specified,
            num_active_students=num_active_students,
            num_students=num_students,
            student=formatted_student, 
            level=level,
            exp=exp
        )
    else:
        caption = KEYBOARDS['show_main_options']['caption_out_of_intensive'][language].format(
            campus=campus_language_specified)

    keyboard = [[InlineKeyboardButton(text=item['text'], callback_data=item['callback_data'])] for item in KEYBOARDS['show_main_options']['keyboard'][language]]

    if out_of_intensive:
        keyboard.pop(1)
        previous_intesives_button = keyboard.pop(-1)
        keyboard.insert(1, previous_intesives_button)
    

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

        for item in KEYBOARDS['button']['stats']['keyboard'][language]:
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
    keyboard_language.append([KEYBOARDS['button']['stats']['keyboard'][language][-1]])

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
        language = get_data(update.effective_chat.id, 'language')
    except KeyError as e:
        raise KeyError(f"An error occured\n{e}")
    
    go_back = KEYBOARDS['button']['stats']['keyboard'][language][-1]['text']

    if query.data == "stats_intensive_week_1":
            keyboard = [
                [InlineKeyboardButton(
                    task, 
                    callback_data=task if task.startswith("T") else task.split(" ")[0]
                )] for task, _ in FIRST_WEEK_INTENSIVE.items()
            ]
            keyboard.append([InlineKeyboardButton(go_back, callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_2":
            keyboard = [
                [InlineKeyboardButton(
                    task, 
                    callback_data=task if task.startswith("T") else task.split(" ")[0]
                )] for task, _ in SECOND_WEEK_INTENSIVE.items()
            ]
            keyboard.append([InlineKeyboardButton(go_back, callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_3":
            keyboard = [
                [InlineKeyboardButton(
                    task, 
                    callback_data=task if task.startswith("T") else task.split(" ")[0]
                )] for task, _ in THIRD_WEEK_INTENSIVE.items()
            ]
            keyboard.append([InlineKeyboardButton(go_back, callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_4":
            keyboard = [
                [InlineKeyboardButton(
                    task, 
                    callback_data=task if task.startswith("T") else task.split(" ")[0]
                )] for task, _ in FOURTH_WEEK_INTENSIVE.items()
            ]
            keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)




async def show_specific_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language, campus = await _get_user_language_and_campus(update, context)

    task = str()
    task_id = str()
    report = dict()
    result = list()

    task = query.data  
    context.user_data['task'] = task
    context.user_data['current_campus'] = campus 
    task_id = TASKS_INTENSIVE_BOT[task]

    report = make_report(task, language, campus, f"../api/data_{intensive_month_selected}/tasks.db", 0)
    result = [report['report']]

    for report_type in ['passed', 'hundred', 'scored_didnt_pass', 'in_progress', 'in_reviews', 'registered']:
        students = report.get(f'scored_{report_type}' if report_type != 'passed' else 'passed_students')
        if students:
            await _process_report_type(task, students, report_type, language, task_id, result, campus)


    text_show_other_campus = KEYBOARDS['show_specific_task_info']['other_campus_stats_button'][language]['text']
    callback_data = "show_other_campus_task_info" 

    buttons = [[InlineKeyboardButton(KEYBOARDS['button']['stats']['keyboard'][language][-1]['text'], callback_data='go_back')]]

    if "report_ready" not in report:
        buttons.insert(0, [InlineKeyboardButton(text_show_other_campus, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_caption("".join(result))
    await query.edit_message_reply_markup(reply_markup=reply_markup)



async def show_other_campus_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = context.user_data.get('task')
    language, campus = await _get_user_language_and_campus(update, context) 

    if 'campus' not in context.user_data:
        context.user_data['campus'] = campus  

    current_campus = context.user_data['campus']

    if isinstance(context.user_data['campus'], tuple):
        current_campus = context.user_data['campus'][0]

    other_campus = str()

    other_campuses = {
        "tashkent": "samarkand",
        "samarkand": "tashkent"
    }

    other_campus = other_campuses[campus]

    if current_campus == "tashkent":
        other_campus = "samarkand"
        context.user_data['campus'] = "samarkand"
    elif current_campus == "samarkand": 
        other_campus = "tashkent"
        context.user_data['campus'] = "tashkent"

    print(f"Switching from {current_campus} to {other_campus}")

    report_other = make_report(task, language, other_campus, f"../api/data_{intensive_month_selected}/tasks.db", 0)

    result = [report_other['report']]
    task_id = TASKS_INTENSIVE_BOT[task]

    for report_type in ['passed', 'hundred', 'scored_didnt_pass', 'in_progress', 'in_reviews', 'registered']:
        students = report_other.get(f'scored_{report_type}' if report_type != 'passed' else 'passed_students')
        if students:
            await _process_report_type(task, students, report_type, language, task_id, result, other_campus)

    combined_report = "".join(result)

    current_caption = update.effective_message.caption

    if not current_caption or combined_report.strip() != current_caption.strip():
        text_show_other_campus = KEYBOARDS['show_specific_task_info']['other_campus_stats_button'][language]['text']
        callback_data = "show_other_campus_task_info" 
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text_show_other_campus, callback_data=callback_data)],
            [InlineKeyboardButton(KEYBOARDS['button']['stats']['keyboard'][language][-1]['text'], callback_data='go_back')]
        ])
        await update.effective_message.edit_caption(combined_report, reply_markup=reply_markup)
    else:
        print("Caption is the same. Not updating.")


async def _get_user_language_and_campus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    try:
        language = get_data(update.effective_chat.id, 'language')
    except KeyError as e:
        raise KeyError(f"An error occurred\n{e}")

    try:
        campus = get_data(update.effective_chat.id, 'campus')
    except KeyError as e:
        raise KeyError(f"An error occurred\n{e}")
    return language, campus



async def change_campus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()


    campus = get_data(update.effective_chat.id, "campus")

    try:
        language = get_data(update.effective_chat.id, 'language')
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

    if language == "russian":
        campus_language_specified = "Ташкент" if campus == "tashkent" else "Самарканд"
    else:
        campus_language_specified = campus.capitalize()

    await query.edit_message_caption(caption=f"{caption} {campus_language_specified}")
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




async def authorize_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия кнопки авторизации"""
    query = update.callback_query
    await query.answer()

    try:
        language = get_data(update.effective_chat.id, 'language')
    except KeyError as e:
        raise KeyError(f"An error occurred\n{e}")

    if query.data == "authorize_user":
        context.user_data.clear()  # Очистка предыдущих данных
        context.user_data['auth_chat_id'] = update.effective_chat.id

        await query.edit_message_caption(caption=KEYBOARDS['authorize_user']['caption'][language])
        await query.message.reply_text(KEYBOARDS['handle_text']['enter_login'][language])
        context.user_data['awaiting'] = "username"



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстового ввода (логин и пароль)"""
    if 'awaiting' not in context.user_data:
        return  # Игнорируем текстовые сообщения без контекста

    try:
        language = get_data(update.effective_chat.id, 'language')
    except KeyError as e:
        raise KeyError(f"An error occurred\n{e}")

    text = update.message.text

    if context.user_data['awaiting'] == "username":
        context.user_data['edu_username'] = text
        context.user_data['awaiting'] = "password"
        await update.message.reply_text(KEYBOARDS['handle_text']['login_saved'][language])

    elif context.user_data['awaiting'] == "password":
        context.user_data['edu_password'] = text
        username = context.user_data['edu_username']
        password = context.user_data['edu_password']
        context.user_data.pop('awaiting', None)  # Очистить статус

        user = await api_authorization(username, password)

        if user:
            chat_id = update.effective_chat.id

            cipher = AESCipher(XXX)
            encrypted_password = cipher.encrypt(password)

            update_user(chat_id, edu_username=username, edu_password=encrypted_password) 
            await update.message.reply_text(KEYBOARDS['handle_text']['success'][language])
        else:
            await update.message.reply_text(KEYBOARDS['handle_text']['failure'][language])
        
        await show_main_options(update, context)



async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    language, campus = await _get_user_language_and_campus(update, context)

    keyboard = [   
       [InlineKeyboardButton(KEYBOARDS['button']['stats']['keyboard'][language][-1]['text'], callback_data=KEYBOARDS['button']['stats']['keyboard'][language][-1]['callback_data'])]   
    ]

    edu_username = get_data(update.effective_chat.id, "edu_username")

    if edu_username is None:
        keyboard.insert(0, [InlineKeyboardButton(KEYBOARDS['show_profile']['keyboard'][language], callback_data="authorize_user")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    else:
        report = make_profile_report(language, campus, f"../api/data_{intensive_month_selected}/participants_to_read/{campus}/personal_stats.db", edu_username)
        reply_markup = InlineKeyboardMarkup(keyboard)

        image_path = f"../api/data_{intensive_month_selected}/images/{random.randint(1, 3)}.png"

        await query.edit_message_caption(caption=report, reply_markup=reply_markup)

        # try:
        #     with open(image_path, "rb") as image_file:
        #         await context.bot.send_photo(
        #             chat_id=update.effective_chat.id,
        #             photo=InputFile(image_file),
        #             caption=report,
        #             reply_markup=reply_markup
        #         )
        #         await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
        # except FileNotFoundError:
        #     print.error(f"Image not found at path: {image_path}")
        #     await context.bot.send_message(
        #         chat_id=update.effective_chat.id,
        #         text=report,
        #         reply_markup=reply_markup
        #     )

async def show_previous_intensives(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    language, campus = await _get_user_language_and_campus(update, context)

    if query.data == "previous_intensives":
        keyboard = [
            [InlineKeyboardButton(text=item['text'], callback_data=item['callback_data'])] for item in KEYBOARDS['show_previous_intensives']['keyboard_campuses'][language]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(caption=KEYBOARDS['show_previous_intensives']['text_campuses'][language], reply_markup=reply_markup)
    
    elif re.match(r"^show_previous_intensives_(tashkent|samarkand)$", query.data):
        campus = query.data.split("_")[-1]

        keyboard = [
            [InlineKeyboardButton(text=item['text'], callback_data=item['callback_data'])] for item in KEYBOARDS['show_previous_intensives'][f'keyboard_intensives_{campus}'][language]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(caption="", reply_markup=reply_markup)


    elif re.match(r"^show_previous_(tashkent|samarkand)_(september|november|february)_(2024|2025)$", query.data):
        chosen_campus, chosen_intensive, chosen_year = query.data.split('_')[2:]

        image_dir = f"../data_previous_intensives/{chosen_campus}/{chosen_intensive}_{chosen_year}/images"
        caption_path = f"../data_previous_intensives/{chosen_campus}/{chosen_intensive}_{chosen_year}/report_{language}.txt"

        media_group = []
        try:
            with open(caption_path, 'r', encoding='utf-8') as caption_file:
                caption = caption_file.read()

            for image_file in os.listdir(image_dir):
                if image_file.endswith(('.png', '.jpg', '.jpeg')):
                    media_group.append(InputMediaPhoto(media=open(os.path.join(image_dir, image_file), 'rb')))

            keyboard = [InlineKeyboardButton(KEYBOARDS['button']['stats']['keyboard'][language][-1]['text'], callback_data='go_back')]

            reply_markup = InlineKeyboardMarkup([keyboard])

            await context.bot.delete_message(message_id=update.effective_message.id, chat_id=update.effective_chat.id)
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=caption)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{KEYBOARDS['button']['stats']['keyboard'][language][-1]['text']} ?", reply_markup=reply_markup)

        except FileNotFoundError as e:
            print(f"Error: {e}")




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

    app.add_handler(CallbackQueryHandler(show_previous_intensives, pattern=r"^previous_intensives|show_previous_intensives_(tashkent|samarkand)|show_previous_(tashkent|samarkand)_(september|november|february)_(2024|2025)$"))

    app.add_handler(CallbackQueryHandler(show_profile, pattern=r"^profile"))
    app.add_handler(CallbackQueryHandler(authorize_user, pattern="^authorize_user$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == '__main__':
    main()

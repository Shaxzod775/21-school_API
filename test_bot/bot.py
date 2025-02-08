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

    keyboard_language = [
        [InlineKeyboardButton("English", callback_data='changed_lang_english')],
        [InlineKeyboardButton("Русский", callback_data='changed_lang_russian')],
        [InlineKeyboardButton("O'zbek", callback_data='changed_lang_uzbek')],
        [InlineKeyboardButton("Go back", callback_data='go_back')]
    ]

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

    if query.data == "stats_intensive_week_1":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in FIRST_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_2":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in SECOND_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_3":
            keyboard = [
                [InlineKeyboardButton(task, callback_data=task)] for task, _ in THIRD_WEEK_INTENSIVE.items()   
            ]
            keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
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

    keyboard = [
       [InlineKeyboardButton("Go back", callback_data='go_back')]   
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = update.effective_message.caption
    context.user_data['caption'] = caption

    task = query.data

    report = make_report(task)
    result = list()
    result.append(report['report'])

    passed_students = report['passed_students']
    if passed_students:
        post_passed = get_post(task, "url_passed")
        if post_passed:
            result.append(f"Список сдавших проэкт: {post_passed}\n\n")
        else:
            post_passed = create_telegraph_post(TELEGRAPH_TOKEN, "Список учеников сдавших проэкт:", make_content(passed_students))['result']['url']
            create_post(task, post_passed, 'url_passed')
            result.append(f"Список сдавших проэкт: {post_passed}\n\n")

    # Students who scored 100%
    scored_hundred = report['scored_hundred'] 
    if scored_hundred:
        post_hundred = get_post(task, 'url_scored_hundred')
        if post_hundred:
            result.append(f"Список учеников, набравших 100%: {post_hundred}\n\n")
        else:
            post_hundred = create_telegraph_post(TELEGRAPH_TOKEN, "Список учеников, набравших 100%:", make_content(scored_hundred))['result']['url']
            create_post(task, post_hundred, 'url_scored_hundred')
            result.append(f"Список учеников, набравших 100%: {post_hundred}\n\n")

    # Students who attempted but failed
    scored_didnt_pass = report['scored_didnt_pass']
    if scored_didnt_pass:
        post_didnt_pass = get_post(task, 'url_scored_didnt_pass')
        if post_didnt_pass:
            result.append(f"Список учеников, не сдавших проэкт, но сделавших хотя бы одно задание: {post_didnt_pass}\n\n")
        else:
            post_didnt_pass = create_telegraph_post(TELEGRAPH_TOKEN, "Список учеников, не сдавших проэкт, но сделавших хотя бы одно задание:", make_content(scored_didnt_pass))['result']['url']
            create_post(task, post_didnt_pass, 'url_scored_didnt_pass')
            result.append(f"Список учеников, не сдавших проэкт, но сделавших хотя бы одно задание: {post_didnt_pass}\n\n")

    # Students currently working on the project
    in_progress = report['in_progress']
    if in_progress:
        post_in_progress = get_post(task, 'url_in_progress')
        if post_in_progress:
            result.append(f"Список учеников, выполняющих проэкт: {post_in_progress}\n\n")
        else:
            post_in_progress = create_telegraph_post(TELEGRAPH_TOKEN, "Список учеников, выполняющих проэкт:", make_content(post_in_progress))['result']['url']
            create_post(task, post_in_progress, 'url_in_progress')
            result.append(f"Список учеников, выполняющих проэкт: {post_in_progress}\n\n")

    # Students waiting for review
    in_reviews = report['in_reviews'] 
    if in_reviews:
        post_in_reviews = get_post(task, 'url_in_reviews')
        if post_in_reviews:
            result.append(f"Список учеников, ожидающих проверку: {post_in_reviews}\n\n")
        else:
            post_in_reviews = create_telegraph_post(TELEGRAPH_TOKEN, "Список учеников, ожидающих проверку:", make_content(in_reviews))['result']['url']
            create_post(task, post_in_reviews, 'url_in_reviews')
            result.append(f"Список учеников, ожидающих проверку: {post_in_reviews}\n\n")

    # Registered students
    registered = report['registered']
    if registered:
        post_registered = get_post(task, 'url_registered')
        if post_registered:
            result.append(f"Список зарегистрированных учеников: {post_registered}\n\n")
        else:
            post_registered = create_telegraph_post(TELEGRAPH_TOKEN, "Список зарегистрированных учеников:", make_content(registered))['result']['url']
            create_post(task, post_registered, 'url_registered')
            result.append(f"Список зарегистрированных учеников: {post_registered}\n\n")

    await query.edit_message_caption(f"{"".join(result)}")
    await query.edit_message_reply_markup(reply_markup=reply_markup)



def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern=r"^lang_(english|russian|uzbek)$"))
    app.add_handler(CallbackQueryHandler(country_selected, pattern="country_uzb"))
    app.add_handler(CallbackQueryHandler(campus_selected, pattern=r"^campus_(tashkent|samarkand)$"))
    app.add_handler(CallbackQueryHandler(stream_selected, pattern="stream_intensive"))

    app.add_handler(CallbackQueryHandler(change_language, pattern=r"^change_language"))
    app.add_handler(CallbackQueryHandler(language_changed, pattern=r"^changed_lang_(english|russian|uzbek)$"))

    app.add_handler(CallbackQueryHandler(button, pattern=r"(stats|go_back)$"))

    app.add_handler(CallbackQueryHandler(show_tasks, pattern=r"^stats_intensive_week_(1|2|3|4)$"))
    app.add_handler(CallbackQueryHandler(show_specific_task_info, pattern=r"^T\d{2}D\d{2}$|^E\d{2}D\d{2}$|^P\d{2}D\d{2}$"))

    app.run_polling()


if __name__ == '__main__':
    main()
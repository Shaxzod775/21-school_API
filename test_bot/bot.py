from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, CallbackContext
from db import *  # Make sure this import is correct
from config import *


TOKEN = '7168050647:AAFvWtm2G-qslN1U6K4zv1Y8L7CyhYXs8R0'  # **REPLACE with your actual token**

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

    await update.message.reply_text("Choose your language:", reply_markup=reply_markup_language)


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    language = query.data.split('_')[1] #get the language without lang_
    context.user_data["language"] = language #save the language in user_data

    keyboard_countries = [
        [InlineKeyboardButton("Uzbekistan", callback_data='country_uzb')],
        [InlineKeyboardButton("Russia", callback_data='country_russia')]
    ]

    reply_markup_countries = InlineKeyboardMarkup(keyboard_countries)
    await query.edit_message_text(text=f"You selected {language}. Now, select your country:", reply_markup=reply_markup_countries)  # Clearer text


async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    country = query.data.split('_')[1]

    if country == "uzb":
        keyboard_campuses_uzb = [  # Use separate variable names
            [InlineKeyboardButton("Ташкент", callback_data='campus_tashkent')],
            [InlineKeyboardButton("Самарканд", callback_data='campus_samarkand')]
        ]
        reply_markup_campuses = InlineKeyboardMarkup(keyboard_campuses_uzb)  # Use the correct markup
        await query.edit_message_text(text="Choose your campus in Uzbekistan:", reply_markup=reply_markup_campuses)

    elif country == "russia":
        keyboard_campuses_rus = [ 
            [InlineKeyboardButton("Новосибирск", callback_data='campus_novosibirsk')],
            [InlineKeyboardButton("Москва", callback_data='campus_moscow')],
            [InlineKeyboardButton("Кампус Ш21 (ТЕСТ)", callback_data='campus_test')],
            [InlineKeyboardButton("Белгород", callback_data='campus_belgorod')],
            [InlineKeyboardButton("Нижний Новгород", callback_data='campus_nizhny_novgorod')],
            [InlineKeyboardButton("Сургут", callback_data='campus_surgut')],
            [InlineKeyboardButton("Липецк", callback_data='campus_lipetsk')],
            [InlineKeyboardButton("Казань", callback_data='campus_kazan')],
            [InlineKeyboardButton("Магас", callback_data='campus_magas')],
            [InlineKeyboardButton("Великий Новгород", callback_data='campus_veliky_novgorod')],
            [InlineKeyboardButton("Ярославль", callback_data='campus_yaroslavl')],
            [InlineKeyboardButton("Якутск", callback_data='campus_yakutsk')],
            [InlineKeyboardButton("Челябинск", callback_data='campus_chelyabinsk')],
            [InlineKeyboardButton("Сахалин", callback_data='campus_sakhalin')],
            [InlineKeyboardButton("ВГИК", callback_data='campus_vgik')],
            [InlineKeyboardButton("Анадырь", callback_data='campus_anadyr')],
            [InlineKeyboardButton("Магадан", callback_data='campus_magadan')]
        ]
        reply_markup_campuses = InlineKeyboardMarkup(keyboard_campuses_rus)  
        await query.edit_message_text(text='Choose your campus in Russia:', reply_markup=reply_markup_campuses)


async def campus_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    campus = query.data.split('_')[1]
    context.user_data['campus'] = campus

    keyboard_streams = [ 
        [InlineKeyboardButton("Osnova", callback_data='stream_osnova')],
        [InlineKeyboardButton("Intensiv", callback_data='stream_intensiv')],
    ]
    reply_markup_streams = InlineKeyboardMarkup(keyboard_streams)  

    await query.edit_message_text(f"You selected {campus} campus. Now select your stream", reply_markup=reply_markup_streams)


async def stream_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    stream = query.data
    context.user_data['stream'] = stream

    create_user(context.user_data['chatId'], context.user_data['language'], context.user_data['campus'], stream)

    await show_main_options(update, context)


# async def show_main_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if update == None:
#         raise Exception(f"{update}")
    
#     chat_id = update.effective_user.id
#     context.user_data['chatId'] = chat_id

#     context.user_data['chatId'] = update.effective_user.id
#     context.user_data['chatId'] = chat_id
    
#     image_path = "./images/21_school_logo.jpg"
#     caption = "Welcome back to the bot!"

#     keyboard = [
#         [InlineKeyboardButton("Статистика по заданиям", callback_data='stats')],
#         [InlineKeyboardButton("Язык", callback_data='change_language')],
#         [InlineKeyboardButton("Кампус", callback_data='change_campus')],
#         [InlineKeyboardButton("Поток", callback_data='change_stream')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     try:
#         with open(image_path, "rb") as image_file:
#             await update.message.reply_photo(photo=InputFile(image_file), caption=caption, reply_markup=reply_markup)
#     except FileNotFoundError:
#         await update.message.reply_text("Image not found!") 
    


async def show_main_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    context.user_data['chatId'] = chat_id

    image_path = "./images/21_school_logo.jpg"
    caption = "Welcome back to the bot!"

    keyboard = [
        [InlineKeyboardButton("Статистика по заданиям", callback_data='stats')],
        [InlineKeyboardButton("Язык", callback_data='change_language')],
        [InlineKeyboardButton("Кампус", callback_data='change_campus')],
        [InlineKeyboardButton("Поток", callback_data='change_stream')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['previous_markup'] = reply_markup

    try:
        with open(image_path, "rb") as image_file:
            if update.callback_query:  
                try:
                    chat_id = update.effective_chat.id
                    await context.bot.send_photo(photo=InputFile(image_file), caption=caption, reply_markup=reply_markup, chat_id=chat_id)
                except Exception as e:
                    print(f"An error occurred while updating the media.\n{e}")
            elif update.message: 
                await update.message.reply_photo(photo=InputFile(image_file), caption=caption, reply_markup=reply_markup)
            else:
                print("An error occurred. Please try again.")
    except FileNotFoundError:
        if update.callback_query:
            await update.callback_query.edit_message_text("Image not found!")
        elif update.message:
            await update.message.reply_text("Image not found!")
        else:
            await context.bot.send_message(chat_id=chat_id, text="Image not found!")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query:
        return
    
    query = update.callback_query
    await query.answer()

    if query.data == 'stats':
        keyboard = [
            [InlineKeyboardButton("1 неделя", callback_data='stats_intensive_week_1')],
            [InlineKeyboardButton("2 неделя", callback_data='stats_intensive_week_2')],
            [InlineKeyboardButton("3 неделя", callback_data='stats_intensive_week_3')],
            [InlineKeyboardButton("4 неделя", callback_data='stats_intensive_week_4')],
            [InlineKeyboardButton("Go back", callback_data='go_back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_markup'] = query.message.reply_markup
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    elif query.data == "go_back":
        previous_markup = context.user_data.get('previous_markup')
        if previous_markup:
            await query.edit_message_reply_markup(reply_markup=previous_markup)
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

    language = query.data.split('_')[1]
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
        [InlineKeyboardButton("This function is working", callback_data="test")]   
    ]
    keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_reply_markup(reply_markup=reply_markup)

    # if query.data == "stats_intensive_week_1":
    #         keyboard = [
    #             [InlineKeyboardButton(task, callback_data=task)] for task, _ in FIRST_WEEK_INTENSIVE.items()   
    #         ]
    #         keyboard.append([InlineKeyboardButton("Go back", callback_data='go_back')])
    #         reply_markup = InlineKeyboardMarkup(keyboard)
    #         await query.edit_message_reply_markup(reply_markup=reply_markup)
  




def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern=r"^lang_(english|russian|uzbek)$"))
    app.add_handler(CallbackQueryHandler(country_selected, pattern=r"^country_(uzb|russia)$"))
    app.add_handler(CallbackQueryHandler(campus_selected, pattern=r"^campus_(tashkent|samarkand|novosibirsk|moscow|test|belgorod|nizhny_novgorod|surgut|lipetsk|kazan|magas|veliky_novgorod|yaroslavl|yakutsk|chelyabinsk|sakhalin|vgik|anadyr|magadan)$"))
    app.add_handler(CallbackQueryHandler(stream_selected, pattern=r"^stream_(intensiv|osnova)$"))

    app.add_handler(CallbackQueryHandler(change_language, pattern=r"^change_language"))
    app.add_handler(CallbackQueryHandler(language_changed, pattern=r"^changed_lang_(english|russian|uzbek)$"))

    app.add_handler(CallbackQueryHandler(button, pattern=r"(stats|go_back)$"))

    app.add_handler(CallbackQueryHandler(show_tasks, pattern=r"^stats_intensive_week_(1|2|3|4)$"))
    app.add_handler(CallbackQueryHandler(show_specific_task_info, pattern=r"^T\d{2}D\d{2}$|^E\d{2}D\d{2}$|^P\d{2}D\d{2}$"))

    app.run_polling()


if __name__ == '__main__':
    main()
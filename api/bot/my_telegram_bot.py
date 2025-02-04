from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from ..database.db_bot import *

# Greet the user and send an image with a description
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user = get_user(chat_id)


    if user[1] and user[2]:
        # Returning user
        campus = user[1]
        stream = user[2]
        await update.message.reply_text(
            f"Добро пожаловать обратно! Ваш кампус: {campus}, поток: {stream}."
        )
        await show_main_options(update, context)
    else:
        # New user
        save_user(chat_id)
        # Send a local image with a description
        image_path = "./api/bot/images/main.jpg"  # Replace with the actual path to your image
        caption = "Добро пожаловать! Давайте начнем"
        with open(image_path, "rb") as image_file:
            await update.message.reply_photo(photo=InputFile(image_file), caption=caption)

        keyboard = [
            [InlineKeyboardButton("Кампус", callback_data='campus')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите ваш кампус:", reply_markup=reply_markup)

# Show the main options (Статистика по заданиям, Язык, Кампус, Поток)
async def show_main_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Статистика по заданиям", callback_data='stats')],
        [InlineKeyboardButton("Язык", callback_data='language')],
        [InlineKeyboardButton("Кампус", callback_data='change_campus')],
        [InlineKeyboardButton("Поток", callback_data='change_stream')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update == None:
        raise Exception(f"{update}")
    await context.bot.send_message( chat_id=update.effective_chat.id, text="Выберите опцию:", reply_markup=reply_markup)


# Handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query:
        return
    
    query = update.callback_query
    await query.answer()


    if query.data == 'campus':
        # Show options for Узбекистан and Россия
        keyboard = [
            [InlineKeyboardButton("Узбекистан", callback_data='campus_uzbekistan')],
            [InlineKeyboardButton("Россия", callback_data='campus_russia')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите страну:", reply_markup=reply_markup)

    elif query.data == 'campus_uzbekistan':
        # Show campuses in Uzbekistan
        keyboard = [
            [InlineKeyboardButton("Ташкент", callback_data='campus_tashkent')],
            [InlineKeyboardButton("Самарканд", callback_data='campus_samarkand')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите кампус в Узбекистане:", reply_markup=reply_markup)

    elif query.data == 'campus_russia':
        # Show campuses in Russia
        keyboard = [
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
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите кампус в России:", reply_markup=reply_markup)

    elif query.data.startswith('campus_'):
        # Handle campus selection
        campus = query.data.split('_')[1]
        context.user_data['campus'] = campus
        await query.edit_message_text(text=f"Вы выбрали кампус: {campus.capitalize()}")

        # Show the Поток button after campus selection
        keyboard = [
            [InlineKeyboardButton("Поток", callback_data='stream')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Теперь выберите поток:", reply_markup=reply_markup)

    elif query.data == 'stream':
        # Show stream options
        keyboard = [
            [InlineKeyboardButton("Интенсис", callback_data='stream_intensis')],
            [InlineKeyboardButton("Основа", callback_data='stream_osnova')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите поток:", reply_markup=reply_markup)

    elif query.data.startswith('stream_'):
        # Handle stream selection
        stream = query.data.split('_')[1]
        context.user_data['stream'] = stream
        await query.edit_message_text(text=f"Вы выбрали поток: {stream.capitalize()}")

        # Show the main options after both campus and stream are selected
        await show_main_options(update, context)

    elif query.data == 'stats':
        # Show statistics options
        keyboard = [
            [InlineKeyboardButton("1 неделя", callback_data='week_1')],
            [InlineKeyboardButton("2 неделя", callback_data='week_2')],
            [InlineKeyboardButton("3 неделя", callback_data='week_3')],
            [InlineKeyboardButton("4 неделя", callback_data='week_4')],
            [InlineKeyboardButton("Go back", callback_data='go_back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите неделю:", reply_markup=reply_markup)

    elif query.data == 'language':
        # Show language options
        keyboard = [
            [InlineKeyboardButton("Русский", callback_data='lang_ru')],
            [InlineKeyboardButton("O'zbekcha", callback_data='lang_uz')],
            [InlineKeyboardButton("English", callback_data='lang_en')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите язык:", reply_markup=reply_markup)

    elif query.data == 'change_campus':
        # Ask if the user wants to change the campus
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='campus')],
            [InlineKeyboardButton("Нет", callback_data='main_options')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Хотите выбрать другой кампус?", reply_markup=reply_markup)

    elif query.data == 'change_stream':
        # Show the current stream and options to change it
        current_stream = context.user_data.get('stream', 'не выбран')
        keyboard = [
            [InlineKeyboardButton("Интенсис", callback_data='stream_intensiv')],
            [InlineKeyboardButton("Основа", callback_data='stream_osnova')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваш текущий поток: {current_stream.capitalize()}. Хотите изменить?", reply_markup=reply_markup)

    elif query.data == "go_back":
        await query.delete_message()
        await context.bot.send_message( chat_id=update.effective_chat.id, text="Выберите опцию:", reply_markup=reply_markup)
        await query.edit_message_text(await show_main_options(update, context))

    elif query.data == 'main_options':
        # Return to the main options
        await show_main_options(update, context)

def main() -> None:
    # Replace "YOUR_API_TOKEN_HERE" with your actual bot token
    application = Application.builder().token("7168050647:AAFvWtm2G-qslN1U6K4zv1Y8L7CyhYXs8R0").build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ApplicationBuilder, ContextTypes
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import io
from PIL import ImageGrab

# Enable logging

TOKEN_CHECKOUT = "7972435110:AAGRSbJzNXbeqKqnU3oHlqMaZkgFtnx2Bx0" # **SECURE NOTE: Do not hardcode tokens in real applications!**

reply_keyboard = [['Make Screenshot']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # Added async
    chat_id = update.message.chat_id

    keyboard = [[telegram.InlineKeyboardButton("Take Screenshot", callback_data="take_screenshot")]]
    markup = telegram.InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text="Дарова! Готов взять для тебя скриншот", reply_markup=markup) # Added await


async def take_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    screenshot = ImageGrab.grab()

    screenshot = screenshot.resize((1920, 1080))

    with io.BytesIO() as output:
        screenshot.save(output, format="PNG") 

        output.seek(0)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output)


def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN_CHECKOUT).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(take_screenshot, pattern="^take_screenshot$"))
   
    application.run_polling()


if __name__ == '__main__':
    main()
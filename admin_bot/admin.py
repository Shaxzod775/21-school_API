import sys
sys.path.append("..")

import glob
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler

from db_modules.db import *
from configs.config_bot import *
from api.main import *
from test_bot.api_helper import *
import requests
import os
import re

def get_admin_chat_id():
    with open("admin_chatId.txt", "r") as f:
        return int(f.read())


MEDIA_GROUP_IMAGE_DIR = "media_group_images"


BROADCAST_CHOICE, AWAITING_MESSAGE, AWAITING_MEDIA_GROUP, CONFIRM_PREVIOUS_MEDIA_GROUP = range(4)
CHECK_SUBSCRIPTION_LOGIN, CHECK_SUBSCRIPTION_PROJECT = range(2)
AWAITING_AUTH_CODE_TASK, AWAITING_AUTH_CODE_STUDENTS = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and shows the broadcast choice buttons."""
    keyboard = [
        [InlineKeyboardButton("Сделать рассылку", callback_data="broadcast_choice")],
        [InlineKeyboardButton("Посмотреть подписку", callback_data="check_subscription")],
        [InlineKeyboardButton("Спарсить данные", callback_data="parse_data")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_id = update.effective_chat.id

    users = get_all_users_chatId("../bot_databases/users.db")
    authenticated_users = get_number_of_users_authenticated_in_bot("../bot_databases/users.db")


    with open("images/jerry.jpg", "rb") as image:
        await context.bot.send_photo(photo=image, caption=f"Саламалексус админ!\n\nКол-во пользователей в боте: {len(users)}\n\nАвторизовано: {authenticated_users}", chat_id=chat_id, reply_markup=reply_markup)


async def check_subscription_init(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the check subscription conversation by asking for login."""
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите ваш логин:") # Changed to send_message
    return CHECK_SUBSCRIPTION_LOGIN


async def check_subscription_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the login input and asks for project name."""
    login = update.message.text
    context.user_data['login'] = login
    await update.message.reply_text("Введите название проекта:")
    return CHECK_SUBSCRIPTION_PROJECT


async def check_subscription_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the project name input and fetches subscription status."""
    project_name = update.message.text
    login = context.user_data.get('login')
    chat_id = update.effective_chat.id

    if not login:
        await update.message.reply_text("Логин не был получен. Пожалуйста, попробуйте снова.")
        return ConversationHandler.END

    project_id, _ = INTENSIVE[project_name]    
    if not project_id:
        await update.message.reply_text("Проект не найден.")
        return ConversationHandler.END

    get_api_token()
    token = get_file_token()

    HEADERS = {
        'Authorization': 'Bearer {}'.format(token),
    }
    try:
        response = requests.get(BASE_URL.format(f"/participants/{login}/projects/{project_id}"), headers=HEADERS)

        if response.status_code == 200:
            response_json = response.json()
            title = response_json.get("title")
            status = response_json.get("status")
            completionDateTime = response_json.get("completionDateTime")
            teamMembers = response_json.get("teamMembers")
            finalPercentage = response_json.get("finalPercentage")

            await update.message.reply_text(f"Проект: {title}\nСтатус: {status}\nДата завершения: {completionDateTime}\nКоманда: {teamMembers}\nПроцент завершения: {finalPercentage}")
        else:
            raise Exception(f"Ошибка при получении подписки: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"Не удалось получить подписку пользователя: {e}")

    return ConversationHandler.END

async def cancel_check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the check subscription conversation."""
    await update.message.reply_text("Проверка подписки отменена.")
    return ConversationHandler.END


async def broadcast_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows buttons for choosing message type: Text, Photo, Media Group."""
    query = update.callback_query
    await query.answer() # Acknowledge button click
    keyboard = [
        [InlineKeyboardButton("Текст", callback_data="start_send_text")],
        [InlineKeyboardButton("Фото", callback_data="start_send_photo")],
        [InlineKeyboardButton("Медиагруппа", callback_data="start_send_media_group")],
        [InlineKeyboardButton("Отмена", callback_data="cancel_broadcast_init")]
       ] # Added cancel here
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите тип рассылки:", reply_markup=reply_markup) # Send new message instead of editing
    context.user_data['state'] = BROADCAST_CHOICE # Set state to broadcast choice


async def start_send_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts user to send a text message for broadcast."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Отправьте текст для рассылки.")
    context.user_data['state'] = AWAITING_MESSAGE
    context.user_data['broadcast_type'] = 'text'


async def start_send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts user to send a photo for broadcast."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Отправьте фото для рассылки.")
    context.user_data['state'] = AWAITING_MESSAGE
    context.user_data['broadcast_type'] = 'photo'


async def start_send_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts user to send a media group for broadcast or use previous if available."""
    query = update.callback_query
    await query.answer()

    image_files = glob.glob(os.path.join(MEDIA_GROUP_IMAGE_DIR, "*"))
    if image_files:
        keyboard = [
            [InlineKeyboardButton("Да", callback_data="confirm_previous_media_group")],
            [InlineKeyboardButton("Нет, отправить новую", callback_data="start_new_media_group")],
            [InlineKeyboardButton("Отмена", callback_data="cancel_broadcast_init")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Найдена предыдущая медиагруппа. Использовать её?", reply_markup=reply_markup)
        context.user_data['state'] = CONFIRM_PREVIOUS_MEDIA_GROUP
    else:
        await query.edit_message_text("Отправьте медиагруппу для рассылки (фото с подписью к первому фото - если нужно).")
        context.user_data['state'] = AWAITING_MEDIA_GROUP
        context.user_data['broadcast_type'] = 'media_group'
        _init_media_group_context(context)  # Initialize media group context


async def confirm_previous_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Loads and previews the previous media group."""
    query = update.callback_query
    context.user_data['broadcast_type'] = 'media_group'
    await query.answer()
    await load_previous_media_group(context)
    await preview_media_group(update, context) # Proceed to preview

async def start_new_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the process for sending a new media group, clearing previous."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Отправьте медиагруппу для рассылки (фото с подписью к первому фото - если нужно).")
    context.user_data['state'] = AWAITING_MEDIA_GROUP
    context.user_data['broadcast_type'] = 'media_group'
    _init_media_group_context(context)  # Initialize media group context
    await cleanup_media_files(context) # Clear previous images


def _init_media_group_context(context):
    """Initializes user_data for media group sending."""
    context.user_data['media_group'] = []
    context.user_data['media_group_image_paths'] = []
    context.user_data['media_group_image_count'] = 0
    context.user_data['caption_set'] = False
    os.makedirs(MEDIA_GROUP_IMAGE_DIR, exist_ok=True)


async def load_previous_media_group(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Loads images and caption from previous media group from disk."""
    context.user_data['media_group'] = []
    context.user_data['media_group_image_paths'] = []
    context.user_data['media_group_image_count'] = 0
    context.user_data['caption_set'] = False # Reset caption flag, will be set if caption file exists

    image_files = sorted(glob.glob(os.path.join(MEDIA_GROUP_IMAGE_DIR, "*")), key=os.path.basename) # Ensure order
    caption_file_path = os.path.join(MEDIA_GROUP_IMAGE_DIR, "caption.txt")

    if os.path.exists(caption_file_path):
        with open(caption_file_path, 'r', encoding='utf-8') as f:
            context.user_data['group_caption'] = f.read()
            context.user_data['caption_set'] = True # Mark caption as set
    else:
        context.user_data['group_caption'] = None

    for image_path in image_files:
        if not image_path.endswith("caption.txt"): # Avoid reading caption.txt as image
            context.user_data['media_group_image_paths'].append(image_path)
            caption = context.user_data['group_caption'] if not context.user_data['media_group'] and context.user_data['caption_set'] else None # Apply caption only to first image if caption exists
            context.user_data['media_group'].append(InputMediaPhoto(media=open(image_path, 'rb'), caption=caption))


async def save_media_group_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Saves images from a media group to disk and prepares InputMediaPhoto list, saves caption."""
    message = update.message
    media_group_id = message.media_group_id

    if context.user_data.get('current_media_group_id') != media_group_id:
        # New media group sequence starts, clear previous
        await cleanup_media_files(context) # Clear previous files before saving new ones
        _init_media_group_context(context) # Re-initialize context for new group
        context.user_data['current_media_group_id'] = media_group_id


    caption = message.caption if not context.user_data['caption_set'] else None
    photo = message.photo[-1]

    context.user_data['media_group_image_count'] += 1
    image_num = context.user_data['media_group_image_count']
    file = await context.bot.get_file(photo.file_id)
    file_extension = file.file_path.split('.')[-1] if file.file_path else 'png'
    image_path = os.path.join(MEDIA_GROUP_IMAGE_DIR, f"{image_num}.{file_extension}")
    await file.download_to_drive(image_path)
    context.user_data['media_group_image_paths'].append(image_path)
    context.user_data['media_group'].append(InputMediaPhoto(media=open(image_path, 'rb'), caption=caption))

    if not context.user_data['caption_set'] and message.caption:
        context.user_data['group_caption'] = message.caption # Store group caption
        context.user_data['caption_set'] = True

        caption_file_path = os.path.join(MEDIA_GROUP_IMAGE_DIR, "caption.txt")
        with open(caption_file_path, 'w', encoding='utf-8') as f:
            f.write(message.caption) # Save caption to file


async def preview_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends preview of the media group and confirmation buttons."""
    query = update.callback_query
    await query.answer()

    preview_media_group_list = []
    for path in context.user_data['media_group_image_paths']:
        preview_media_group_list.append(InputMediaPhoto(media=open(path, 'rb')))

    if len(preview_media_group_list) > 0:
        caption_preview = context.user_data.get('group_caption', None) # Get stored caption for preview
        if not caption_preview:
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=preview_media_group_list)
        else: # Send caption separately after media group if it exists
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=preview_media_group_list, caption=caption_preview)


    keyboard = [[InlineKeyboardButton("Да", callback_data="confirm_broadcast")],
                [InlineKeyboardButton("Нет", callback_data="cancel_broadcast")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Медиагруппа готова к отправке. Подтвердите рассылку?", reply_markup=reply_markup) # More clear text


async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text, photo, and media group messages based on state."""
    state = context.user_data.get('state')
    message = update.message

    if not message:
        return

    if state == AWAITING_MESSAGE:
        if context.user_data.get('broadcast_type') == 'text':
            context.user_data['text_message'] = message.text
        elif context.user_data.get('broadcast_type') == 'photo':
            context.user_data['media_group'] = [InputMediaPhoto(media=message.photo[-1].file_id, caption=message.caption or "")]
        await process_broadcast_confirmation(update, context) # Proceed to confirmation after single message

    elif state == AWAITING_MEDIA_GROUP:
        if message.media_group_id and message.photo:
            await save_media_group_images(update, context)
            return # Wait for all media group messages
        else:
            # Assume media group is complete when a non-media-group message or different media_group_id arrives after AWAITING_MEDIA_GROUP
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Медиагруппа получена.")
            await preview_media_group(update, context) # Directly to preview after receiving media group

    elif state == AWAITING_AUTH_CODE_STUDENTS:
        context.user_data['auth_code'] = message.text
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Код авторизации получен.")
        await start_parsing_students(update, context)

    elif state == AWAITING_AUTH_CODE_TASK:
        context.user_data['auth_code'] = message.text
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Код авторизации получен.")
        await start_parsing_task_data(update, context)
        # Proceed with the next steps after receiving the auth code


async def process_broadcast_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends confirmation message with buttons and displays the broadcast message."""
    context.user_data['state'] = None # Reset state

    keyboard = [[InlineKeyboardButton("Да", callback_data="confirm_broadcast")],
                [InlineKeyboardButton("Нет", callback_data="cancel_broadcast")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Sending media group if available for preview (for text and single photo it will be empty lists)
    if context.user_data.get('media_group'):
        if len(context.user_data['media_group']) > 1:
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=context.user_data['media_group'])
        elif len(context.user_data['media_group']) == 1:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=context.user_data['media_group'][0].media, caption=context.user_data['media_group'][0].caption)
    # Sending text message preview if available
    elif context.user_data.get('text_message'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=context.user_data['text_message'])

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text="Сообщение для рассылки: Подтвердите отправку",
                                            reply_markup=reply_markup)


async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the broadcast and sends a confirmation message using ANOTHER BOT."""
    query = update.callback_query
    await query.answer()


    another_bot_app = ApplicationBuilder().token(TOKEN).build()
    another_bot = another_bot_app.bot # Get bot instance from application

    users = get_all_users_chatId("../bot_databases/users.db") # Assuming this function exists and works

    broadcast_type = context.user_data.get('broadcast_type')

    if broadcast_type == 'text':
        text_message = context.user_data.get('text_message')
        if text_message:
            sent_count = 0
            failed_count = 0
            for user_id in users:
                try:
                    await another_bot.send_message(chat_id=user_id, text=text_message) # Use another_bot to send
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send text message to user {user_id} via broadcast bot: {e}")
                    failed_count += 1
            confirmation_message = f"Текстовая рассылка через broadcast bot завершена.\nУспешно отправлено: {sent_count}\nНе удалось отправить: {failed_count}"

    elif broadcast_type == 'photo':
        media_group = context.user_data.get('media_group')
        if media_group and len(media_group) == 1: # Assuming single photo in media_group for 'photo' type
            photo = media_group[0].media
            caption = media_group[0].caption
            sent_count = 0
            failed_count = 0
            for user_id in users:
                try:
                    await another_bot.send_photo(chat_id=user_id, photo=photo, caption=caption) # Use another_bot to send
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send photo to user {user_id} via broadcast bot: {e}")
                    failed_count += 1
            confirmation_message = f"Фото рассылка через broadcast bot завершена.\nУспешно отправлено: {sent_count}\nНе удалось отправить: {failed_count}"

    elif broadcast_type == 'media_group':
        media_group = context.user_data.get('media_group')
        if media_group and len(media_group) > 0:
            sent_count = 0
            failed_count = 0
            for user_id in users:
                try:
                    await another_bot.send_media_group(chat_id=user_id, media=media_group) # Use another_bot to send
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send media group to user {user_id} via broadcast bot: {e}")
                    failed_count += 1
            confirmation_message = f"Медиагруппа рассылка через broadcast bot завершена.\nУспешно отправлено: {sent_count}\nНе удалось отправить: {failed_count}"
    else:
        confirmation_message = "Ошибка: Тип рассылки не определен."

    await query.edit_message_text(confirmation_message) # Edit confirmation to button sender (admin bot)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=confirmation_message) # Send confirmation to admin as well (admin bot)
    await cleanup_media_files(context)
    await start(update, context) # Go back to main menu (admin bot)
    context.user_data.clear()



async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancels the broadcast from confirmation buttons."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Рассылка отменена.")
    await cleanup_media_files(context)
    await start(update, context) # Go back to main menu
    context.user_data.clear()

async def cancel_broadcast_init(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancels the broadcast from initial choice and resets."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Действие отменено.")
    await cleanup_media_files(context) # Clean up files just in case if media group was started but cancelled early
    await start(update, context) # Go back to main menu
    context.user_data.clear() # Clear all user data


async def cleanup_media_files(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cleans up media files from disk."""
    for path in context.user_data.get('media_group_image_paths', []):
        try:
            os.remove(path)
        except Exception as e:
            print(f"Failed to remove image file: {path}, error: {e}")
    context.user_data['media_group_image_paths'] = []


async def parse_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  

    if query.data == "parse_data":
        keyboard = [[InlineKeyboardButton(item['text'], callback_data=item['callback_data'])] for item in KEYBOARDS['button']['stats']['keyboard']["russian"]][:-1]

        keyboard.append([InlineKeyboardButton("Парсить учеников", callback_data="parse_students")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['previous_markup'] = query.message.reply_markup
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    if query.data == "stats_intensive_week_1":
        keyboard = [
            [InlineKeyboardButton(
                task,
                callback_data=task if task.startswith("T") else task.split(" ")[0]
            )] for task, _ in FIRST_WEEK_INTENSIVE.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_2":
        keyboard = [
            [InlineKeyboardButton(
                task,
                callback_data=task if task.startswith("T") else task.split(" ")[0]
            )] for task, _ in SECOND_WEEK_INTENSIVE.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif query.data == "stats_intensive_week_3":
        keyboard = [
            [InlineKeyboardButton(
                task,
                callback_data=task if task.startswith("T") else task.split(" ")[0]
            )] for task, _ in THIRD_WEEK_INTENSIVE.items()
        ]
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

    elif re.match(r"^T\d{2}D\d{2}$|^E\d{2}D\d{2}$|^P\d{2}D\d{2}$", query.data):
        context.user_data['task'] = query.data
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите код авторизации:")
        context.user_data['state'] = AWAITING_AUTH_CODE_TASK

        # script_path = os.path.join(os.path.dirname(__file__), "../api/main.py")
        # main_directory = os.path.dirname(script_path)

        # original_directory = os.getcwd()
        # try:
        #     await context.bot.send_message(chat_id=update.effective_chat.id, text="Скрипт начал работу...")

        #     os.chdir(main_directory)
        #     os.system(f"wsl.exe -e bash -c 'cd {main_directory} && source ../venv/bin/activate && python3 main.py {query.data} march'")

        #     await context.bot.send_message(chat_id=update.effective_chat.id, text="Скрипт успешно завершен.")
        # except Exception as e:
        #     await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка при выполнении скрипта: {e}")
        # finally:
        #     os.chdir(original_directory)

    elif query.data == "parse_students":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите код авторизации:")
        context.user_data['state'] = AWAITING_AUTH_CODE_STUDENTS




async def start_parsing_task_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    script_path = os.path.join(os.path.dirname(__file__), "../api/new_api.py")
    main_directory = os.path.dirname(script_path)

    original_directory = os.getcwd()

    task = context.user_data.get('task')

    try:
        auth_code = context.user_data.get('auth_code')

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Парсинг учеников начался")

        os.chdir(main_directory)
        os.system(f"python .\\new_api.py {task.upper()} march {auth_code}")

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ученики успешно спарсены")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка при выполнении скрипта парсинга учеников: {e}")
    finally:
        os.chdir(original_directory)



async def start_parsing_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    script_path = os.path.join(os.path.dirname(__file__), "../api/new_api.py")
    main_directory = os.path.dirname(script_path)

    original_directory = os.getcwd()

    try:
        auth_code = context.user_data.get('auth_code')

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Парсинг учеников начался")

        os.chdir(main_directory)
        os.system(f"python .\\new_api.py parse_students march {auth_code}")

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ученики успешно спарсены")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка при выполнении скрипта парсинга учеников: {e}")
    finally:
        os.chdir(original_directory)


def main_bot() -> None:
    application = ApplicationBuilder().token(TOKEN_ADMIN_BOT).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel_broadcast_init)) # Add direct cancel command

    # Conversation handler for check_subscription
    check_subscription_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(check_subscription_init, pattern="check_subscription")],
        states={
            CHECK_SUBSCRIPTION_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_subscription_login)],
            CHECK_SUBSCRIPTION_PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_subscription_project)],
        },
        fallbacks=[CommandHandler("cancel", cancel_check_subscription),
                   CallbackQueryHandler(cancel_check_subscription, pattern="cancel")] # Add cancel via command and callback for more flexibility
    )
    application.add_handler(check_subscription_conv_handler)


    # Callback query handlers (button clicks)
    application.add_handler(CallbackQueryHandler(broadcast_choice, pattern="broadcast_choice"))
    application.add_handler(CallbackQueryHandler(start_send_text, pattern="start_send_text"))
    application.add_handler(CallbackQueryHandler(start_send_photo, pattern="start_send_photo"))
    application.add_handler(CallbackQueryHandler(start_send_media_group, pattern="start_send_media_group"))
    application.add_handler(CallbackQueryHandler(confirm_previous_media_group, pattern="confirm_previous_media_group"))
    application.add_handler(CallbackQueryHandler(start_new_media_group, pattern="start_new_media_group"))
    application.add_handler(CallbackQueryHandler(preview_media_group, pattern="preview_media_group"))
    application.add_handler(CallbackQueryHandler(confirm_broadcast, pattern="confirm_broadcast"))
    application.add_handler(CallbackQueryHandler(cancel_broadcast, pattern="cancel_broadcast"))
    application.add_handler(CallbackQueryHandler(cancel_broadcast_init, pattern="cancel_broadcast_init"))



    application.add_handler(CallbackQueryHandler(parse_data, pattern=r"^parse_students|parse_data$|^stats_intensive_week_1$|^stats_intensive_week_2$|^stats_intensive_week_3$|^stats_intensive_week_4$|T\d{2}D\d{2}$|^E\d{2}D\d{2}$|^P\d{2}D\d{2}$"))
    application.add_handler(CallbackQueryHandler(start_parsing_students, pattern=r"^start_parsing_students$"))

    


    # Message handler for broadcast messages (text, photo, media group)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_broadcast_message))

    application.run_polling()


if __name__ == "__main__":
    main_bot()

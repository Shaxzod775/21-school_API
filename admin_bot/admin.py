import sys
sys.path.append("..")

import glob
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from db_modules.db import *  
from configs.config_bot import *
from api.main import *
from test_bot.api_helper import *

def get_admin_chat_id():
    with open("admin_chatId.txt", "r") as f:
        return int(f.read())


MEDIA_GROUP_IMAGE_DIR = "media_group_images"


BROADCAST_CHOICE, AWAITING_MESSAGE, AWAITING_MEDIA_GROUP, CONFIRM_PREVIOUS_MEDIA_GROUP = range(4)




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and shows the broadcast choice buttons."""
    keyboard = [
        [InlineKeyboardButton("Сделать рассылку", callback_data="broadcast_choice")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_id = update.effective_chat.id

    users = get_all_users_chatId("../bot_databases/users.db")
    authenticated_users = get_number_of_users_authenticated_in_bot("../bot_databases/users.db")


    with open("images/jerry.jpg", "rb") as image:
        await context.bot.send_photo(photo=image, caption=f"Саламалексус админ!\n\nКол-во пользователей в боте: {len(users)}\n\nАвторизовано: {authenticated_users}", chat_id=chat_id, reply_markup=reply_markup)


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


def main() -> None:
    application = ApplicationBuilder().token(TOKEN_ADMIN_BOT).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel_broadcast_init)) # Add direct cancel command

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
    application.add_handler(CallbackQueryHandler(cancel_broadcast_init, pattern="cancel_broadcast_init")) # Handle cancel from choice buttons

    # Message handler for broadcast messages (text, photo, media group)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_broadcast_message))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
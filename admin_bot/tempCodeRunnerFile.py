    elif re.match(r"^T\d{2}D\d{2}$|^E\d{2}D\d{2}$|^P\d{2}D\d{2}$", query.data):
        script_path = os.path.join(os.path.dirname(__file__), "../api/main.py")
        main_directory = os.path.dirname(script_path)

        original_directory = os.getcwd()
        try:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Скрипт начал работу...")

            keyboard = [[InlineKeyboardButton("Скриншот терминала", callback_data="send_screenshot")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_reply_markup(reply_markup=reply_markup)

            os.chdir(main_directory)
            os.system(f"powershell.exe -Command \"Start-Process 'wsl.exe' -ArgumentList '-e bash -c \"cd {main_directory} && source ../venv/bin/activate && python3 main.py {query.data} march\"'\"")

            await context.bot.send_message(chat_id=update.effective_chat.id, text="Скрипт успешно завершен.", reply_markup=reply_markup)  # Moved reply_markup here
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка при выполнении скрипта: {e}")
        finally:
            os.chdir(original_directory)
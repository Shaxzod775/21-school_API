TASKS_INTENSIVE_BOT = {
    # FIRST WEEK
    'T01D01': 19153,
    'T02D02': 19154,
    'T03D03': 19155,
    'T04D04': 19156,
    'E01D05': 19157,
    'P01D06': 19160,
    # SECOND WEEK
    'T05D08': 19161,
    'T06D09': 19162,
    'T07D10': 19163,
    'T08D11': 62331,
    'E02D12': 19368,
    'P02D13': 19165,
    # THIRD WEEK
    'T09D15': 19166,
    'T10D16': 19168,
    'T11D17': 19169,
    'T12D18': 19170,
    'E03D19': 19369,
    'P03D20': 19171,
    #FOURTH WEEK
    'T13D22': 19172,
    'T14D23': 19173,
    'T15D24': 19174,
    'E04D26': 19459,
}

FIRST_WEEK_INTENSIVE = {
    'T01D01': 19153,
    'T02D02': 19154,
    'T03D03': 19155,
    'T04D04': 19156,
    'E01D05 (exam)': 19157,
    'P01D06 (group project)': 19160
}

SECOND_WEEK_INTENSIVE = {
    'T05D08': 19161,
    'T06D09': 19162,
    'T07D10': 19163,
    'T08D11': 62331,
    'E02D12 (exam)': 19368,
    'P02D13 (group project)': 19165
}

THIRD_WEEK_INTENSIVE = {
    'T09D15': 19166,
    'T10D16': 19168,
    'T11D17': 19169,
    'T12D18': 19170,
    'E03D19 (exam)': 19369,
    'P03D20 (group project)': 19171,
}

FOURTH_WEEK_INTENSIVE = {
    'T13D22': 19172,
    'T14D23': 19173,
    'T15D24': 19174,
    'E04D26 (exam)': 19459,
}

TOKEN = '8180010320:AAF7CF6M9BFeVnJu78XfAXpBvz6n7Nq786k' 
TELEGRAPH_TOKEN = 'b0994b00bcab357cdb5a579123e57c7484db31abe61e06d83775bb4abe6d'
TOKEN_ADMIN_BOT = '7576903606:AAHWaZRnbmn4GWLEvZGnBU2mRYqn7G7rvc8'


KEYBOARDS = {
    "language_selected": { 
        "keyboard": {
            "english": ["Uzbekistan"],
            "russian": ["Узбекистан"],
            "uzbek": ["Oʻzbekiston"]
        },
        "message": {  
            "english": "You chose English. Now, please choose your country",  
            "russian": "Вы выбрали Русский. Теперь, пожалуйста, выберите вашу страну", 
            "uzbek": "Siz o'zbek tilini tanladingiz. Endi, iltimos, o'z mamlakatingizni tanlang." 
        }
    },
    "country_selected" : {
        "keyboard": {
            "english": ["Tashkent", "Samarkand"],
            "russian": ["Ташкент", "Самарканд"],
            "uzbek": ["Toshkent", "Samarqand"]
        },
        "message": {  
            "english": "Choose your campus",  
            "russian": "Выберите ваш кампус", 
            "uzbek": "Kampusingizni tanlang" 
        }
    },
    "campus_selected" : {
        "keyboard": {
            "english": ["Intensiv"],
            "russian": ["Интенсив"],
            "uzbek": ["Intensiv"]
        },
        "message": {  
            "english": "Now, please choose your stage of education",  
            "russian": "Теперь пожалуйста выберите ваш поток", 
            "uzbek": "Endi, iltimos, o'z oqimingizni tanlang" 
        }
    },
    "show_main_options" : {
        "keyboard": {
            "english": [{"text": "Profile", "callback_data" : "profile"}, {"text":"Task Statistics", "callback_data" : "stats"}, {"text": "Language", "callback_data": "change_language"}, {"text": "Campus", "callback_data": "change_campus"}, {"text": "Past Intensives", "callback_data": "previous_intensives"}],
            "russian": [{"text": "Профиль", "callback_data" : "profile"}, {"text":"Статистика по заданиям", "callback_data" : "stats"}, {"text": "Язык", "callback_data": "change_language"}, {"text": "Кампус", "callback_data": "change_campus"}, {"text": "Прошлые интенсивы", "callback_data": "previous_intensives"}],
            "uzbek": [{"text": "Profil", "callback_data" : "profile"}, {"text":"Topshiriqlar statistikasi", "callback_data" : "stats"}, {"text": "Til", "callback_data": "change_language"}, {"text": "Kampus", "callback_data": "change_campus"}, {"text": "O\'tgan intensivlar", "callback_data": "previous_intensives"}]
        },
        "caption_during_intensive": {  
            "english": "🏫 Campus: {campus}\n\n✅ Actively visiting the campus: {num_active_students} out of {num_students}\n\n🧑🏻If the buttons are not working, please enter /start",  
            "russian": "🏫 Кампус: {campus}\n\n✅ Активно посещают кампус: {num_active_students} из {num_students}\n\nЕсли кнопки не жмуться введите /start", 
            "uzbek": "🏫 Kampus: {campus}\n\n✅ Kampusga faol tashrif buyuruvchilar: {num_students} dan {num_active_students}\n\nAgar tugmalar ishlamasa\, iltimos\, /start kiriting" 
        },
        # "caption_during_intensive": {  
        #     "english": "🏫 Campus: {campus}\n\n✅ Actively visiting the campus: {num_active_students} out of {num_students}\n\n🧑🏻‍🎓 Best student in the campus: {student} \( Level {level} \| {exp} exp \)\n\n If the buttons are not working, please enter /start",  
        #     "russian": "🏫 Кампус: {campus}\n\n✅ Активно посещают кампус: {num_active_students} из {num_students}\n\n🧑🏻‍🎓 Лучший студент в кампусе: {student} \( {level} уровень \| {exp} exp \)\n\nЕсли кнопки не жмуться введите /start", 
        #     "uzbek": "🏫 Kampus: {campus}\n\n✅ Kampusga faol tashrif buyuruvchilar: {num_students} dan {num_active_students}\n\n🧑🏻‍🎓 Kampusda eng yaxshi talaba: {student} \( {level} daraja \| {exp} tajriba \)\n\nAgar tugmalar ishlamasa\, iltimos\, /start kiriting" 
        # },
        "caption_out_of_intensive": {
            "english": "🏫 Campus: {campus}\n\n🙃The last intensive is over\. Waiting for the start of the new one\n\n🫠You can view reports on past intensives by clicking the \"Past Intensives\" button\n\nIf the buttons are not working, please enter /start",  
            "russian": "🏫 Кампус: {campus}\n\n🙃Последний интенсив завершен\. Ждем начало нового интенсива\n\n🫠Пока вы можете посмотреть отчеты по прошлым интенсивам нажав на кнопку \"Прошлые интенсивы\"\n\nЕсли кнопки не жмуться введите /start", 
            "uzbek": "🏫 Kampus: {campus}\n\n🙃Oxirgi intensiv tugadi\. Yangi intensiv boshlanishini kutyapmiz\n\n🫠Siz \"O\'tgan intensivlar\" tugmasini bosib, oldingi intensivlar bo\'yicha hisobotlarni ko\'rishingiz mumkin" 
        },
        "caption_unauthorized": {
            "english": "😃 For more information please authorize by clicking on \"Profile\" button\n",  
            "russian": "😃 Для получения дополнительной информации, пожалуйста, авторизуйтесь, нажав на кнопку \"Профиль\"\n", 
            "uzbek": "😃 Qo'shimcha ma'lumot olish uchun, \"Profil\" tugmasini bosib, avtorizatsiyadan o'ting\n" 
        },
        "caption_authorized": {
            "english": "🏫 Campus: {campus}\n\n✅ Actively visiting the campus: {num_active_students} out of {num_students}\n\n🧑🏻‍🎓 Best student in the campus: {student} \(Level {level}, {exp} exp\)\n",  
            "russian": "🏫 Кампус: {campus}\n\n✅ Активно посещают кампус: {num_active_students} из {num_students}\n\n🧑🏻‍🎓 Лучший студент в кампусе: {student} \({level} уровень, {exp} exp\)\n\n\n", 
            "uzbek": "🏫 Kampus: {campus}\n\n✅ Kampusga faol tashrif buyuruvchilar: {num_students} dan {num_active_students}\n\n🧑🏻‍🎓 Kampusda eng yaxshi talaba: {student} \({level} daraja, {exp} tajriba\)\n" 
        },
    },
    "change_campus" : {
        "keyboard": {
            "english": [{"text":["Tashkent", "Samarkand"]}, {"text": "Go Back", "callback_data": "go_back"}],
            "russian": [{"text":["Ташкент", "Самарканд"]}, {"text": "Назад", "callback_data": "go_back"}],
            "uzbek": [{"text":["Toshkent", "Samarqand"]}, {"text": "Ortga", "callback_data": "go_back"}],
        },
        "caption": {
            "english": "The campus you chose is",
            "russian": "Выбранный вами кампус:",
            "uzbek": "Siz tanlagan kampus:",
        }
    },
    "button" : {
        "stats" : {
            "keyboard": {
                "english": [{"text":"1 week", "callback_data" : "stats_intensive_week_1"}, {"text":"2 week", "callback_data" : "stats_intensive_week_2"}, {"text":"3 week", "callback_data" : "stats_intensive_week_3"}, {"text":"4 week", "callback_data" : "stats_intensive_week_4"}, {"text": "Go Back", "callback_data": "go_back"}],
                "russian": [{"text":"1 неделя", "callback_data" : "stats_intensive_week_1"}, {"text":"2 неделя", "callback_data" : "stats_intensive_week_2"}, {"text":"3 неделя", "callback_data" : "stats_intensive_week_3"}, {"text":"4 неделя", "callback_data" : "stats_intensive_week_4"}, {"text": "Назад", "callback_data": "go_back"}],
                "uzbek": [{"text":"1 hafta", "callback_data" : "stats_intensive_week_1"}, {"text":"2 hafta", "callback_data" : "stats_intensive_week_2"}, {"text":"3 hafta", "callback_data" : "stats_intensive_week_3"}, {"text":"4 hafta", "callback_data" : "stats_intensive_week_4"}, {"text": "Ortga", "callback_data": "go_back"}],
            }
        }
    },
    "show_specific_task_info": {
        "stats" : {
            "keyboard": {
                "english": [{"text":"1 week", "callback_data" : "stats_intensive_week_1"}, {"text":"2 week", "callback_data" : "stats_intensive_week_2"}, {"text":"3 week", "callback_data" : "stats_intensive_week_3"}, {"text":"4 week", "callback_data" : "stats_intensive_week_4"}, {"text": "Go Back", "callback_data": "go_back"}],
                "russian": [{"text":"1 неделя", "callback_data" : "stats_intensive_week_1"}, {"text":"2 неделя", "callback_data" : "stats_intensive_week_2"}, {"text":"3 неделя", "callback_data" : "stats_intensive_week_3"}, {"text":"4 неделя", "callback_data" : "stats_intensive_week_4"}, {"text": "Назад", "callback_data": "go_back"}],
                "uzbek": [{"text":"1 hafta", "callback_data" : "stats_intensive_week_1"}, {"text":"2 hafta", "callback_data" : "stats_intensive_week_2"}, {"text":"3 hafta", "callback_data" : "stats_intensive_week_3"}, {"text":"4 hafta", "callback_data" : "stats_intensive_week_4"}, {"text": "Ortga", "callback_data": "go_back"}],
                }
            },
        "other_campus_stats_button" : {
            "english": {"text":"Show the report of the other campus", "callback_data" : "show_other_campus_stats"},
            "russian": {"text":"Показать отчёт по другому кампусу", "callback_data" : "show_other_campus_stats"},
            "uzbek": {"text":"Boshqa kampus bo'yicha hisobotni ko'rsatish", "callback_data" : "show_other_campus_stats"},
        },
    },
    "show_profile" : {
        "keyboard": {
            "english": "Log In",
            "russian": "Авторизоваться",
            "uzbek": "Тизимга кириш",
        }
    },
    "authorize_user" : {
        "keyboard": {
            "english": [{"text": "Go Back", "callback_data": "go_back"}],
            "russian": [{"text": "Назад", "callback_data": "go_back"}],
            "uzbek": [{"text": "Ortga", "callback_data": "go_back"}],
        },
        "caption": {
            "english": "Enter your username from https://edu.21-school.ru/",
            "russian": "Введите свой логин от https://edu.21-school.ru/",
            "uzbek": "https://edu.21-school.ru/ saytidan loginingizni kiriting.",
        }
    },
    "handle_text": {
        "enter_login": {
            "english": "Enter your login",
            "russian": "Введите ваш логин",
            "uzbek": "Loginingizni kiriting",
        },
        "login_saved": {
            "english": "Login has been saved. Now enter your password",
            "russian": "Логин сохранён. Теперь введите ваш пароль",
            "uzbek": "Login qabul qilindi. Endi parolingizni kiriting",
        },
        "success": {
            "english": "You have successfully authorized!",
            "russian": "Вы успешно авторизовались!",
            "uzbek": "Муваффақиятли авторизациядан ўтдингиз!",
        },
        "failure": {
            "english": "Incorrect login or password! Please try again.",
            "russian": "Логин или пароль неверны! Попробуйте снова.",
            "uzbek": "Login yoki parol noto'g'ri! Qayta dan urinib ko'ring.",
        },

    },
    "show_previous_intensives": {
        "text_campuses": {
            "english": "Choose the campus",
            "russian": "Выберите кампус",
            "uzbek": "Kampusni tanlang",
        },
        "keyboard_campuses": {
            "english": [{"text": "Tashkent", "callback_data": "show_previous_intensives_tashkent"}, {"text": "Samarkand", "callback_data": "show_previous_intensives_samarkand"}, {"text": "Go Back", "callback_data": "go_back"}],
            "russian": [{"text": "Ташкент", "callback_data": "show_previous_intensives_tashkent"}, {"text": "Самарканд", "callback_data": "show_previous_intensives_samarkand"}, {"text": "Назад", "callback_data": "go_back"}],
            "uzbek": [{"text": "Toshkent", "callback_data": "show_previous_intensives_tashkent"}, {"text": "Samarkand", "callback_data": "show_previous_intensives_samarkand"}, {"text": "Ortga", "callback_data": "go_back"}],
        },
        "keyboard_intensives_tashkent": {
            "english": [{"text": "November 2024", "callback_data": "show_previous_tashkent_november_2024"}, {"text": "February 2025", "callback_data": "show_previous_tashkent_february_2025"}, {"text": "Go Back", "callback_data": "go_back"}],
            "russian": [{"text": "Ноябрь 2024", "callback_data": "show_previous_tashkent_november_2024"}, {"text": "Февраль 2025", "callback_data": "show_previous_tashkent_february_2025"}, {"text": "Назад", "callback_data": "go_back"}],
            "uzbek": [{"text": "Noyabr 2024", "callback_data": "show_previous_tashkent_november_2024"}, {"text": "Fevral 2025", "callback_data": "show_previous_tashkent_february_2025"}, {"text": "Ortga", "callback_data": "go_back"}],
        },
        "keyboard_intensives_samarkand": {
            "english": [{"text": "February 2025", "callback_data": "show_previous_samarkand_february_2025"}, {"text": "Go Back", "callback_data": "go_back"}],
            "russian": [{"text": "Февраль 2025", "callback_data": "show_previous_samarkand_february_2025"}, {"text": "Назад", "callback_data": "go_back"}],
            "uzbek": [ {"text": "Fevral 2025", "callback_data": "show_previous_samarkand_february_2025"}, {"text": "Ortga", "callback_data": "go_back"}],
        },
    }
}


XXX = "0836"

MAKE_CONTENT = {
    "title": {
        "english": "Nickname, Percent for the project",
        "russian": "Никнейм, Процент за проект",
        "uzbek": "Nikneym, Loyiha uchun foiz"
    }
}


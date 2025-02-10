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
    'E01D05': 19157,
    'P01D06': 19160
}

SECOND_WEEK_INTENSIVE = {
    'T05D08': 19161,
    'T06D09': 19162,
    'T07D10': 19163,
    'T08D11': 62331,
    'E02D12': 19368,
    'P02D13': 19165
}

THIRD_WEEK_INTENSIVE = {
    'T09D15': 19166,
    'T10D16': 19168,
    'T11D17': 19169,
    'T12D18': 19170,
    'E03D19': 19369,
    'P03D20': 19171,
}

FOURTH_WEEK_INTENSIVE = {
    'T13D22': 19172,
    'T14D23': 19173,
    'T15D24': 19174,
    'E04D26': 19459,
}

TOKEN = '7168050647:AAFvWtm2G-qslN1U6K4zv1Y8L7CyhYXs8R0' 
TELEGRAPH_TOKEN = 'b0994b00bcab357cdb5a579123e57c7484db31abe61e06d83775bb4abe6d'


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
            "english": [{"text":"Task Statistics", "callback_data" : "stats"}, {"text": "Language", "callback_data": "change_language"}, {"text": "Campus", "callback_data": "change_campus"}],
            "russian": [{"text":"Статистика по заданиям", "callback_data" : "stats"}, {"text": "Язык", "callback_data": "change_language"}, {"text": "Кампус", "callback_data": "change_campus"}],
            "uzbek": [{"text":"Topshiriqlar statistikasi", "callback_data" : "stats"}, {"text": "Til", "callback_data": "change_language"}, {"text": "Kampus", "callback_data": "change_campus"}]
        },
        "caption": {  
            "english": "This bot was created to track statistics in the School 21 campuses in Uzbekistan",  
            "russian": "Бот создан для ведения статистики в кампусах школы 21 в Узбекистане", 
            "uzbek": "Bu bot O'zbekistondagi 21\-maktab kampuslari statistika yuritish uchun yaratilgan" 
        }
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
        }
    },
}

MAKE_CONTENT = {
    "title": {
        "english": "Nickname, Percent for the project",
        "russian": "Никнейм, Процент за проект",
        "uzbek": "Nikneym, Loyiha uchun foiz"
    }
}


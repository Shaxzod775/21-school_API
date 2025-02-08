import sys
sys.path.append("..")

import requests
from config_api import *
from config import *


# # Step 1: Create a new Telegraph account (only needed once)
# def create_telegraph_account():
#     url = "https://api.telegra.ph/createAccount"
#     data = {
#         "short_name": "Shaxzod",
#         "author_name": "Shaxzod775",
#         "author_url": "https://t.me/Shaxzod775"
#     }
#     response = requests.post(url, json=data).json()
#     return response.get("result", {}).get("access_token")

# Step 2: Create a new post
def create_telegraph_post(access_token, title, content):
    url = "https://api.telegra.ph/createPage"
    data = {
        "access_token": access_token,
        "title": title,
        "author_name": "Glassole",
        "content": content, 
        "return_content": True
    }
    response = requests.post(url, json=data).json()
    return response


def make_content(students):
    content = [
        {"tag": "p", "children": ["Никнейм, Процент за проект"]}
    ]

    # Append each student entry as a hyperlink
    content.extend([
        {"tag": "p", "children": [
            {"tag": "a", "attrs": {"href": f"https://edu.21-school.ru/profile/{student[0]}"}, "children": [f"{student[0]}, {student[1]}"]}
        ]}
        for student in students
    ])

    return content


# Example usage
# access_token = TELEGRAPH_TOKEN  # Only needed once; save the token

# content = [
#     {"tag": "p", "children": [
#         f"Никнейм, Процент за проэкт"
#     ]},
#     {"tag": "a", "attrs": {"href": "https://edu.21-school.ru/profile/orivelam"}, "children": ["awesome link"]},
#     " for more info. orivelam",
#     # {"tag": "p", "children": [
#     #     "Follow us on ",
#     #     {"tag": "a", "attrs": {"href": "https://t.me/mychannel"}, "children": ["Telegram"]},
#     #     "!"
#     # ]}
# ]



# report = make_report("E01D05")
# text = report['report']

# passed_students = report['passed_students'] 
# scored_hundred = report['scored_hundred'] 
# scored_didnt_pass = report['scored_didnt_pass'] 
# in_progress = report['in_progress'] 
# in_reviews = report['in_reviews'] 
# registered = report['registered'] 

# make_content(passed_students)





# content = [
#     {"tag": "p", "children": [
#         f"Список учеников 123:"
#     ]},
#     {"tag": "p", "children": [
#         f"Check out this",
#         {"tag": "a", "attrs": {"href": "https://edu.21-school.ru/profile/orivelam"}, "children": ["awesome link"]},
#         " for more info. orivelam"
#     ]},
#     {"tag": "p", "children": [
#         "Follow us on ",
#         {"tag": "a", "attrs": {"href": "https://t.me/mychannel"}, "children": ["Telegram"]},
#         "!"
#     ]}
# ]

# post = create_telegraph_post(TELEGRAPH_TOKEN, "Список учеников", content)
# print(post)



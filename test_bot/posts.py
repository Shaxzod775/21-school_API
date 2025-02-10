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


def make_content(students, task_id, language):
    if language not in ("english", "russian", "uzbek"):
        raise Exception(f"The text in given language cannot be displayed! {language}")

    title = MAKE_CONTENT['title'][language]

    content = [
        {"tag": "p", "children": [title]}
    ]

    # Append each student entry as a hyperlink
    content.extend([
        {"tag": "p", "children": [
            {"tag": "a", "attrs": {"href": f"https://edu.21-school.ru/profile/{student[0]}/project/{task_id}/about"}, "children": [f"{student[0]}, {student[1]}"]}
        ]}

        for student in students
    ])

    return content



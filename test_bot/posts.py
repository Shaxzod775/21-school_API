import sys
sys.path.append("..")

import requests
from config_api import *
from config import *
import json 


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

# def create_telegraph_post(access_token, title, content):
#     try:
#         url = "https://api.telegra.ph/createPage"
#         data = {
#             "access_token": access_token,
#             "title": title,
#             "author_name": "Glassole",
#             "content": content, 
#             "return_content": True
#         }
#         response = requests.post(url, data=data) #Your request
#         response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

#         response_json = json.loads(response.text) #Load the response to json

#         if response_json.get('ok'): #Check if 'ok' is in the json response
#             print("POST HAS BEEN CREATED!!!")
#             return response_json #If ok, then return the response
#         else:
#             print(f"Telegraph API Error: {response_json.get('error')}") #Print error
#             return {'result': {'url': ""}} #Return empty url
#     except requests.exceptions.RequestException as e:
#         print(f"Error communicating with Telegraph API: {e}")
#         return {'result': {'url': ""}}  # Return a default value in case of error
#     except json.JSONDecodeError as e: # Catch json decode error
#         print(f"Error decoding JSON response: {e}, Response: {response.text}")
#         return {'result': {'url': ""}}


# def make_content(students, task_id, language):
#     if language not in ("english", "russian", "uzbek"):
#         raise Exception(f"The text in given language cannot be displayed! {language}")

#     title = MAKE_CONTENT['title'][language]

#     content = [
#         {"tag": "p", "children": [title]}
#     ]

#     # Append each student entry as a hyperlink
#     # content.extend([
#     #     {"tag": "p", "children": [
#     #         {"tag": "a", "attrs": {"href": f"https://edu.21-school.ru/profile/{student[0]}/project/{task_id}/about"}, "children": [f"{student[0]}, {student[1]}"]}
#     #     ]}

#     #     for student in students
#     # ])

#     content.extend([
#         {"tag": "p", "children": [
#             {"tag": "a", 
#             "attrs": {"href": f"https://edu.21-school.ru/profile/{student[0]}/project/{task_id}/about"}, 
#             "children": [f"{student[0]}, {student[1]}"]}  # Ensure the child is a text node
#         ]}
#         for student in students
#     ])

#     return content


if __name__ == "__main__":
    students = [['advisorj', '27']]


    post = create_telegraph_post(TELEGRAPH_TOKEN, "dicks", make_content(students, 19153, "english"))['result']['url']
    print(post)

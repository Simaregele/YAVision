# coding: utf-8
from requests import post
import json
import base64
from credentials import FOLDER_ID, OAUTH_TOKEN, IMAGE_PATH
from parse_dialog import group_words_by_line, prepare_data, group_data_by_x, build_dialogue
import numpy as np


# The function returns the IAM token for the Yandex account.
def get_iam_token(iam_url, oauth_token):
    response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
    json_data = json.loads(response.text)
    if json_data is not None and 'iamToken' in json_data:
        return json_data['iamToken']
    return None


# The function sends an image recognition request to the server and returns a response from the  server.
def request_analyze(vision_url, iam_token, folder_id, image_data):
    response = post(vision_url, headers={'Authorization': 'Bearer '+iam_token}, json={
        'folderId': folder_id,
        'analyzeSpecs': [
            {
                'content': image_data,
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'textDetectionConfig': {'languageCodes': ['en', 'ru']}
                    }
                ],
            }
        ]})
    return response.text


def main():
    iam_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    iam_token = get_iam_token(iam_url, OAUTH_TOKEN)
    with open(IMAGE_PATH, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    response_text = request_analyze(vision_url, iam_token, FOLDER_ID, image_data)
    # Преобразование JSON строки в объект Python
    json_data = json.loads(response_text)


    # Пример использования
    lines_dict = group_words_by_line(json_data)  # Предполагаем, что lines_dict уже заполнен
    # Группировка данных
    print(lines_dict)
    prepared_data = prepare_data(lines_dict)

    groups = group_data_by_x(prepared_data, 10)

    # Построение диалога
    dialogue = build_dialogue(prepared_data, groups)

    # Вывод диалога
    for sender, message in dialogue:
        print(f"{sender}: {message}")

if __name__ == '__main__':
    main()

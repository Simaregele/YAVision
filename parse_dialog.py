import numpy as np


def group_words_by_line_last(json_data):
    lines_dict = {}
    for result in json_data['results']:
        for page in result['results']:
            for block in page['textDetection']['pages'][0]['blocks']:
                for line in block['lines']:
                    # Находим Y координату строки
                    line_y = int(line['words'][0]['boundingBox']['vertices'][0]['y'])

                    # Находим X координату самого правого слова в строке
                    max_word_x = max(int(word['boundingBox']['vertices'][2]['x']) for word in line['words'])

                    # Формируем ключ из максимального X и Y
                    line_key = (max_word_x, line_y)

                    # Добавляем все слова в словарь для данной строки
                    if line_key not in lines_dict:
                        lines_dict[line_key] = []

                    lines_dict[line_key].extend([word['text'] for word in line['words']])

    return lines_dict


def group_words_by_line(json_data):
    lines_dict = {}
    for result in json_data['results']:
        for page in result['results']:
            for block in page['textDetection']['pages'][0]['blocks']:
                for line in block['lines']:
                    # Сортируем слова по X координате, чтобы найти первое слово
                    sorted_words = sorted(line['words'], key=lambda w: int(w['boundingBox']['vertices'][0]['x']))
                    first_word_x = int(sorted_words[0]['boundingBox']['vertices'][0]['x'])

                    # Условно считаем, что Y координата первого слова представляет всю строку
                    line_y = int(sorted_words[0]['boundingBox']['vertices'][0]['y'])

                    # Формируем ключ из координат первого слова
                    line_key = (first_word_x, line_y)

                    # Добавляем все слова в словарь для данной строки
                    if line_key not in lines_dict:
                        lines_dict[line_key] = []

                    lines_dict[line_key].extend([word['text'] for word in sorted_words])

    return lines_dict


def group_data_by_x(extracted_data, max_distance):
    """
    Группировка данных по близости значений X.

    :param extracted_data: Список кортежей в формате (X, текст сообщения)
    :param max_distance: Максимальное расстояние между значениями X для группировки
    :return: Список групп данных
    """
    # Преобразование X в числовой формат для сортировки и вычислений
    extracted_data_converted = [(int(x), text) for x, text in extracted_data]
    extracted_data_sorted = sorted(extracted_data_converted, key=lambda x: x[0])
    groups = []
    current_group = [extracted_data_sorted[0]]

    for i in range(1, len(extracted_data_sorted)):
        x, text = extracted_data_sorted[i]
        prev_x, _ = current_group[-1]

        if abs(x - prev_x) <= max_distance:
            current_group.append((x, text))
        else:
            groups.append(current_group)
            current_group = [(x, text)]

    if current_group:
        groups.append(current_group)

    return groups


def build_dialogue(data, groups):
    """
    Построение диалога с учетом группировки данных.

    :param data: Исходные данные в формате (X, текст сообщения)
    :param groups: Группы данных, возвращаемые функцией group_data_by_x
    :return: Список сообщений с указанием отправителя
    """
    largest_group_index = max(range(len(groups)), key=lambda i: len(groups[i]))
    group_sender_mapping = {i: "Отправитель 1" if i == largest_group_index else "Отправитель 2" for i in range(len(groups))}

    rebuilt_dialogue = []
    current_sender = None
    current_message = ""

    for x, message in data:
        # Преобразование message в строку на случай, если это не строка
        message = str(message)

        sender = next((group_sender_mapping[index] for index, group in enumerate(groups) if int(x) in [item[0] for item in group]), None)

        if sender != current_sender:
            if current_message:
                rebuilt_dialogue.append((current_sender, current_message.strip()))
            current_sender = sender
            current_message = message
        else:
            current_message += " " + message

    if current_message:
        rebuilt_dialogue.append((current_sender, current_message.strip()))

    return rebuilt_dialogue


def prepare_data(data_dict):
    """
    Преобразование словаря данных в список кортежей для дальнейшей обработки.

    :param data_dict: Словарь с ключами в виде кортежей координат (X, Y) и значениями в виде списков слов.
    :return: Список кортежей в формате (X, текст сообщения)
    """
    prepared_data = []
    for (x, _), words in data_dict.items():
        message = ' '.join(words)
        prepared_data.append((x, message))
    return prepared_data
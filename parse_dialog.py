

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


def group_data_by_x(data_dict, max_distance):
    """
    Группировка данных по близости значений X.
    :param data_dict: Словарь с ключами в виде кортежей координат (X, Y) и значениями в виде списков слов.
    :param max_distance: Максимальное расстояние между значениями X для группировки
    :return: Список групп данных
    Функция сортирует по X и затем смотрит если значение меньше чем в 10 пикселей от X то значит это одна группа,
    в ином случае вторая группа.
    Смотрит по самому минимальному X
    """
    # Преобразование данных в список кортежей (X, текст сообщения)
    extracted_data = []
    for (x, _), words in data_dict.items():
        message = ' '.join(words)
        extracted_data.append((x, message))
    # Сортировка данных по X
    extracted_data_sorted = sorted(extracted_data, key=lambda x: x[0])
    groups = []
    current_group = [extracted_data_sorted[0]]
    # Группировка данных
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


def build_dialogue(data_dict, groups):
    """
    Построение диалога с учетом группировки данных.
    :param data_dict: Словарь с ключами в виде кортежей координат (X, Y) и значениями в виде списков слов.
    :param groups: Группы данных, возвращаемые функцией group_data_by_x
    :return: Список сообщений с указанием отправителя

    """
    largest_group_index = max(range(len(groups)), key=lambda i: len(groups[i]))
    group_sender_mapping = {i: "Отправитель 1" if i == largest_group_index else "Отправитель 2" for i in range(len(groups))}
    rebuilt_dialogue = []
    current_sender = None
    current_message = ""
    for (x, _), words in data_dict.items():
        message = ' '.join(words)
        sender = next((group_sender_mapping[index] for index, group in enumerate(groups) if x in [item[0] for item in group]), None)
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

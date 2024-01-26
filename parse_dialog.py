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


def extract_and_sort_data(data_dict):
    extracted_data = [(x, ' '.join(words)) for (x, _), words in data_dict.items()]
    return sorted(extracted_data, key=lambda x: x[0])


def process_anomalies(groups, anomalies):
    if groups:
        first_group_x = groups[0][0][0]
        last_group_x = groups[-1][0][0]
        for x_anomaly, text_anomaly in anomalies:
            if abs(x_anomaly - first_group_x) < abs(x_anomaly - last_group_x):
                groups[0].append((x_anomaly, text_anomaly))
            else:
                groups[-1].append((x_anomaly, text_anomaly))


def group_data_by_x(data_dict, max_distance):
    """Группировка данных по близости значений X."""
    extracted_data_sorted = extract_and_sort_data(data_dict)
    groups = []
    anomalies = []
    current_group = [extracted_data_sorted[0]]
    for x, text in extracted_data_sorted[1:]:
        prev_x, _ = current_group[-1]
        if abs(x - prev_x) <= max_distance:
            current_group.append((x, text))
        else:
            if len(current_group) == 1:
                anomalies.append(current_group[0])
            else:
                groups.append(current_group)
            current_group = [(x, text)]
    if current_group:
        groups.append(current_group)
    process_anomalies(groups, anomalies)
    return groups


def build_dialogue(data_dict, groups):
    # Назначаем метки отправителей на основе порядка групп
    group_sender_mapping = {i: f"Отправитель {i + 1}" for i in range(len(groups))}
    rebuilt_dialogue = []
    current_sender = None
    current_message = ""
    for (x, _), words in data_dict.items():
        message = ' '.join(words)
        # Определяем отправителя на основе группы, в которую попадает сообщение
        sender = next(
            (group_sender_mapping[index] for index, group in enumerate(groups) if x in [item[0] for item in group]),
            None)
        if sender != current_sender:
            if current_message:
                rebuilt_dialogue.append((current_sender, current_message.strip()))
            current_sender = sender
            current_message = message
        else:
            current_message += " " + message
    # Добавляем последнее сообщение
    if current_message:
        rebuilt_dialogue.append((current_sender, current_message.strip()))
    return rebuilt_dialogue

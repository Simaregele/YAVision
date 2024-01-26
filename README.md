# импорт зависимостей происходит из файла credentials.py

###Импорт `from credentials import FOLDER_ID, OAUTH_TOKEN, IMAGE_PATH`

#main.py

# Импорт зависимостей

Импортируются необходимые модули (requests для HTTP-запросов, json для работы с JSON, base64 для кодирования данных изображения) и переменные из `credentials` и `parse_dialog`.

## Функция `get_iam_token(iam_url, oauth_token)`

### Описание
Получает IAM токен для аккаунта Yandex.

### Параметры
- `iam_url`: URL-адрес для получения IAM токена.
- `oauth_token`: OAuth токен пользователя.

### Возвращает
IAM токен или `None`, если токен не был получен.

### Логика работы
1. Отправка POST-запроса на `iam_url`.
2. Разбор ответа и извлечение IAM токена.

## Функция `request_analyze(vision_url, iam_token, folder_id, image_data)`

### Описание
Отправляет запрос на анализ изображения в сервис Yandex Vision.

### Параметры
- `vision_url`: URL-адрес сервиса Yandex Vision.
- `iam_token`: IAM токен для аутентификации.
- `folder_id`: Идентификатор папки в Yandex Cloud.
- `image_data`: Данные изображения в формате base64.

### Возвращает
Ответ сервера в виде текста.

### Логика работы
Формирование и отправка POST-запроса с данными изображения и параметрами анализа.

## Главная функция `main()`

### Логика работы
1. Получение IAM токена.
2. Чтение и кодирование изображения.
3. Отправка запроса на анализ изображения.
4. Обработка ответа и извлечение текста из изображения.
5. Использование функций `group_words_by_line`, `group_data_by_x` и `build_dialogue` из модуля `parse_dialog` для обработки текста.
6. Вывод результата в виде диалога.

## Выполнение функции `main()` при запуске скрипта

При запуске скрипта как главного файла (`__name__ == '__main__'`) вызывается функция `main()`.




#parse_dialog.py

# Функции обработки данных

## Функция `group_words_by_line(json_data)`

### Описание
Группирует слова по строкам на основе их координат в пределах блока текста.

### Параметры
- `json_data`: Объект JSON, содержащий текстовые данные для анализа.

### Возвращает
Словарь, где ключ - это кортеж с координатами X и Y первого слова в строке, а значение - список слов в этой строке.

### Логика работы
1. Перебор всех блоков текста и строк в этих блоках.
2. Сортировка слов в каждой строке по координате X для определения порядка слов в строке.
3. Использование координат первого слова в строке как ключа для группировки слов.

## Функция `extract_and_sort_data(data_dict)`

### Описание
Извлекает и сортирует данные для дальнейшей обработки.

### Параметры
- `data_dict`: Словарь данных, полученный из функции `group_words_by_line`.

### Возвращает
Отсортированный список кортежей, содержащих координаты и соответствующий объединенный текст.

### Логика работы
1. Преобразование словаря в список кортежей.
2. Сортировка списка по координате X.

## Функция `process_anomalies(groups, anomalies)`

### Описание
Обрабатывает аномальные данные, распределяя их между группами.

### Параметры
- `groups`: Список групп данных.
- `anomalies`: Список аномальных данных.

### Логика работы
Распределение аномалий между первой и последней группой на основе расстояния.

## Функция `group_data_by_x(data_dict, max_distance)`

### Описание
Группирует данные на основе близости значений X координаты.

### Параметры
- `data_dict`: Словарь данных для группировки.
- `max_distance`: Максимальное расстояние между элементами в группе.

### Возвращает
Список группированных данных.

### Логика работы
1. Сортировка и группировка данных на основе близости координат X.
2. Обработка аномальных данных, которые не вписываются в группы.

## Функция `build_dialogue(data_dict, groups)`

### Описание
Строит диалог на основе группированных данных.

### Параметры
- `data_dict`: Словарь данных, содержащий слова и их координаты.
- `groups`: Список групп данных.

### Возвращает
Структурированный диалог в виде списка кортежей (отправитель, сообщение).

### Логика работы
1. Назначение меток отправителей на основе порядка групп.
2. Определение отправителя для каждого сообщения на основе его принадлежности к группе.
3. Сборка и форматирование окончательного диалога.

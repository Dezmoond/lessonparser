import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URL страницы с мероприятиями
url = 'https://quicktickets.ru/chita-filarmoniya'

# Заголовки для имитации запроса от браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://quicktickets.ru/",
    "DNT": "1",
    "Connection": "keep-alive",
}

# Выполняем GET-запрос к странице
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    events = soup.find_all('div', class_='elem')

    events_data = []

    for event in events:
        # Название
        title_tag = event.find('span', class_='underline')
        title = title_tag.get_text(strip=True) if title_tag else 'Нет названия'

        # Описание
        description_tag = event.find('div', class_='d')
        description = description_tag.get_text(strip=True) if description_tag else 'Нет описания'

        # Даты
        sessions = event.find('div', class_='sessions')
        dates = []
        if sessions:
            date_tags = sessions.find_all('span', class_='underline')
            dates = [date.get_text(strip=True) for date in date_tags]

        # Ссылка на билеты
        ticket_link_tag = event.find('p', class_='b')
        ticket_link = ''
        if ticket_link_tag:
            a_tag = ticket_link_tag.find('a', href=True)
            if a_tag:
                ticket_link = 'https://quicktickets.ru' + a_tag['href']

        # Изображение мероприятия
        img_tag = event.find('img', class_='polaroid')
        image_url = img_tag['src'] if img_tag and img_tag.get('src') else ''

        # Собираем всё в словарь
        events_data.append({
            'title': title,
            'description': description,
            'dates': dates,
            'ticket_link': ticket_link,
            'image': image_url
        })

    # Сохраняем в JSON
    with open('events.json', 'w', encoding='utf-8') as f:
        json.dump(events_data, f, ensure_ascii=False, indent=4)

    print('✅ Данные успешно сохранены в файл events.json')
else:
    print(f'❌ Ошибка при получении страницы: {response.status_code}')


# Словарь русских месяцев
RU_MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
}

def parse_event_date(date_str):
    """
    Преобразует строку формата '16 мая 18:00' в datetime.
    Если дата уже прошла в текущем году — берёт следующий год.
    Возвращает datetime или None.
    """
    try:
        parts = date_str.strip().split()
        if len(parts) != 3:
            return None

        day = int(parts[0])
        month_name = parts[1].lower()
        time_str = parts[2]

        month = RU_MONTHS.get(month_name)
        if not month:
            return None

        now = datetime.now()
        year = now.year
        hour, minute = map(int, time_str.split(':'))

        event_date = datetime(year, month, day, hour, minute)

        # Если дата уже прошла — берём следующий год
        if event_date < now:
            event_date = datetime(year + 1, month, day, hour, minute)

        return event_date
    except Exception as e:
        print(f"❌ Ошибка разбора даты '{date_str}': {e}")
        return None


# --- Загрузка и обработка мероприятий ---
with open('events.json', encoding='utf-8') as f:
    events = json.load(f)

for event in events:
    parsed_dates = []
    for date_str in event.get("dates", []):
        dt = parse_event_date(date_str)
        if dt:
            parsed_dates.append(dt.isoformat())  # Можно заменить на dt.strftime('%Y-%m-%d %H:%M')
    event["parsed_dates"] = parsed_dates

# --- Сохраняем результат ---
with open('events_with_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=4)

print("✅ Даты успешно интерпретированы и сохранены в events_with_parsed.json")
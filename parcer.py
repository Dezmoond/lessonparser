import requests
from bs4 import BeautifulSoup
import json

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

# Проверяем успешность запроса
if response.status_code == 200:
    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все элементы мероприятий
    events = soup.find_all('div', class_='elem')

    # Список для хранения информации о мероприятиях
    events_data = []

    for event in events:
        # Извлекаем название мероприятия
        title_tag = event.find('span', class_='underline')
        title = title_tag.get_text(strip=True) if title_tag else 'Нет названия'

        # Извлекаем описание мероприятия
        description_tag = event.find('div', class_='d')
        description = description_tag.get_text(strip=True) if description_tag else 'Нет описания'

        # Извлекаем даты мероприятия
        sessions = event.find('div', class_='sessions')
        dates = []
        if sessions:
            date_tags = sessions.find_all('span', class_='underline')
            dates = [date.get_text(strip=True) for date in date_tags]

        # Извлекаем ссылку на покупку билета
        ticket_link_tag = event.find('p', class_='b')
        ticket_link = ''
        if ticket_link_tag:
            a_tag = ticket_link_tag.find('a', href=True)
            if a_tag:
                ticket_link = 'https://quicktickets.ru' + a_tag['href']

        # Добавляем информацию о мероприятии в список
        events_data.append({
            'title': title,
            'description': description,
            'dates': dates,
            'ticket_link': ticket_link
        })

    # Сохраняем данные в JSON-файл
    with open('events.json', 'w', encoding='utf-8') as f:
        json.dump(events_data, f, ensure_ascii=False, indent=4)

    print('Данные успешно сохранены в файл events.json')
else:
    print(f'Ошибка при получении страницы: {response.status_code}')

import time

from services import date
from settings import Settings
import urllib.parse

settings = Settings()

def generate_giveaway_text(data: dict) -> str:
    text = f'<b>{data["title"]}</b>'

    if data['description']:
        text += f'\n\n{data["description"]}'

    text += "\n\n<blockquote>" \
                 f"Участников: <b>{len(data['members'])}</b>\n" \
                 f"Призовых мест: <b>{data['win_count']}</b>\n" \
                 f"Дата завершения: <b>{date.date_to_string(data['end_et'])} по МСК</b>\n" \
             "</blockquote>"

    return text


def generate_image_url(data: dict) -> str:
    # TODO: Фиксануть генерацию даты
    difference = data['end_et'] - date.datetime.now()
    end_text = f'{difference.days} д.'
    data = {
        'title': data['title'],
        'end': end_text,
        'wins': data['win_count'],
        'users': len(data['members']),
        'time': str(time.time())
    }
    return f'{settings.server_image}/generate?{urllib.parse.urlencode(data)}'

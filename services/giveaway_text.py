import time
import base64
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
        'time': int(time.time())
    }
    return f'{settings.server_image}/generate?{urllib.parse.urlencode(data)}'

def generate_button_link(username: str, giveaway_id: str, channel_id: int) -> str:
    data = base64.b64encode(f"{giveaway_id}|{channel_id}".encode('utf-8')).decode('utf-8')
    return f'https://t.me/{username}/app?startapp={data}'

from services import date

def generate_giveaway_text(data: dict) -> str:
    text = f'<b>{data["title"]}</b>'

    if data['description']:
        text += f'\n\n{data["description"]}'

    text += "\n\n<blockquote>" \
                 f"Участников: <b>{len(data['members'])}</b>\n" \
                 f"Призовых мест: <b>{data['win_count']}</b>\n" \
                 f"Дата завершения: <b>{date.date_to_string(data['end_et'])}</b>\n" \
             "</blockquote>"

    return text

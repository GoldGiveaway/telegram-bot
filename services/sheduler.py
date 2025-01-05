import traceback

from aiogram import Bot, exceptions
from aiogram.types import InputMediaPhoto
from services import db, giveaway_text, date
from keyboards import for_giveaway_edit
import logging

async def update(bot: Bot):
    bot_me = await bot.get_me()

    for giveaway in await db.get_all_update_giveaways():
        logging.info(f'Update message {giveaway["giveaway_id"]}')
        url_media = giveaway_text.generate_image_url(giveaway)
        for channel in giveaway['channels']:
            try:
                await bot.edit_message_media(
                    chat_id=channel['id'],
                    message_id=channel['message_id'],
                    media=InputMediaPhoto(media=url_media,
                                          caption=giveaway_text.generate_giveaway_text(giveaway)),
                    reply_markup=for_giveaway_edit.giveaway_publish(giveaway_text.generate_button_link(bot_me.username, giveaway['giveaway_id'], channel['id']))
                )
            except exceptions.TelegramBadRequest as e:
                if 'MESSAGE_ID_INVALID' in str(e):
                    try:
                        await bot.send_message(
                            chat_id=giveaway['owner_id'],
                            text=f'<b>⚠️ КРИТИЧЕСКАЯ ОШИБКА:</b> Сообщение с розыгрышем было удалено с канала <b>{channel["name"]}</b>\n\n' \
                                 'Нажмите на кнопку ниже что-бы отправить его снова',
                            reply_markup=for_giveaway_edit.giveaway_channel_send(giveaway['giveaway_id'], channel['id'])
                        )
                    except:
                        pass
            except exceptions.TelegramForbiddenError as e:
                try:
                    await bot.send_message(
                        chat_id=giveaway['owner_id'],
                        text=f'<b>⚠️ КРИТИЧЕСКАЯ ОШИБКА:</b> Бот был удалён с канала <b>{channel["name"]}</b>\n\n' \
                        'Пожалуйста добавьте бота снова как администратора'
                    )
                except: pass
            except:
                logging.error(traceback.format_exc())

        await db.update_giveaway(giveaway['giveaway_id'], {'last_message_update': date.now_datetime()})

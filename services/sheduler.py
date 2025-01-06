import traceback
import random
from aiogram import Bot, exceptions
from aiogram.types import InputMediaPhoto
from interface.giveaway import IGiveaway, IMember
from services import db, giveaway_text, date
from keyboards import for_giveaway_edit
from datetime import datetime, timezone
import logging

async def winner_identification(giveaway: IGiveaway, bot: Bot):
    winners = random.sample(giveaway.members, (len(giveaway.members) - giveaway.win_count) + giveaway.win_count)

    text = '<b>ИТОГИ РОЗЫГРЫША</b>\n'
    for id_, winner in enumerate(winners, start=1):
        user = await db.get_user(winner.id)
        if user.username:
            text += f'\n<b>{id_}.</b> <a href="https://t.me/{user.username}">{user.first_name or ""} {user.last_name or ""}</a> <code>({user.user_id})</code>\n'
        else:
            text += f'\n<b>{id_}.</b> {user.first_name or ""} {user.last_name or ""} <code>({user.user_id})</code>\n'

    await db.update_giveaway(giveaway.giveaway_id, {'status': 'finalized', 'winners': winners})

    for channel in giveaway.channels:
        try:
            await bot.send_message(
                chat_id=channel.id,
                reply_to_message_id=channel.message_id,
                text=text,
            )
        except exceptions.TelegramForbiddenError as e:
            try:
                await bot.send_message(
                    chat_id=giveaway.owner_id,
                    text=f'<b>⚠️ КРИТИЧЕСКАЯ ОШИБКА:</b> Бот был удалён с канала или ему не хватает прав <b>{channel.name}</b>\n\n' \
                         'Пожалуйста добавьте бота снова как администратора'
                )
            except:
                pass
        except:
            logging.error(traceback.format_exc())

async def update(bot: Bot):
    bot_me = await bot.get_me()

    for giveaway in await db.get_all_update_giveaways():
        logging.info(f'Update message {giveaway.giveaway_id}')
        url_media = giveaway_text.generate_image_url(giveaway)
        for channel in giveaway.channels:
            try:
                await bot.edit_message_media(
                    chat_id=channel.id,
                    message_id=channel.message_id,
                    media=InputMediaPhoto(media=url_media,
                                          caption=giveaway_text.generate_giveaway_text(giveaway)),
                    reply_markup=for_giveaway_edit.giveaway_publish(giveaway_text.generate_button_link(bot_me.username, giveaway.giveaway_id, channel.id))
                )
            except exceptions.TelegramBadRequest as e:
                if 'MESSAGE_ID_INVALID' in str(e):
                    try:
                        await bot.send_message(
                            chat_id=giveaway.owner_id,
                            text=f'<b>⚠️ КРИТИЧЕСКАЯ ОШИБКА:</b> Сообщение с розыгрышем было удалено с канала <b>{channel.name}</b>\n\n' \
                                 'Нажмите на кнопку ниже что-бы отправить его снова',
                            reply_markup=for_giveaway_edit.giveaway_channel_send(giveaway.giveaway_id, channel.id)
                        )
                    except:
                        pass
            except exceptions.TelegramForbiddenError as e:
                try:
                    await bot.send_message(
                        chat_id=giveaway.owner_id,
                        text=f'<b>⚠️ КРИТИЧЕСКАЯ ОШИБКА:</b> Бот был удалён с канала или ему не хватает прав <b>{channel.name}</b>\n\n' \
                        'Пожалуйста добавьте бота снова как администратора'
                    )
                except: pass
            except:
                logging.error(traceback.format_exc())

        await db.update_giveaway(giveaway.giveaway_id, {'last_message_update': datetime.now()})
        if datetime.now() > giveaway.end_et:
            await winner_identification(giveaway, bot)

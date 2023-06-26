import psycopg2
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from database import favorite, adverts
from keyboards import inline


class UserFavorites(StatesGroup):
    favorite = State()


async def handle_favorites(call: types.CallbackQuery, state: FSMContext):
    if call.data == "favorites":
        await state.set_state(UserFavorites.favorite.state)
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
        results = await favorite.get_all_favorites(call.from_user.id)
        if results:
            current_index = 0
            result = results[current_index]
            media_group = []
            file_ids = result[4].strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            username = await adverts.get_username_by_advert_id(result[0])
            text = f"<b>Избранное: {current_index + 1} из {len(results)}</b>\n\n" \
                   f"<b>ID объявления:</b> {result[0]}\n" \
                   f"<b>Дата размещения:</b> {result[1].strftime('%d-%m-%Y')}\n" \
                   f"<b>Категория:</b> {result[9]}\n" \
                   f"<b>Населённый пункт:</b> {result[2]}, {result[3]}\n" \
                   f"<b>Описание:</b> {result[5]}"
            if not result[6]:
                text += f'\n\nВещи можно забрать <b>только через самовывоз</b>'
            else:
                text += f'\n\nВещи можно забрать <b>доставкой или через самовывоз</b>'
                if result[7] == "Author":
                    text += f"\n<b>Владелец берёт на себя расходы на доставку</b>"
                elif result[7] == "User":
                    text += f"\n<b>Расходы на доставку берёт на себя получатель</b>"
            media_group = await call.message.answer_media_group(media_group)
            cap = await call.message.answer(text,
                                            reply_markup=inline.favorites_menu(username[0], results, current_index))
            async with state.proxy() as data:
                data['media_group'] = media_group
                data['cap'] = cap
                data['ad_id'] = result[0]
                data['current_index'] = current_index
                data['username'] = username
                data['results'] = results
        else:
            await call.message.answer("У вас нет избранных объявлений!", reply_markup=inline.main_menu())
            await state.finish()


async def handle_pagination(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'favorite_remove':
        async with state.proxy() as data:
            await favorite.remove_from_favorites(int(data.get('ad_id')), call.from_user.id)
            await call.message.edit_reply_markup(reply_markup=inline.favorites_menu_2(
                data.get('username')[0], data.get('results'), len(data.get('results')) - 1))
            await call.answer('Объявление удалено из избранного!')
    elif call.data == 'main_menu_search':
        name = call.from_user.first_name
        async with state.proxy() as data:
            for message in data.get('media_group'):
                await call.bot.delete_message(call.message.chat.id, int(message.message_id))
        async with state.proxy() as data:
            message_id = data.get('cap')
            await call.bot.delete_message(call.message.chat.id, int(message_id.message_id))
        await state.finish()
        await call.message.answer(f"{name}, добро пожаловать в Freebies Bot!", reply_markup=inline.main_menu())
    else:
        async with state.proxy() as data:
            current_index = data.get('current_index')
            print(current_index)
            username = data.get('username')
        try:
            for message in data.get('media_group'):
                try:
                    await call.bot.delete_message(call.message.chat.id, int(message.message_id))
                except MessageToDeleteNotFound:
                    pass
            try:
                message_id = data.get('cap')
                await call.bot.delete_message(call.message.chat.id, int(message_id.message_id))
            except MessageToDeleteNotFound:
                pass
        except TypeError:
            pass
        results = await favorite.get_all_favorites(call.from_user.id)
        if results:
            result = results[current_index]
            if call.data.startswith('prev') or call.data.startswith('next'):
                callback_data = call.data.split(":")
                action = callback_data[0]
                if action == "next":
                    if current_index + 1 < len(results):
                        current_index += 1
                elif action == "prev":
                    if current_index > 0:
                        current_index -= 1
                result = results[current_index]
            media_group = []
            file_ids = result[4].strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            text = f"<b>Избранное: {current_index + 1} из {len(results)}</b>\n\n" \
                   f"<b>ID объявления:</b> {result[0]}\n" \
                   f"<b>Дата размещения:</b> {result[1].strftime('%d-%m-%Y')}\n" \
                   f"<b>Категория:</b> {result[9]}\n" \
                   f"<b>Населённый пункт:</b> {result[2]}, {result[3]}\n" \
                   f"<b>Описание:</b> {result[5]}"
            if not result[6]:
                text += f'\n\nВещи можно забрать <b>только через самовывоз</b>'
            else:
                text += f'\n\nВещи можно забрать <b>доставкой или через самовывоз</b>'
                if result[7] == "Author":
                    text += f"\n<b>Владелец берёт на себя расходы на доставку</b>"
                elif result[7] == "User":
                    text += f"\n<b>Расходы на доставку берёт на себя получатель</b>"
            media_group = await call.message.answer_media_group(media_group)
            cap = await call.message.answer(text,
                                            reply_markup=inline.favorites_menu(username[0], results, current_index))
            async with state.proxy() as data:
                data['current_index'] = current_index
                data['media_group'] = media_group
                data['cap'] = cap
                data['ad_id'] = result[0]
        else:
            await call.message.answer("У вас нет избранных объявлений!", reply_markup=inline.main_menu())
            await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(handle_favorites, text='favorites')
    dp.register_callback_query_handler(handle_pagination, state=UserFavorites.favorite)

import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound, BotBlocked

import handlers.create
from database import users, adverts, review
from keyboards import inline


class UserAdverts(StatesGroup):
    advert = State()
    status = State()
    delete = State()
    agreement = State()


class ReceiverAdverts(StatesGroup):
    advert = State()
    grade = State()
    review = State()


class Review(StatesGroup):
    review = State()
    paginate = State()


class ChangeRegion(StatesGroup):
    region = State()
    moscow = State()
    city = State()
    finish = State()


async def profile_menu(call: types.CallbackQuery):
    user_data = await users.get_user_data(call.from_user.id)
    grade_amount = await users.get_grade_amount(call.from_user.id)
    author_count, author_deals, user_count, user_deals = await adverts.get_amount_agreements(call.from_user.id)
    grade_text = '\(оценок пока что нет\)' if grade_amount == 0 else f'\(количество оценок: {grade_amount}\)'
    user_data = list(user_data)
    user_data[6] = str(user_data[6])
    for i in range(0, 7):
        if isinstance(user_data[i], str):
            special_chars = ['_', '.', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}']
            for char in special_chars:
                user_data[i] = user_data[i].replace(char, '\\' + char)
    user_data = tuple(user_data)
    text = f"**Мой профиль:**\n\n**🆔 Уникальный ID:** _`{user_data[0]}` \(копируется при касании\)_" \
           f"\n**⭐️ Рейтинг:** _{user_data[6]} {grade_text}_"
    if user_data[1]:
        text += f"\n\n**🤖 Username**: _{user_data[1]}_"
    else:
        text += f"\n\n**📞 Контакт**: _{user_data[3]}_"
    if author_deals:
        arguments_author = [str(lst[2]) for lst in author_deals]
        arguments_author_str = 'ID объявлений: ' + ', '.join(arguments_author)
    else:
        arguments_author_str = 'Сделок нет'
    if user_deals:
        arguments_user = [str(lst[2]) for lst in user_deals]
        arguments_user_str = 'ID объявлений: ' + ', '.join(arguments_user)
    else:
        arguments_user_str = 'Сделок нет'
    text += f"\n**😊 Имя**: _{user_data[2]}_" \
            f"\n\n**🤝 Активные сделки:**" \
            f"\n**🤴 Владелец:** _{author_count[0]} \({arguments_author_str}\)_" \
            f"\n**🚚 Получатель:** _{user_count[0]} \({arguments_user_str}\)_" \
            f"\n\n**🌆 Регион**: _{user_data[4]}_" \
            f"\n**🏠 Населенный пункт**: _{user_data[5]}_"
    await call.message.edit_text(text, reply_markup=await inline.profile_menu(call.from_user.id),
                                 parse_mode=types.ParseMode.MARKDOWN_V2)


async def change_region(call: types.CallbackQuery):
    await call.message.edit_text(f"Выберите первую букву своего региона:",
                                 reply_markup=await inline.region_letter_2())
    await ChangeRegion.region.set()


async def handle_change_region_letter(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back_2":
        await state.finish()
        user_data = await users.get_user_data(call.from_user.id)
        grade_amount = await users.get_grade_amount(call.from_user.id)
        author_count, author_deals, user_count, user_deals = await adverts.get_amount_agreements(call.from_user.id)
        grade_text = '\(оценок пока что нет\)' if grade_amount == 0 else f'\(количество оценок: {grade_amount}\)'
        user_data = list(user_data)
        user_data[6] = str(user_data[6])
        for i in range(0, 7):
            if isinstance(user_data[i], str):
                special_chars = ['_', '.', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}']
                for char in special_chars:
                    user_data[i] = user_data[i].replace(char, '\\' + char)
        user_data = tuple(user_data)
        text = f"**Мой профиль:**\n\n**🆔 Уникальный ID:** _`{user_data[0]}` \(копируется при касании\)_" \
               f"\n**⭐️ Рейтинг:** _{user_data[6]} {grade_text}_"
        if user_data[1]:
            text += f"\n\n**🤖 Username**: _{user_data[1]}_"
        else:
            text += f"\n\n**📞 Контакт**: _{user_data[3]}_"
        if author_deals:
            arguments_author = [str(lst[2]) for lst in author_deals]
            arguments_author_str = 'ID объявлений: ' + ', '.join(arguments_author)
        else:
            arguments_author_str = 'Сделок нет'
        if user_deals:
            arguments_user = [str(lst[2]) for lst in user_deals]
            arguments_user_str = 'ID объявлений: ' + ', '.join(arguments_user)
        else:
            arguments_user_str = 'Сделок нет'
        text += f"\n**😊 Имя**: _{user_data[2]}_" \
                f"\n\n**🤝 Активные сделки:**" \
                f"\n**🤴 Владелец:** _{author_count[0]} \({arguments_author_str}\)_" \
                f"\n**🚚 Получатель:** _{user_count[0]} \({arguments_user_str}\)_" \
                f"\n\n**🌆 Регион**: _{user_data[4]}_" \
                f"\n**🏠 Населенный пункт**: _{user_data[5]}_"
        await call.message.edit_text(text, reply_markup=await inline.profile_menu(call.from_user.id),
                                     parse_mode=types.ParseMode.MARKDOWN_V2)
    else:
        letter = call.data
        await call.message.edit_text("Выберите свой регион:",
                                     reply_markup=await inline.region_list(letter))
        await state.set_state(ChangeRegion.city.state)


async def change_city_selection(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await call.message.edit_text(f"Выберите первую букву своего региона:",
                                     reply_markup=await inline.region_letter_2())
        await state.set_state(ChangeRegion.region.state)
    else:
        async with state.proxy() as data:
            data['region'] = call.data
        if call.data == 'Москва и Московская обл.':
            await call.message.edit_text("Выберите диапазон названия вашего населённого пункта",
                                         reply_markup=await inline.moscow_region_name_range())
            await state.set_state(ChangeRegion.moscow.state)
        else:
            await call.message.edit_text("Выберите свой населенный пункт или тот, который находится ближе всего к вам:",
                                         reply_markup=await inline.cities_list(call.data))
            await state.set_state(ChangeRegion.finish.state)


async def change_moscow_city_selection(call: types.CallbackQuery, state: FSMContext):
    ranges = ['А-Г', 'Д-И', 'К-Л', 'М-П', 'Р-Т', 'У-Я']
    if call.data in ranges:
        await call.message.edit_text("Выберите свой населенный пункт или тот, который находится ближе всего к вам:",
                                     reply_markup=await inline.moscow_city_list(call.data))
        await state.set_state(ChangeRegion.finish.state)
    else:
        await state.set_state(ChangeRegion.city.state)
        async with state.proxy() as data:
            letter = data.get('region')[0]
            await call.message.edit_text("Выберите свой регион:",
                                         reply_markup=await inline.region_list(letter))


async def finish_change_region(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == "back":
            if data.get('region') == 'Москва и Московская обл.':
                await state.set_state(ChangeRegion.moscow.state)
                await call.message.edit_text("Выберите диапазон названия вашего населённого пункта",
                                             reply_markup=await inline.moscow_region_name_range())
            else:
                await state.set_state(ChangeRegion.city.state)
                letter = data.get('region')[0]
                await call.message.edit_text("Выберите свой регион:",
                                             reply_markup=await inline.region_list(letter))
        else:
            data['city'] = call.data
            await users.update_region(data.get('region'), data.get('city'), call.from_user.id)
            await call.message.edit_text("Регион успешно обновлён!", reply_markup=inline.main_menu())
            await state.finish()


async def my_adverts(call: types.CallbackQuery):
    await call.message.edit_text("Выберите один из вариантов:", reply_markup=inline.adverts_menu())


async def my_adverts_author(call: types.CallbackQuery, state: FSMContext):
    results = await adverts.get_user_adverts(call.from_user.id)
    if results:
        await call.message.delete()
        current_index = 0
        result = results[current_index]
        media_group = []
        file_ids = result[4].strip().split("\n")
        for file_id in file_ids:
            media = types.InputMediaPhoto(media=file_id)
            media_group.append(media)
        username = await adverts.get_username_by_advert_id(result[0])
        status_keys = {'active': 'Активное объявление', 'agreement': 'Найден получатель',
                       'confirm': 'Вещи переданы'}
        status = ''
        for key, value in status_keys.items():
            if result[10] == key:
                status = value
        if status == 'Найден получатель':
            receiver = await users.get_agreement_users(result[0])
            receiver_username = await users.get_user_data(receiver[2])
            receiver_username = "@" + receiver_username[1] if receiver_username[1] else 'username отсутствует'
            status_text = f"<b>Статус:</b> {status}\n" \
                          f"<b>Получатель:</b> {receiver[2]} ({receiver_username})\n"
        else:
            status_text = f"<b>Статус:</b> {status}\n"
        text = f"<b>Мои объявления: {current_index + 1} из {len(results)}</b>\n\n" \
               f"<b>ID объявления:</b> {result[0]}\n" \
               f'{status_text}' \
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
        async with state.proxy() as data:
            cap = await call.message.answer(
                text, reply_markup=inline.user_adverts(data.get('ad_id'), results, current_index))
        await UserAdverts.advert.set()
        async with state.proxy() as data:
            data['media_group'] = media_group
            data['cap'] = cap
            data['ad_id'] = result[0]
            data['current_index'] = current_index
            data['username'] = username
            data['result'] = result
    else:
        await call.message.edit_text("У вас нет объявлений! Создадим новое?", reply_markup=inline.user_adverts_empty())


async def paginate_my_adverts_author(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('delete_advert_'):
        async with state.proxy() as data:
            await call.message.answer(f'Вы действительно хотите удалить объявление с ID {data.get("ad_id")}?',
                                      reply_markup=inline.yesno())
            await state.set_state(UserAdverts.delete.state)
    elif call.data.startswith('change_status_'):
        async with state.proxy() as data:
            result = data.get('result')
            status_keys = {'active': 'Активное объявление', 'agreement': 'Найден получатель',
                           'confirm': 'Вещи переданы'}
            for key, value in status_keys.items():
                if result[10] == key:
                    status = value
            if result[10] == 'confirm':
                text = "Вы не можете изменить статус, так как вещи уже переданы, " \
                       "вам необходимо создавать новое объявление"
            else:
                text = f'<b>Текущий статус объявления</b> - {status}\n\n<b>Выберите новый статус:</b>'
            status_message = await call.message.answer(text, reply_markup=inline.new_status(result[10]))
            data['status_message'] = status_message
            await state.set_state(UserAdverts.status.state)
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
        results = await adverts.get_user_adverts(call.from_user.id)
        if results:
            current_index = data.get('current_index')
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
            username = await adverts.get_username_by_advert_id(result[0])
            status_keys = {'active': 'Активное объявление', 'agreement': 'Найден получатель',
                           'confirm': 'Вещи переданы'}
            status = ''
            for key, value in status_keys.items():
                if result[10] == key:
                    status = value
            if status == 'Найден получатель':
                receiver = await users.get_agreement_users(result[0])
                receiver_username = await users.get_user_data(receiver[2])
                receiver_username = "@" + receiver_username[1] if receiver_username[1] else 'username отсутствует'
                status_text = f"<b>Статус:</b> {status}\n" \
                              f"<b>Получатель:</b> {receiver[2]} ({receiver_username})\n"
            else:
                status_text = f"<b>Статус:</b> {status}\n"
            text = f"<b>Мои объявления: {current_index + 1} из {len(results)}</b>\n\n" \
                   f"<b>ID объявления:</b> {result[0]}\n" \
                   f'{status_text}' \
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
            cap = await call.message.answer(
                text, reply_markup=inline.user_adverts(data.get('ad_id'), results, current_index))
            await UserAdverts.advert.set()
            async with state.proxy() as data:
                data['media_group'] = media_group
                data['cap'] = cap
                data['ad_id'] = result[0]
                data['current_index'] = current_index
                data['username'] = username
                data['result'] = result


async def my_adverts_receiver(call: types.CallbackQuery, state: FSMContext):
    results = await adverts.get_receiver_adverts(call.from_user.id)
    if results:
        await call.message.delete()
        current_index = 0
        result = results[current_index]
        media_group = []
        file_ids = result[4].strip().split("\n")
        for file_id in file_ids:
            media = types.InputMediaPhoto(media=file_id)
            media_group.append(media)
        username = await adverts.get_username_by_advert_id(result[0])
        user_name = "@" + username[0] if username[0] else "username отсутствует"
        text = f"<b>Объявления, в которых я отмечен как получатель: {current_index + 1} из {len(results)}</b>\n\n" \
               f"<b>ID объявления:</b> {result[0]}\n" \
               f"<b>Автор объявления:</b> {result[8]} ({user_name})\n" \
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
        status = await adverts.get_advert_data(result[0])
        cap = await call.message.answer(
            text, reply_markup=inline.receiver_adverts(username[0], results, current_index, status))
        await ReceiverAdverts.advert.set()
        async with state.proxy() as data:
            data['media_group'] = media_group
            data['cap'] = cap
            data['ad_id'] = result[0]
            data['current_index'] = current_index
            data['username'] = username
            data['result'] = result
    else:
        await call.message.edit_text("У вас нет объявлений, где вы отмечены как получатель!",
                                     reply_markup=await inline.profile_menu(call.from_user.id))


async def paginate_my_adverts_receiver(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("review_author_"):
        async with state.proxy() as data:
            data['author_id'] = call.data.split("_")[2]
        review_existing = await review.get_user_author_review(call.data.split('_')[2], call.from_user.id)
        if review_existing:
            results = await adverts.get_receiver_adverts(call.from_user.id)
            await call.message.edit_reply_markup(
                inline.receiver_adverts_2(data.get('username'), results, data.get('current_index')))
            await call.answer("Вы уже ставили оценку этому автору!", show_alert=True)
        else:
            try:
                async with state.proxy() as data:
                    for message in data.get('media_group'):
                        await call.bot.delete_message(call.message.chat.id, int(message.message_id))
                async with state.proxy() as data:
                    message_id = data.get('cap')
                    await call.bot.delete_message(call.message.chat.id, int(message_id.message_id))
            except MessageToDeleteNotFound:
                pass
            await call.message.answer("Окей, поставьте оценку автору объявления:", reply_markup=inline.author_rating())
            await ReceiverAdverts.next()
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
        results = await adverts.get_receiver_adverts(call.from_user.id)
        if results:
            current_index = data.get('current_index')
            result = results[current_index]
            if call.data.startswith('prev') or call.data.startswith('next'):
                callback_data = call.data.split(":")
                action = callback_data[0]
                if action == "next":
                    if current_index + 1 < len(results):
                        current_index += 1
                elif action == "prev":
                    current_index -= 1 if current_index > 0 else 0
                result = results[current_index]
            media_group = []
            file_ids = result[4].strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            username = await adverts.get_username_by_advert_id(result[0])
            user_name = "@" + username[0] if username[0] else "username отсутствует"
            text = f"<b>Объявления, в которых я отмечен как получатель: {current_index + 1} из {len(results)}</b>\n\n" \
                   f"<b>ID объявления:</b> {result[0]}\n" \
                   f"<b>Автор объявления:</b> {result[8]} ({user_name})\n" \
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
            status = await adverts.get_advert_data(result[0])
            cap = await call.message.answer(
                text, reply_markup=inline.receiver_adverts(username[0], results, current_index, status))
            await ReceiverAdverts.advert.set()
            async with state.proxy() as data:
                data['media_group'] = media_group
                data['cap'] = cap
                data['ad_id'] = result[0]
                data['current_index'] = current_index
                data['username'] = username
                data['result'] = result


async def delete_advert(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        async with state.proxy() as data:
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
        await adverts.delete_advert(data.get('ad_id'))
        await call.message.edit_text("Объявление удалено!", reply_markup=await inline.profile_menu(call.from_user.id))
        await state.finish()
    else:
        message = await call.message.edit_text("Окей, можете продолжать просмотр объявлений")
        await state.set_state(UserAdverts.advert.state)
        await asyncio.sleep(3)
        await call.bot.delete_message(call.message.chat.id, message.message_id)


async def change_status(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        message = await call.message.edit_text("Окей, можете продолжать просмотр объявлений")
        await state.set_state(UserAdverts.advert.state)
        await asyncio.sleep(3)
        await call.bot.delete_message(call.message.chat.id, message.message_id)
    elif call.data == 'create':
        await state.finish()
        await handlers.create.start_creation(call)
    elif call.data == 'agreement':
        await state.set_state(UserAdverts.agreement.state)
        agreement_message = await call.message.edit_text("Попросите у пользователя, с которым вы договорились, "
                                                         "его ID в боте и введите его "
                                                         "\n(Он может посмотреть его в разделе 'Мой профиль'):")
        async with state.proxy() as data:
            data['agreement_message'] = agreement_message
    elif call.data == 'active':
        async with state.proxy() as data:
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
        async with state.proxy() as data:
            await call.message.edit_text(f"Окей, объявление c ID {data.get('ad_id')} "
                                         f"снова доступно для всех пользователей!",
                                         reply_markup=await inline.profile_menu(call.from_user.id))
            await adverts.change_status(data.get('ad_id'), 'active')
            await users.delete_agreement(call.from_user.id, data.get('ad_id'))
            await state.finish()
    else:
        async with state.proxy() as data:
            agreement_users = await users.get_agreement_users(data.get('ad_id'))
            try:
                for message in data.get('media_group'):
                    try:
                        await call.bot.delete_message(call.message.chat.id, int(message.message_id))
                    except MessageToDeleteNotFound:
                        pass
                try:
                    message_id = data.get('cap')
                    message_id_2 = data.get('status_message')
                    await call.bot.delete_message(call.message.chat.id, int(message_id.message_id))
                    await call.bot.delete_message(call.message.chat.id, int(message_id_2.message_id))
                except MessageToDeleteNotFound:
                    pass
            except TypeError:
                pass
        agreement_id, author_id, user_id = agreement_users
        try:
            await call.bot.send_message(int(author_id), "Окей, оцените опыт взаимодействия с получателем:",
                                        reply_markup=inline.rating(agreement_id))
        except BotBlocked:
            print("Бот заблокирован пользователем!")
        await state.finish()


async def handle_agreement_status(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.delete()
        isdigit_message = await msg.answer("Необходимо ввести ID цифрами, попробуйте еще раз!")
        async with state.proxy() as data:
            data['isdigit_message'] = isdigit_message
    else:
        all_users = await users.get_users_list()
        if int(msg.text) not in all_users:
            await msg.delete()
            wrong_user = await msg.answer('Пользователя с данным ID нет в базе, перепроверьте и отправьте еще раз!')
            async with state.proxy() as data:
                data['wrong_user'] = wrong_user
        else:
            async with state.proxy() as data:
                try:
                    for message in data.get('media_group'):
                        try:
                            await msg.bot.delete_message(msg.chat.id, int(message.message_id))
                        except MessageToDeleteNotFound:
                            pass
                    try:
                        message_id = data.get('cap')
                        await msg.bot.delete_message(msg.chat.id, int(message_id.message_id))
                    except MessageToDeleteNotFound:
                        pass
                except TypeError:
                    pass
                await users.new_agreement(msg.from_id, int(msg.text), data.get('ad_id'))
                await adverts.change_status(data.get('ad_id'), 'agreement')
                await msg.delete()
                try:
                    message_id = data.get('agreement_message')
                    message_id_2 = data.get('isdigit_message')
                    message_id_3 = data.get('wrong_user')
                    await msg.bot.delete_message(msg.chat.id, int(message_id.message_id))
                    await msg.bot.delete_message(msg.chat.id, int(message_id_2.message_id))
                    await msg.bot.delete_message(msg.chat.id, int(message_id_3.message_id))
                except MessageToDeleteNotFound:
                    pass
                except AttributeError:
                    pass
                try:
                    await msg.bot.send_message(
                        int(msg.text), f"Вас отметили как получателя в объявлении с ID {data.get('ad_id')}! "
                                       f"Вы можете посмотреть его в разделе "
                                       f"'Мой профиль' -> 'Мои объявления' -> 'Получатель'")
                except BotBlocked:
                    print("Пользователь заблокировал бота!")
                await msg.answer(f"Статус объявления c ID {data.get('ad_id')} изменён!",
                                 reply_markup=await inline.profile_menu(msg.from_user.id))
                await state.finish()


async def handle_rating(call: types.CallbackQuery, state: FSMContext):
    if call.data.split("_")[1] == 'cancel':
        await call.message.edit_text("Отмена!")
    else:
        agreement_id = call.data.split("_")[1]
        rating = call.data.split("_")[2]
        agreement_data = await users.get_agreement_data(int(agreement_id))
        advert_id, author_id, user_id = agreement_data
        if call.from_user.id == author_id:
            mess = await call.message.edit_text(
                f"Вы поставили оценку {rating} для получателя.\n\nТеперь напишите небольшой "
                f"отзыв, не более 500 символов:")
            await Review.review.set()
            await state.update_data(
                {"user_id": user_id, "advert_id": advert_id, "message": mess.message_id, "rating": rating})


async def handle_review(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        explicit_words = await adverts.get_explicit_words()
        found_words = []
        for word in explicit_words:
            if word in msg.text.lower():
                found_words.append(word)
        if found_words:
            await msg.delete()
            await msg.answer(f"Найдены запрещенные слова: {', '.join(found_words)}"
                             f"\n\nПопробуйте заново, избегая запрещённых слов")
        else:
            data['author_id'] = msg.from_id
            data['review'] = msg.text
            await msg.bot.delete_message(msg.chat.id, int(data.get('message')))
            await review.new_review(data.get('author_id'), data.get('user_id'), msg.text)
            await msg.delete()
            await adverts.change_status(data.get('advert_id'), 'confirm')
            await users.update_user_rating(data.get('user_id'), data.get('rating'))
            advert_author = await adverts.get_advert_data(data.get('advert_id'))
            if advert_author[8] == msg.from_id:
                await msg.answer(f"Статус объявления с ID {data.get('advert_id')} успешно изменён!"
                                 f"\n\nОтзыв для получателя сохранён!", reply_markup=inline.main_menu())
                await msg.bot.send_message(
                    data.get('user_id'), f"Автор объявления с ID {data.get('advert_id')} поставил вам "
                                         f"оценку и написал отзыв!\nЕсли хотите, вы также можете поставить оценку "
                                         f"владельцу объявления и написать о нём отзыв, это можно сделать в разделе "
                                         f"'Мои объявления'",
                    reply_markup=await inline.profile_menu(data.get('user_id')))
            await state.finish()


async def get_reviews(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'main_menu_search':
        await state.finish()
        await profile_menu(call)
    else:
        results = await review.get_user_review(call.from_user.id)
        if results:
            current_index = 0
            result = results[current_index]
            author_name = await users.get_user_data(result[1])
            text = f'<b>Отзыв {current_index + 1} из {len(results)}:</b>' \
                   f'\n<b>ID автора отзыва:</b> {result[1]}\n<b>Полное имя:</b> {author_name[2]}' \
                   f'\n\n<b>Текст отзыва:</b>\n<em>{result[0]}</em>'
            await call.message.edit_text(text, reply_markup=inline.review_pagination(results, current_index))
            await Review.paginate.set()
            async with state.proxy() as data:
                data['current_index'] = current_index
        else:
            await call.message.edit_text("На данный момент никто не оставлял на вас отзыв!",
                                         reply_markup=inline.main_menu())


async def handle_review_pagination(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'main_menu_search':
        await state.finish()
        await profile_menu(call)
    else:
        results = await review.get_user_review(call.from_user.id)
        if results:
            async with state.proxy() as data:
                current_index = data.get('current_index')
            result = results[current_index]
            author_name = await users.get_user_data(result[1])
            if call.data.startswith('prev') or call.data.startswith('next'):
                callback_data = call.data.split(":")
                current_index = int(callback_data[1])
                action = callback_data[0]
                if action == "next":
                    if current_index + 1 < len(results):
                        current_index += 1
                elif action == "prev":
                    if current_index > 0:
                        current_index -= 1
                result = results[current_index]
                text = f'<b>Отзыв {current_index + 1} из {len(results)}:</b>' \
                       f'\n<b>ID автора отзыва:</b> {result[1]}\n<b>Полное имя:</b> {author_name[2]}' \
                       f'\n\n<b>Текст отзыва:</b>\n<em>{result[0]}</em>'
                await call.message.edit_text(text, reply_markup=inline.review_pagination(results, current_index))
                async with state.proxy() as data:
                    data['current_index'] = current_index
            elif call.data == 'main_menu_review':
                name = call.from_user.first_name
                await state.finish()
                await call.message.edit_text(f"{name}, добро пожаловать в Freebies Bot!",
                                             reply_markup=inline.main_menu())


async def new_username(call: types.CallbackQuery):
    if call.from_user.username:
        await users.update_username(call.from_user.username, call.from_user.id)
        await call.answer('Ваш username обновлён!')
        await call.message.edit_reply_markup(await inline.profile_menu(call.from_user.id))
    else:
        await call.answer('Для корректной работы этой функции вам необходимо создать username!', show_alert=True)


async def review_to_author(call: types.CallbackQuery, state: FSMContext):
    if call.data.split("_")[1] == 'cancel':
        await call.message.edit_text("Отмена!")
    else:
        async with state.proxy() as data:
            data['rating'] = call.data.split("_")[1]
            mess = await call.message.edit_text(
                f"Вы поставили оценку {call.data.split('_')[1]} для автора.\n\nТеперь напишите небольшой "
                f"отзыв, не более 500 символов:")
            data['message'] = mess.message_id
        await ReceiverAdverts.next()


async def handle_author_review(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        explicit_words = await adverts.get_explicit_words()
        found_words = []
        for word in explicit_words:
            if word in msg.text.lower():
                found_words.append(word)
        if found_words:
            await msg.delete()
            await msg.answer(f"Найдены запрещенные слова: {', '.join(found_words)}"
                             f"\n\nПопробуйте заново, избегая запрещённых слов")
        else:
            data['user_id'] = msg.from_id
            data['review'] = msg.text
            advert_author = await adverts.get_advert_data(data.get('ad_id'))
            await msg.bot.delete_message(msg.chat.id, int(data.get('message')))
            await review.new_review(data.get('user_id'), advert_author[8], msg.text)
            await msg.delete()
            await users.update_user_rating(advert_author[8], data.get('rating'))
            advert_author = await adverts.get_advert_data(data.get('ad_id'))
            await msg.answer("Оценка и отзыв успешно отправлены!",
                             reply_markup=await inline.profile_menu(data.get('user_id')))
            await msg.bot.send_message(
                advert_author[8], f"Объявление {data.get('ad_id')}:\nПолучатель поставил вам оценку "
                                  f"{data.get('rating')} и оставил отзыв! "
                                  f"\nЕго можно посмотреть в разделе 'Полученные отзывы'!")
            await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(profile_menu, text='profile')
    dp.register_callback_query_handler(change_region, text='change_region')
    dp.register_callback_query_handler(handle_change_region_letter, state=ChangeRegion.region)
    dp.register_callback_query_handler(change_moscow_city_selection, state=ChangeRegion.moscow)
    dp.register_callback_query_handler(change_city_selection, state=ChangeRegion.city)
    dp.register_callback_query_handler(finish_change_region, state=ChangeRegion.finish)
    dp.register_callback_query_handler(my_adverts, text='my_adverts')
    dp.register_callback_query_handler(my_adverts_author, text='my_adverts_author')
    dp.register_callback_query_handler(paginate_my_adverts_author, state=UserAdverts.advert)
    dp.register_callback_query_handler(my_adverts_receiver, text='my_adverts_receiver')
    dp.register_callback_query_handler(paginate_my_adverts_receiver, state=ReceiverAdverts.advert)
    dp.register_callback_query_handler(delete_advert, state=UserAdverts.delete)
    dp.register_callback_query_handler(change_status, state=UserAdverts.status)
    dp.register_message_handler(handle_agreement_status, state=UserAdverts.agreement)
    dp.register_callback_query_handler(handle_rating, lambda c: c.data.startswith('rating_'))
    dp.register_message_handler(handle_review, state=Review.review)
    dp.register_callback_query_handler(get_reviews, text='reviews')
    dp.register_callback_query_handler(handle_review_pagination, state=Review.paginate)
    dp.register_callback_query_handler(new_username, text='username')
    dp.register_callback_query_handler(review_to_author, state=ReceiverAdverts.grade)
    dp.register_message_handler(handle_author_review, state=ReceiverAdverts.review)

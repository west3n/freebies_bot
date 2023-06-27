import asyncio

import decouple
import psycopg2
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from database import users, adverts, favorite
from keyboards import inline


class AdvertSearch(StatesGroup):
    category = State()
    format = State()
    region = State()
    letter = State()
    city = State()
    confirm = State()
    complaint = State()


async def select_category(call: types.CallbackQuery):
    await call.message.edit_text("Выберите категорию, в которой хотите найти объявление:",
                                 reply_markup=await inline.get_category_search_list())
    await AdvertSearch.category.set()


async def search_format(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'all_categories':
        async with state.proxy() as data:
            data['category'] = "Все категории"
        await call.message.edit_text(f"Вы выбрали поиск <b>по всем категориям</b>"
                                     f"\n\nВыберите один из вариантов:", reply_markup=inline.search_all_exact())
        await AdvertSearch.next()
    else:
        if call.data == 'return_format':
            async with state.proxy() as data:
                await call.message.edit_text(f"Вы выбрали категорию <b>'{data.get('category')}'</b>"
                                             f"\n\nВыберите один из вариантов:", reply_markup=inline.search_all_exact())
        else:
            async with state.proxy() as data:
                data['category'] = call.data
            await call.message.edit_text(f"Вы выбрали категорию <b>'{data.get('category')}'</b>"
                                         f"\n\nВыберите один из вариантов:", reply_markup=inline.search_all_exact())
            await AdvertSearch.next()


async def handle_format(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'return_category':
        await state.finish()
        await select_category(call)
    elif call.data == 'search_all':
        city = await users.get_user_data(call.from_user.id)
        async with state.proxy() as data:
            data['format'] = "Любые слова"
        await call.message.edit_text("Вы выбрали поиск <b>по всем словам</b>.\n\n"
                                     "Теперь необходимо выбрать регион:", reply_markup=inline.search_region(city[5]))
        await state.set_state(AdvertSearch.region.state)
    elif call.data == 'search_exact':
        message_3 = await call.message.edit_text("Введите слово (или несколько слов через запятую, но не больше 3-х), "
                                                 "которые должны быть в тексте объявления:")
        async with state.proxy() as data:
            data['message_3'] = message_3


async def exact_words(msg: types.Message, state: FSMContext):
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
        city = await users.get_user_data(msg.from_user.id)
        if "," in msg.text:
            words = msg.text.split(',')
            if len(words) <= 3:
                async with state.proxy() as data:
                    data['format'] = words
                    message_3 = data.get('message_3')
                await msg.delete()
                await msg.bot.delete_message(msg.chat.id, message_3.message_id)
                await msg.answer(f"Вы выбрали поиск по этим словам: '{msg.text}'.\n\n"
                                 "Теперь необходимо выбрать регион:", reply_markup=inline.search_region(city[5]))
                await state.set_state(AdvertSearch.region.state)
            else:
                await msg.delete()
                await msg.answer("Слов должно быть не больше 3-х! Попробуйте заново")
        else:
            if len(msg.text.split()) == 1:
                async with state.proxy() as data:
                    data['format'] = msg.text
                    message_3 = data.get('message_3')
                await msg.delete()
                await msg.bot.delete_message(msg.chat.id, message_3.message_id)
                await msg.answer(f"Вы выбрали поиск по слову '{msg.text}'.\n\n"
                                 "Теперь необходимо выбрать регион:", reply_markup=inline.search_region(city[5]))
                await state.set_state(AdvertSearch.region.state)
            else:
                await msg.delete()
                await msg.answer("Слова должны быть написаны через запятую! Попробуйте заново")


async def handle_region(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'return_format':
        await state.set_state(AdvertSearch.format.state)
        await search_format(call, state)
    elif call.data == 'all_cities':
        async with state.proxy() as data:
            data['region'] = 'Россия'
            category = data.get('category')
            text_format = data.get('format')
            if type(text_format) == list:
                text_format = ",".join(text_format)
        await call.message.edit_text(f"Подтвердите данные поиска:\n\n<b>Категория</b> - {category}"
                                     f"\n<b>Слова в поиске:</b> {text_format}"
                                     f"\n<b>Регион поиска:</b> {data.get('region')}",
                                     reply_markup=inline.confirm_searching())
        await state.set_state(AdvertSearch.confirm.state)
    elif call.data == 'other_city':
        await call.message.edit_text("Выберите первую букву региона поиска:", reply_markup=await inline.region_letter())
        await state.set_state(AdvertSearch.letter.state)
    elif call.data == 'back':
        await state.set_state(AdvertSearch.city.state)
        async with state.proxy() as data:
            region = data.get('region_search')
        letter = region[0]
        await call.message.edit_text("Выберите регион поиска:",
                                     reply_markup=await inline.region_list(letter))
    else:
        async with state.proxy() as data:
            data['region'] = call.data
            category = data.get('category')
            text_format = data.get('format')
            if type(text_format) == list:
                text_format = ",".join(text_format)
        await call.message.edit_text(f"Подтвердите данные поиска:\n\n<b>Категория</b> - {category}"
                                     f"\n<b>Слова в поиске:</b> {text_format}"
                                     f"\n<b>Регион поиска:</b> {data.get('region')}",
                                     reply_markup=inline.confirm_searching())
        await state.set_state(AdvertSearch.confirm.state)


async def handle_region_letter(call: types.CallbackQuery):
    letter = call.data
    await call.message.edit_text("Выберите регион поиска:",
                                 reply_markup=await inline.region_list(letter))
    await AdvertSearch.next()


async def search_city_selection(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await call.message.edit_text(f"Выберите первую букву своего региона:",
                                     reply_markup=await inline.region_letter())
        await state.set_state(AdvertSearch.letter.state)
    else:
        async with state.proxy() as data:
            data['region_search'] = call.data
        await call.message.edit_text("Выберите населенный пункт, в котором хотите произвести поиск:",
                                     reply_markup=await inline.cities_list(call.data))
        await state.set_state(AdvertSearch.region.state)


async def start_searching(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'favorite_advert':
        async with state.proxy() as data:
            try:
                await favorite.add_to_favorite(int(data.get('ad_id')), call.from_user.id)
            except psycopg2.Error:
                await call.answer('Это объявление уже было добавлено в избранное!')
            await call.message.edit_reply_markup(reply_markup=inline.advert_menu_favorite(
                data.get('username'), data.get('results'), data.get('current_index')))
            await call.answer('Объявление добавлено в избранное!')
    elif call.data == 'complain_advert':
        async with state.proxy() as data:
            complaint_message = await call.message.reply(
                f"Вы хотите пожаловаться на объявление с ID {data.get('ad_id')}.\n\n"
                f"Опишите причину жалобы (не больше 500 символов)")
            data['complaint_message'] = complaint_message
            await AdvertSearch.complaint.set()
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
    elif call.data == 'return_region':
        city = await users.get_user_data(call.from_user.id)
        await state.set_state(AdvertSearch.region.state)
        async with state.proxy() as data:
            text_format = data.get('format')
        if text_format == "Любые слова":
            text = "Вы выбрали поиск по всем словам"
            await call.message.edit_text(f"{text}\n\nТеперь необходимо выбрать регион:",
                                         reply_markup=inline.search_region(city[5]))
        if type(text_format) == list:
            text = f"Вы выбрали поиск по этим словам: '{','.join(text_format)}'"
        else:
            text = f"Вы выбрали поиск по слову '{text_format}'"
        await call.message.edit_text(f"{text}\n\nТеперь необходимо выбрать регион:",
                                     reply_markup=inline.search_region(city[5]))
    else:
        try:
            await call.message.delete()
        except MessageToDeleteNotFound:
            pass
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
            results = await adverts.search_adverts(call.from_user.id, data.get('region'),
                                                   data.get('format'), data.get('category'))
        if results:
            current_index = 0
            result = results[current_index]
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
            media_group = []
            file_ids = result[4].strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            username = await adverts.get_username_by_advert_id(result[0])
            text = f"<b>Объявление {current_index + 1} из {len(results)}:</b>\n\n" \
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
            cap = await call.message.answer(text, reply_markup=inline.advert_menu(username[0], results, current_index))
            async with state.proxy() as data:
                data['media_group'] = media_group
                data['cap'] = cap
                data['ad_id'] = result[0]
                data['current_index'] = current_index
                data['results'] = results
                data['username'] = username
        else:
            await call.message.answer("Поиск не дал результатов, попробуйте снова!",
                                      reply_markup=inline.main_menu())
            await state.finish()


async def handle_complaint(msg: types.Message, state: FSMContext):
    if len(msg.text) > 500:
        await msg.delete()
        await msg.answer("Длина текста жалобы не должна превышать 500 символов. Попробуйте еще раз!")
    explicit_words = await adverts.get_explicit_words()
    found_words = []
    for word in explicit_words:
        if word in msg.text.lower():
            found_words.append(word)
    if found_words:
        await msg.delete()
        message_2 = await msg.answer(f"Найдены запрещенные слова: {', '.join(found_words)}"
                                     f"\n\nПопробуйте заново, избегая запрещённых слов")
        async with state.proxy() as data:
            data['explicit'] = message_2
    else:
        async with state.proxy() as data:
            data['complaint'] = msg.text
        try:
            message_id = data.get('complaint_message')
            explicit_message = data.get('explicit')
            await msg.bot.delete_message(msg.chat.id, int(message_id.message_id))
            await msg.bot.delete_message(msg.chat.id, int(explicit_message.message_id))
        except MessageToDeleteNotFound:
            pass
        except AttributeError:
            pass
        await msg.delete()
        async with state.proxy() as data:
            result = await adverts.get_advert_data(data.get('ad_id'))
            media_group = []
            file_ids = result[4].strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            username = await adverts.get_username_by_advert_id(result[0])
            username_text = f"\nПрофиль автора в Телеграм: @{username[0]}" if username[0] else ''
            text = f'Пользователь c ID {msg.from_user.id} ({msg.from_user.full_name}) пожаловался на объявление:' \
                   f'\n<b>Текст жалобы:</b> <em>{msg.text}</em>' \
                   f"\n\n<b>ID объявления:</b> {result[0]}\n" \
                   f"{username_text}" \
                   f"\n<b>Дата размещения:</b> {result[1].strftime('%d-%m-%Y')}" \
                   f"\n<b>Категория:</b> {result[9]}" \
                   f"\n<b>Населённый пункт:</b> {result[2]}, {result[3]}" \
                   f"\n<b>Описание:</b> {result[5]}" \
                   f"\n\nВыберите дальнейшее действие:"
        await msg.bot.send_media_group(int(decouple.config("ADMIN_ID")), media_group)
        await msg.bot.send_message(int(decouple.config("ADMIN_ID")), text,
                                   reply_markup=inline.admin_complaint(data.get('ad_id')))
        message_2 = await msg.answer(
            "Ваша жалоба отправлена администратору."
            "\nЕсли жалоба будет одобрена, вам придёт сообщение от бота."
            "\nВы можете вернуться к просмотру объявлений, это сообщение исчезнет через 10 секунд")
        if msg.from_id == int(decouple.config('ADMIN_ID')):
            await state.finish()
        else:
            await state.set_state(AdvertSearch.confirm.state)
        await asyncio.sleep(10)
        await msg.bot.delete_message(msg.chat.id, int(message_2.message_id))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(select_category, text='find')
    dp.register_callback_query_handler(search_format, state=AdvertSearch.category)
    dp.register_callback_query_handler(handle_format, state=AdvertSearch.format)
    dp.register_message_handler(exact_words, state=AdvertSearch.format)
    dp.register_callback_query_handler(handle_region, state=AdvertSearch.region)
    dp.register_callback_query_handler(handle_region_letter, state=AdvertSearch.letter)
    dp.register_callback_query_handler(search_city_selection, state=AdvertSearch.city)
    dp.register_callback_query_handler(start_searching, state=AdvertSearch.confirm)
    dp.register_message_handler(handle_complaint, state=AdvertSearch.complaint)

import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

import handlers.create
from database import users, adverts, review
from keyboards import inline
from handlers.registration import Registration


class UserAdverts(StatesGroup):
    advert = State()
    status = State()
    delete = State()
    agreement = State()


class Review(StatesGroup):
    review = State()


async def profile_menu(call: types.CallbackQuery):
    user_data = await users.get_user_data(call.from_user.id)
    text = f"<b>Мой профиль:</b>\n\n<b>Уникальный ID</b> - <em>{user_data[0]}</em>" \
           f"\n<b>Рейтинг</b> - {user_data[6]}"
    if user_data[3] == "Нет контакта":
        text += f"\n<b>Username</b> - <em>{user_data[1]}</em>"
    else:
        text += f"\n<b>Номер телефона</b> - <em>{user_data[3]}</em>"
    text += f"\n<b>Имя</b> - <em>{user_data[2]}</em>" \
            f"\n<b>Регион</b> - <em>{user_data[4]}</em>" \
            f"\n<b>Населенный пункт</b> - <em>{user_data[5]}</em>"
    await call.message.edit_text(text, reply_markup=inline.profile_menu())


async def change_region(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Registration.region.state)
    await call.message.edit_text(f"Выберите первую букву своего региона:",
                                 reply_markup=await inline.region_letter())


async def my_adverts(call: types.CallbackQuery, state: FSMContext):
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
        text = f"<b>Мои объявления: {current_index + 1} из {len(results)}</b>\n\n" \
               f"<b>ID объявления:</b> {result[0]}\n" \
               f"<b>Статус:</b> {status}\n" \
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


async def paginate_my_adverts(call: types.CallbackQuery, state: FSMContext):
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
            text = f"<b>Мои объявления: {current_index + 1} из {len(results)}</b>\n\n" \
                   f"<b>ID объявления:</b> {result[0]}\n" \
                   f"<b>Статус:</b> {status}\n" \
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
        await call.message.edit_text("Объявление удалено!", reply_markup=inline.profile_menu())
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
                                                         "его ID в боте и введите его:")
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
                                         reply_markup=inline.profile_menu())
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
        await call.bot.send_message(int(author_id), "Окей, оцените опыт взаимодействия с получателем:",
                                    reply_markup=inline.rating(agreement_id))
        await call.bot.send_message(
            int(user_id), f"Владелец объявления отметил объявление с ID {data.get('ad_id')} как завершённое! "
                          "Оцените опыт взаимодействия с владельцем объявления:",
            reply_markup=inline.rating(agreement_id))
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
                await msg.answer(f"Статус объявления c ID {data.get('ad_id')} изменён!",
                                 reply_markup=inline.profile_menu())
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
            await state.update_data({"user_id": user_id, "advert_id": advert_id, "message": mess.message_id})
        if call.from_user.id == user_id:
            mess = await call.message.edit_text(
                f"Вы поставили оценку {rating} для владельца объявления с ID {advert_id}."
                f"\n\nТеперь напишите небольшой отзыв, не более 500 символов:")
            await Review.review.set()
            await state.update_data({"user_id": author_id, "advert_id": advert_id, "message": mess.message_id})


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
            await adverts.change_status(data.get('advert_id'), 'confirm')
            advert_author = await adverts.get_advert_data(data.get('advert_id'))
            if advert_author[8] == msg.from_id:
                await msg.answer(f"Статус объявления с ID {data.get('advert_id')} успешно изменён!"
                                 f"\n\nОтзыв для получателя сохранён!", reply_markup=inline.main_menu())
            else:
                await msg.answer("Отзыв для автора объявления успешно сохранён!", reply_markup=inline.main_menu())
            await state.finish()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(profile_menu, text='profile')
    dp.register_callback_query_handler(change_region, text='change_region')
    dp.register_callback_query_handler(my_adverts, text='my_adverts')
    dp.register_callback_query_handler(paginate_my_adverts, state=UserAdverts.advert)
    dp.register_callback_query_handler(delete_advert, state=UserAdverts.delete)
    dp.register_callback_query_handler(change_status, state=UserAdverts.status)
    dp.register_message_handler(handle_agreement_status, state=UserAdverts.agreement)
    dp.register_callback_query_handler(handle_rating, lambda c: c.data.startswith('rating_'))
    dp.register_message_handler(handle_review, state=Review.review)

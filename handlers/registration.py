import asyncio
import decouple
import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound
from keyboards import inline, reply
from database import users


class Registration(StatesGroup):
    contact = State()
    region = State()
    city = State()
    finish = State()


# def is_link(text):
#     pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
#     return re.search(pattern, text) is not None
#
#
# def is_email(text):
#     pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
#     return re.search(pattern, text) is not None


async def see_manual(call: types.CallbackQuery):
    video = decouple.config('MANUAL')
    await call.message.delete()
    await call.message.answer_video(video, caption="Как создать username в Телеграме?",
                                    reply_markup=inline.manual())


async def add_username(call: types.CallbackQuery):
    if not call.from_user.username:
        await call.answer("Вы не добавили username, попробуйте еще раз!", show_alert=True)
    else:
        await call.message.delete()
        await call.message.answer(f"Отлично! Теперь выберите первую букву своего региона:",
                                  reply_markup=await inline.region_letter_1())
        await Registration.region.set()


async def input_contact(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Окей, вы можете оставить свой номер телефона, нажав на кнопку ниже:",
                              reply_markup=reply.contact())
    # message = await call.message.answer(
    #     'Окей, вы можете оставить свой номер телефона, нажав на кнопку ниже или оставить другой контакт для связи, '
    #     '(ссылку на другие соц.сети, электронную почту или другой номер телефона)\nПримеры правильных форматов:\n'
    #     '- Для ссылки: https://example.com\n- Для адреса электронной почты: example@example.com\n'
    #     '-Для номера телефона +79993210783, букв быть не должно', reply_markup=reply.contact())
    await Registration.contact.set()
    # async with state.proxy() as data:
    #     data['message'] = message


async def handle_user_contact(msg: types.Message, state: FSMContext):
    if msg.contact:
        await msg.delete()
        async with state.proxy() as data:
            data['contact'] = msg.contact.phone_number
        await msg.answer(f"Отлично! Теперь выберите первую букву своего региона:",
                         reply_markup=await inline.region_letter_1())
        await Registration.next()
    # elif msg.text:
    #     if msg.text.isdigit():
    #         async with state.proxy() as data:
    #             data['contact'] = msg.text
    #             delete_message = data.get('message')
    #             delete_message_2 = data.get('message_2')
    #         try:
    #             await msg.bot.delete_message(msg.chat.id, delete_message.message_id)
    #             await msg.bot.delete_message(msg.chat.id, delete_message_2.message_id)
    #         except MessageToDeleteNotFound:
    #             pass
    #         except AttributeError:
    #             pass
    #         await msg.delete()
    #         message = await msg.answer('Загружаю регионы...', reply_markup=reply.kb_remove)
    #         await msg.bot.send_chat_action(msg.chat.id, 'typing')
    #         await asyncio.sleep(2)
    #         await msg.bot.delete_message(msg.chat.id, message.message_id)
    #         await msg.answer(f"Отлично! Теперь выберите первую букву своего региона:",
    #                          reply_markup=await inline.region_letter())
    #         await msg.edit_reply_markup(reply_markup=reply.kb_remove)
    #     elif msg.text.startswith("+"):
    #         number = msg.text.split("+")[1]
    #         if number.isdigit():
    #             async with state.proxy() as data:
    #                 data['contact'] = msg.text
    #                 delete_message = data.get('message')
    #                 delete_message_2 = data.get('message_2')
    #             try:
    #                 await msg.bot.delete_message(msg.chat.id, delete_message.message_id)
    #                 await msg.bot.delete_message(msg.chat.id, delete_message_2.message_id)
    #             except MessageToDeleteNotFound:
    #                 pass
    #             except AttributeError:
    #                 pass
    #             await msg.delete()
    #             message = await msg.answer('Загружаю регионы...', reply_markup=reply.kb_remove)
    #             await msg.bot.send_chat_action(msg.chat.id, 'typing')
    #             await asyncio.sleep(2)
    #             await msg.bot.delete_message(msg.chat.id, message.message_id)
    #             await msg.answer(f"Отлично! Теперь выберите первую букву своего региона:",
    #                              reply_markup=await inline.region_letter())
    #         else:
    #             await msg.answer("Вы ввели неверный формат. Пожалуйста, введите правильный формат.\n\n"
    #                              "Примеры правильного формата:\n"
    #                              "+79993210783, букв быть не должно", reply_markup=reply.kb_remove)
    #     elif is_link(msg.text):
    #         async with state.proxy() as data:
    #             data['contact'] = msg.text
    #             delete_message = data.get('message')
    #             delete_message_2 = data.get('message_2')
    #         try:
    #             await msg.bot.delete_message(msg.chat.id, delete_message.message_id)
    #             await msg.bot.delete_message(msg.chat.id, delete_message_2.message_id)
    #         except MessageToDeleteNotFound:
    #             pass
    #         except AttributeError:
    #             pass
    #         await msg.delete()
    #         message = await msg.answer('Загружаю регионы...', reply_markup=reply.kb_remove)
    #         await msg.bot.send_chat_action(msg.chat.id, 'typing')
    #         await asyncio.sleep(2)
    #         await msg.bot.delete_message(msg.chat.id, message.message_id)
    #         await msg.answer(f"Отлично! Теперь выберите первую букву своего региона:",
    #                          reply_markup=await inline.region_letter())
    #         await Registration.next()
    #     elif is_email(msg.text):
    #         async with state.proxy() as data:
    #             data['contact'] = msg.text
    #             delete_message = data.get('message')
    #             delete_message_2 = data.get('message_2')
    #         try:
    #             await msg.bot.delete_message(msg.chat.id, delete_message.message_id)
    #             await msg.bot.delete_message(msg.chat.id, delete_message_2.message_id)
    #         except MessageToDeleteNotFound:
    #             pass
    #         except AttributeError:
    #             pass
    #         await msg.delete()
    #         message = await msg.answer('Загружаю регионы...', reply_markup=reply.kb_remove)
    #         await msg.bot.send_chat_action(msg.chat.id, 'typing')
    #         await asyncio.sleep(2)
    #         await msg.bot.delete_message(msg.chat.id, message.message_id)
    #         await msg.answer(f"Отлично! Теперь выберите первую букву своего региона:",
    #                          reply_markup=await inline.region_letter())
    #         await Registration.next()
    #     else:
    #         await msg.delete()
    #         message_2 = await msg.answer("Вы ввели неверный формат. Пожалуйста, введите правильный формат.\n\n"
    #                                      "Примеры правильных форматов:\n"
    #                                      "- Для ссылки: https://example.com\n"
    #                                      "- Для адреса электронной почты: example@example.com",
    #                                      reply_markup=reply.kb_remove)
    #         async with state.proxy() as data:
    #             data['message_2'] = message_2


async def handle_region_letter(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back_2":
        await state.set_state(Registration.region.state)
        user_data = await users.get_user_data(call.from_user.id)
        grade_amount = await users.get_grade_amount(call.from_user.id)
        grade_text = '(оценок пока что нет)' if grade_amount == 0 else f'(количество оценок: {grade_amount})'
        text = f"<b>Мой профиль:</b>\n\n<b>🆔 Уникальный ID:</b> <em>{user_data[0]}</em>" \
               f"\n<b>⭐️ Рейтинг:</b> {user_data[6]} {grade_text}"
        if user_data[3] == "Нет контакта":
            text += f"\n\n<b>🤖 Username</b>: <em>{user_data[1]}</em>"
        else:
            text += f"\n\n<b>📞 Контакт</b>: <em>{user_data[3]}</em>"
        text += f"\n<b>😊 Имя</b>: <em>{user_data[2]}</em>" \
                f"\n\n<b>🌆 Регион</b>: <em>{user_data[4]}</em>" \
                f"\n<b>🏠 Населенный пункт</b>: <em>{user_data[5]}</em>"
        await state.finish()
        await call.message.edit_text(text, reply_markup=inline.profile_menu())
    else:
        letter = call.data
        await call.message.edit_text("Выберите свой регион:",
                                     reply_markup=await inline.region_list(letter))
        await Registration.next()


async def city_selection(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.set_state(Registration.region.state)
        await call.message.edit_text(f"Выберите первую букву своего региона:",
                                     reply_markup=await inline.region_letter_1())
    else:
        async with state.proxy() as data:
            data['region'] = call.data
        await call.message.edit_text("Выберите свой населенный пункт или тот, который находится ближе всего к вам:",
                                     reply_markup=await inline.cities_list(call.data))
        await Registration.next()


async def finish_registration(call: types.CallbackQuery, state: FSMContext):
    user_exist = await users.get_user_data(call.from_user.id)
    async with state.proxy() as data:
        if call.data == "back":
            await state.set_state(Registration.city.state)
            region = data.get('region')
            letter = region[0]
            await call.message.edit_text("Выберите свой регион:",
                                         reply_markup=await inline.region_list(letter))
        else:
            data['city'] = call.data
            if user_exist:
                await users.update_region(data.get('region'), data.get('city'), call.from_user.id)
                await call.message.edit_text("Регион успешно обновлён!", reply_markup=inline.main_menu())
                await state.finish()
            else:
                await users.add_new_user(call.from_user.id, call.from_user.username, call.from_user.full_name,
                                         data.get('contact'), data.get('region'), data.get('city'))
                await call.message.edit_text("Регистрация пройдена успешно!", reply_markup=inline.main_menu())
                await state.finish()


def register(dp: Dispatcher):
    # dp.register_callback_query_handler(see_manual, text='see_manual')
    # dp.register_callback_query_handler(add_username, text='add_username')
    dp.register_callback_query_handler(input_contact, text='input_contact')
    dp.register_message_handler(handle_user_contact, content_types=['text', 'contact'], state=Registration.contact)
    dp.register_callback_query_handler(handle_region_letter, state=Registration.region)
    dp.register_callback_query_handler(city_selection, state=Registration.city)
    dp.register_callback_query_handler(finish_registration, state=Registration.finish)

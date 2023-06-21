
import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import users
from keyboards import inline, reply
from handlers.registration import Registration
from aiogram.utils.exceptions import MessageIdentifierNotSpecified, BadRequest


class Subscription(StatesGroup):
    sub = State()


async def bot_start(msg: types.Message, state: FSMContext):
    message_id = await msg.answer("Загружаю главное меню...")
    await msg.bot.send_chat_action(msg.chat.id, 'typing')
    try:
        name = msg.from_user.first_name
        member = await msg.bot.get_chat_member(decouple.config("GROUP_ID"), msg.from_id)
        if member.status == 'left':
            await msg.bot.delete_message(msg.chat.id, message_id.message_id)
            link = await msg.bot.create_chat_invite_link(decouple.config("GROUP_ID"))
            mess = await msg.answer("Для продолжения работы с ботом вам необходимо подписаться на группу, "
                                    "затем снова нажать на /start",
                                    reply_markup=inline.link_to_group(link.invite_link))
            await Subscription.sub.set()
            await state.update_data({"sub": mess.message_id})
        else:
            if msg.from_user.id in await users.get_blocked_users_list():
                reason = await users.get_block_reason(msg.from_id)
                await msg.bot.delete_message(msg.chat.id, message_id.message_id)
                await msg.answer(f"Вы заблокированы в Freebies Боте.\nПричина - '{reason[0]}'"
                                 f"\nЕсли вас заблокировали по ошибке, можете написать администратору, указав свой ID"
                                 f"- {msg.from_id}",
                                 reply_markup=inline.link_to_admin())
            async with state.proxy() as data:
                try:
                    await msg.bot.delete_message(chat_id=msg.from_id, message_id=data.get('sub'))
                    await state.finish()
                except MessageIdentifierNotSpecified:
                    await state.finish()
            if msg.from_user.id not in await users.get_users_list():
                if not msg.from_user.username:
                    await msg.bot.delete_message(msg.chat.id, message_id.message_id)
                    await msg.answer(f"{name}, добро пожаловать в Freebies Bot! Давайте начнём регистрацию!"
                                     f"\nНажмите 'Отправить контакт'", reply_markup=reply.contact())
                    await Registration.contact.set()
                else:
                    await msg.bot.delete_message(msg.chat.id, message_id.message_id)
                    await msg.answer(f"{name}, добро пожаловать в Freebies Bot! Давайте начнём регистрацию!"
                                     f"\nВыберите первую букву своего региона:",
                                     reply_markup=await inline.region_letter())
                    await Registration.region.set()
            else:
                if msg.from_user.id not in await users.get_blocked_users_list():
                    await msg.bot.delete_message(msg.chat.id, message_id.message_id)
                    await msg.answer(f"{name}, добро пожаловать в Freebies Bot!", reply_markup=inline.main_menu())
    except BadRequest:
        pass


async def call_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    name = call.from_user.first_name
    await call.message.edit_text(f"{name}, добро пожаловать в Freebies Bot!", reply_markup=inline.main_menu())


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
    dp.register_callback_query_handler(call_main_menu, text='main_menu')

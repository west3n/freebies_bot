from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import users
from keyboards import inline, reply
from handlers.registration import Registration


async def bot_start(msg: types.Message, state: FSMContext):
    await state.finish()
    name = msg.from_user.first_name
    if msg.from_user.id not in await users.get_users_list():
        if not msg.from_user.username:
            await msg.answer(f"{name}, добро пожаловать в Freebies Bot! Давайте начнём регистрацию!"
                             f"\nНажмите 'Отправить контакт'", reply_markup=reply.contact())
            await Registration.contact.set()
        else:
            await msg.answer(f"{name}, добро пожаловать в Freebies Bot! Давайте начнём регистрацию!"
                             f"\nВыберите первую букву своего региона:",
                             reply_markup=await inline.region_letter())
            await Registration.region.set()
    else:
        await msg.answer(f"{name}, добро пожаловать в Freebies Bot!", reply_markup=inline.main_menu())


async def call_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    name = call.from_user.first_name
    await call.message.edit_text(f"{name}, добро пожаловать в Freebies Bot!", reply_markup=inline.main_menu())


def register(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands='start', state='*')
    dp.register_callback_query_handler(call_main_menu, text='main_menu')

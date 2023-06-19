from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from database import users
from keyboards import inline
from handlers.registration import Registration


async def profile_menu(call: types.CallbackQuery):
    user_data = await users.get_user_data(call.from_user.id)
    text = f"<b>Мой профиль:</b>\n\n<b>Уникальный ID</b> - <em>{user_data[0]}</em>"
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


def register(dp: Dispatcher):
    dp.register_callback_query_handler(profile_menu, text='profile')
    dp.register_callback_query_handler(change_region, text='change_region')

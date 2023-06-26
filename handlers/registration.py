from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import inline
from database import users


class Registration(StatesGroup):
    contact = State()
    region = State()
    city = State()
    finish = State()


async def handle_user_contact(msg: types.Message, state: FSMContext):
    if msg.contact:
        async with state.proxy() as data:
            data['contact'] = msg.contact.phone_number
        await msg.answer(f"Отлично! Теперь выберите первую букву своего региона:",
                         reply_markup=await inline.region_letter())
        await Registration.next()


async def handle_region_letter(call: types.CallbackQuery):
    letter = call.data
    await call.message.edit_text("Выберите свой регион:",
                                 reply_markup=await inline.region_list(letter))
    await Registration.next()


async def city_selection(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await state.set_state(Registration.region.state)
        await call.message.edit_text(f"Выберите первую букву своего региона:",
                                     reply_markup=await inline.region_letter())
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
    dp.register_message_handler(handle_user_contact, content_types='contact', state=Registration.contact)
    dp.register_callback_query_handler(handle_region_letter, state=Registration.region)
    dp.register_callback_query_handler(city_selection, state=Registration.city)
    dp.register_callback_query_handler(finish_registration, state=Registration.finish)

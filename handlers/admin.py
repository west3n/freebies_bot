from aiogram import Dispatcher, types
from database import adverts, users
from keyboards import inline


async def pass_complaint(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Окей, босс, хорошего дня!")


async def admin_delete_advert(call: types.CallbackQuery):
    ad_id = call.data.split("_")[2]
    await call.answer("Удаление объявления выполнено!", cache_time=8)
    await adverts.delete_advert(ad_id)
    await call.message.edit_reply_markup(reply_markup=inline.admin_complaint_no_block_no_delete(ad_id))


async def admin_block_user(call: types.CallbackQuery):
    ad_id = call.data.split("_")[2]
    author_id = await adverts.get_advert_data(ad_id)
    await users.block_user(author_id[8], f'На ваше объявление с ID {ad_id} '
                                         f'поступила жалоба, которая была одобрена администратором')
    await adverts.delete_advert(ad_id)
    await call.answer("Пользователь заблокирован и объявление удалено! "
                      "Разблокировать пользователя можно а админ-панели", cache_time=8)
    await call.message.edit_reply_markup(reply_markup=inline.admin_complaint_no_block_no_delete(ad_id))


def register(dp: Dispatcher):
    dp.register_callback_query_handler(pass_complaint, lambda c: c.data.startswith('pass'), state="*")
    dp.register_callback_query_handler(admin_delete_advert, lambda c: c.data.startswith('delete_advert_'), state="*")
    dp.register_callback_query_handler(admin_block_user, lambda c: c.data.startswith('block_user_'), state="*")

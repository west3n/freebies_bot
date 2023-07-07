import decouple
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import users
from keyboards import inline
from handlers.registration import Registration
from aiogram.utils.exceptions import MessageIdentifierNotSpecified, BadRequest


class Subscription(StatesGroup):
    sub = State()


async def file_id(msg: types.Message):
    if str(msg.from_id) in ['254465569', '15362825']:
        if msg.video:
            await msg.reply(msg.video.file_id)


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
                    await msg.answer(
                        f"{name}, добро пожаловать в Freebies Bot! Давайте начнём регистрацию!"
                        f"\nУ вас нет username, выберите один из вариантов (настоятельно рекомендуем вам "
                        f"зарегистрировать username, во избежания попадания вашего номера телефона в "
                        f"руки мошенников):",
                        reply_markup=inline.no_username())
                else:
                    await msg.bot.delete_message(msg.chat.id, message_id.message_id)
                    await msg.answer(f"{name}, добро пожаловать в Freebies Bot! Давайте начнём регистрацию!"
                                     f"\nВыберите первую букву своего региона:",
                                     reply_markup=await inline.region_letter_1())
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


async def information(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Бот предназначен для передачи или приема в дар различных предметов или домашних животных. "
                     "Все объявления, имеющие коммерческую или любую другую тематику, не связанную с "
                     "данной платформой, будут заблокированы администраторами или автоматически."
                     "\n\nПосле создания профиля вы сможете искать и создавать объявления. Если вас заинтересовало "
                     "определенное объявление, вы можете нажать на кнопку «связаться с владельцем» и перейти в личный "
                     "чат для общения с ним. Обратите внимание, что эта функция находится вне бота, поэтому важно "
                     "указать ваше имя и причину обращения."
                     "\n\nПосле завершения всех деталей сделки, создатель объявления может изменить его статус на "
                     "«Найден получатель» в разделе «Мои объявления». Это автоматически снимет объявление с "
                     "публикации.\n\nВ конце сделки создатель объявления должен ввести «Уникальный ID» "
                     "получателя, который тот может посмотреть в разделе «Мой профиль» и сообщить его дарителю, "
                     "что свяжет их аккаунты и даст возможность взаимодействия.")


async def faq(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Раздел 'FAQ' находится в разработке!")


def register(dp: Dispatcher):
    dp.register_message_handler(file_id, content_types=['video'])
    dp.register_message_handler(bot_start, commands='start', state='*')
    dp.register_message_handler(information, commands='information', state='*')
    dp.register_message_handler(faq, commands='faq', state='*')
    dp.register_callback_query_handler(call_main_menu, text='main_menu', state="*")

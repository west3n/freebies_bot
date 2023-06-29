import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageToDeleteNotFound

from keyboards import inline
from handlers.commands import call_main_menu
from database import adverts, users


class Creation(StatesGroup):
    category = State()
    caption = State()
    media_amount = State()
    media = State()
    readiness = State()
    payer = State()
    confirm = State()
    changes = State()
    category_changes = State()
    caption_changes = State()
    media_changes = State()
    delivery_changes = State()
    finish = State()


async def start_creation(call: types.CallbackQuery):
    advert_amount = await adverts.get_amount_by_date_and_user(datetime.datetime.now().date(), call.from_user.id)
    if int(advert_amount[0]) >= 2:
        await call.message.edit_text("В день можно разместить не больше 2-х объявлений! Попробуйте завтра!",
                                     reply_markup=inline.profile_menu())
    else:
        await call.message.edit_text("Выберите категорию объявления:", reply_markup=await inline.get_category_list())
        await Creation.category.set()


async def handle_category(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == 'main_menu':
            await state.finish()
            await call_main_menu(call, state)
        else:
            data['category'] = call.data
            message_1 = await call.message.edit_text(f"<b>Вы выбрали категорию</b> <em>'{call.data}'</em>."
                                                     f"\n\nВведите текст вашего объявления "
                                                     f"и отправьте его в бота, БЕЗ ФОТОГРАФИЙ, "
                                                     f"они будут в следующем шаге:")
            data['message_1'] = message_1.message_id
            await Creation.next()


async def handle_caption(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        explicit_words = await adverts.get_explicit_words()
        found_words = []
        for word in explicit_words:
            if word in msg.text.lower():
                found_words.append(word)
        if found_words:
            await msg.delete()
            await msg.bot.delete_message(msg.chat.id, int(data.get('message_1')))
            await msg.answer(f"Найдены запрещенные слова: {', '.join(found_words)}"
                             f"\n\nПопробуйте заново, избегая запрещённых слов")
        else:
            data['caption'] = msg.text
            await msg.delete()
            try:
                await msg.bot.delete_message(msg.chat.id, int(data.get('message_1')))
            except MessageToDeleteNotFound:
                pass
            message_2 = await msg.answer(f"<b>Категория</b> - <em>'{data.get('category')}'</em>"
                                         f"\n\n<b>Описание</b> - <em>'{msg.text}'</em>"
                                         f"\n\nТеперь необходимо выбрать количество фотографий, "
                                         f"которые вы хотите прикрепить к объявлению",
                                         reply_markup=inline.media_amount())
            data['message_2'] = message_2.message_id
            await Creation.next()


async def handle_media_amount(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['media_amount'] = call.data
    await call.message.edit_text(f"\n\nТеперь прикрепите фотографии."
                                 f"\nВажно! Фотографии нужно отправить <b>ОДНИМ СООБЩЕНИЕМ "
                                 f"(НЕ В ВИДЕ ДОКУМЕНТОВ)</b>."
                                 f"\nФотографий должно быть ровно {data.get('media_amount')}.")
    await Creation.next()


async def handle_media(msg: types.Message, state: FSMContext):
    if msg.photo:
        async with state.proxy() as data:
            if 'media_id' and 'media_count' not in data:
                data['media_id'] = ''
                data['media_count'] = 0
            data['media_id'] = data.get('media_id') + f'\n{msg.photo[-1].file_id}'
            data['media_count'] += 1
            if data.get('media_count') == int(data.get('media_amount')):
                await msg.answer("Фотографии загружены. Теперь укажите готовность отправить "
                                 "вещи по почте или через службу доставки:",
                                 reply_markup=inline.delivery_readiness())


async def handle_readiness(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await call.bot.delete_message(call.message.chat.id, int(data.get('message_2')))
        if call.data == "ready":
            data['readiness'] = True
            await state.set_state(Creation.payer.state)
            await call.message.edit_text("Теперь определите, кто будет оплачивать доставку:",
                                         reply_markup=inline.delivery_payer())
            await Creation.next()
        else:
            media_group = []
            file_ids = data.get('media_id').strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            await state.set_state(Creation.confirm.state)
            data['readiness'] = False
            await call.message.delete()
            messages = await call.bot.send_media_group(call.message.chat.id, media_group)
            data['group_message_id'] = messages
            await call.message.answer(
                f"Проверьте корректность объявления:"
                f"\n\n<b>Категория</b> - <em>'{data.get('category')}'</em>"
                f"\n<b>Описание</b> - <em>'{data.get('caption')}'</em>"
                f"\n<b>Вещи можно забрать только самовывозом</b>"
                f"\nФотографии, которые будут прикреплены к объявлению, <b>отправлены сообщением выше.</b>"
                f"\n\nМожем размещать объявление?", reply_markup=inline.advert_confirmation())
            await Creation.next()


async def handle_payer(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == "payer_author":
            data['payer'] = "Author"
            text = '\nДоставка будет оплачена <b>за счёт владельца</b>'
        else:
            data['payer'] = "User"
            text = '\nДоставка будет оплачена <b>за счёт получателя</b>'
        media_group = []
        file_ids = data.get('media_id').strip().split("\n")
        for file_id in file_ids:
            media = types.InputMediaPhoto(media=file_id)
            media_group.append(media)
        await call.message.delete()
        messages = await call.bot.send_media_group(call.message.chat.id, media_group)
        data['group_message_id'] = messages
        await call.message.answer(
            f"Проверьте корректность объявления:"
            f"\n\n<b>Категория</b> - <em>'{data.get('category')}'</em>"
            f"\n<b>Описание</b> - <em>'{data.get('caption')}'</em>"
            f"\n<b>Вещи можно забрать самовывозом или доставкой</b>"
            f"{text}"
            f"\n\nФотографии, которые будут прикреплены к объявлению, <b>отправлены сообщением выше.</b>"
            f"\n\nМожем размещать объявление?", reply_markup=inline.advert_confirmation())
        await Creation.next()


async def finish_creation(call: types.CallbackQuery, state: FSMContext):
    if call.data == "confirm_advert":
        async with state.proxy() as data:
            await state.set_state(Creation.finish.state)
            user_data = await users.get_user_data(call.from_user.id)
            advert_id = await adverts.save_new_advert(datetime.datetime.now().date(), call.from_user.id, user_data[4],
                                                      user_data[5], data.get('category'), data.get('media_id'),
                                                      data.get('caption'), data.get('readiness'), data.get('payer'))
            await call.message.edit_text('Объявление сохранено! Вы можете его посмотреть в своём профиле в разделе '
                                         f'<b>"Мои объявления"</b>. Его ID - <em>{advert_id[0]}</em>.',
                                         reply_markup=inline.main_menu())
            for message in data.get('group_message_id'):
                try:
                    await call.bot.delete_message(call.message.chat.id, int(message.message_id))
                except MessageToDeleteNotFound:
                    pass
            await state.finish()
    elif call.data == 'change_advert':
        async with state.proxy() as data:
            await state.set_state(Creation.finish.state)
            await call.message.edit_text("Выберите параметр, который хотели бы изменить:",
                                         reply_markup=inline.advert_changing())
            for message in data.get('group_message_id'):
                try:
                    await call.bot.delete_message(call.message.chat.id, int(message.message_id))
                except MessageToDeleteNotFound:
                    pass
            await state.set_state(Creation.payer.state)


async def handle_changing(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == 'change_category':
            await call.message.edit_text(f"<b>Текущая категория:</b> <em>{data.get('category')}</em>"
                                         f"\n\nВыберите новую категорию объявления:",
                                         reply_markup=await inline.update_category_list())
            await state.set_state(Creation.category_changes.state)
        elif call.data == 'change_caption':
            await call.message.edit_text(f"*Текущий текст объявления:* `{data.get('caption')}`"
                                         f"\n\nВведите *новый текст* объявления:",
                                         parse_mode=types.ParseMode.MARKDOWN_V2)
            await state.set_state(Creation.caption_changes.state)
        elif call.data == "change_media":
            media_group = []
            file_ids = data.get('media_id').strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            await call.message.delete()
            await call.bot.send_media_group(call.message.chat.id, media_group)
            await call.message.answer(f"Выше представлены текущие фотографии, вам необходимо отправить "
                                      f"новые фотографии.\nВажно! Фотографии нужно отправить <b>ОДНИМ СООБЩЕНИЕМ "
                                      f"(НЕ В ВИДЕ ДОКУМЕНТОВ)</b>."
                                      f"\nФотографий должно быть ровно {data.get('media_amount')}.")
            await state.set_state(Creation.media_changes.state)
            data['media_id'] = ''
            data['media_count'] = 0
        elif call.data == 'change_delivery':
            if data.get('readiness'):
                text = 'На данный момент вы готовы отправить вещи доставкой. ' \
                       '\n\nВыберите вариант, который вам подходит:'
            else:
                text = 'На данный момент вы <b>НЕ</b> готовы отправить вещи доставкой. ' \
                       '\n\nВыберите вариант, который вам подходит'
            await call.message.edit_text(text, reply_markup=inline.delivery_readiness())
            await state.set_state(Creation.delivery_changes.state)


async def handle_category_changes(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if not data['readiness']:
            text = f"\n<b>Вещи можно забрать только самовывозом</b>"
            text_2 = ''
        else:
            text = f"\n<b>Вещи можно забрать самовывозом или доставкой</b>"
            if data['payer'] == "Author":
                text_2 = '\nДоставка будет оплачена <b>за счёт владельца</b>'
            elif data['payer'] == "User":
                text_2 = '\nДоставка будет оплачена <b>за счёт получателя</b>'
        data['category'] = call.data
        media_group = []
        file_ids = data.get('media_id').strip().split("\n")
        for file_id in file_ids:
            media = types.InputMediaPhoto(media=file_id)
            media_group.append(media)
        messages = await call.bot.send_media_group(call.message.chat.id, media_group)
        data['group_message_id'] = messages
        await call.message.delete()
        await call.message.answer(
            f"Обновили категорию! Проверьте корректность объявления:"
            f"\n\n<b>Категория</b> - <em>'{data.get('category')}'</em>"
            f"\n<b>Описание</b> - <em>'{data.get('caption')}'</em>"
            f'{text}{text_2}'
            f"\nФотографии, которые будут прикреплены к объявлению, <b>отправлены сообщением выше.</b>"
            f"\n\nМожем размещать объявление?", reply_markup=inline.advert_confirmation())
        await state.set_state(Creation.changes.state)


async def handle_caption_changes(msg: types.Message, state: FSMContext):
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
            if not data['readiness']:
                text = f"\n<b>Вещи можно забрать только самовывозом</b>"
                text_2 = ''
            else:
                text = f"\n<b>Вещи можно забрать самовывозом или доставкой</b>"
                if data['payer'] == "Author":
                    text_2 = '\nДоставка будет оплачена <b>за счёт владельца</b>'
                elif data['payer'] == "User":
                    text_2 = '\nДоставка будет оплачена <b>за счёт получателя</b>'
            data['caption'] = msg.text
            media_group = []
            file_ids = data.get('media_id').strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            messages = await msg.bot.send_media_group(msg.chat.id, media_group)
            data['group_message_id'] = messages
            await msg.delete()
            await msg.answer(
                f"Обновили категорию! Проверьте корректность объявления:"
                f"\n\n<b>Категория</b> - <em>'{data.get('category')}'</em>"
                f"\n<b>Описание</b> - <em>'{data.get('caption')}'</em>"
                f'{text}{text_2}'
                f"\nФотографии, которые будут прикреплены к объявлению, <b>отправлены сообщением выше.</b>"
                f"\n\nМожем размещать объявление?", reply_markup=inline.advert_confirmation())
            await state.set_state(Creation.changes.state)


async def handle_media_changes(msg: types.Message, state: FSMContext):
    if msg.photo:
        async with state.proxy() as data:
            if not data['readiness']:
                text = f"\n<b>Вещи можно забрать только самовывозом</b>"
                text_2 = ''
            else:
                text = f"\n<b>Вещи можно забрать самовывозом или доставкой</b>"
                if data['payer'] == "Author":
                    text_2 = '\nДоставка будет оплачена <b>за счёт владельца</b>'
                elif data['payer'] == "User":
                    text_2 = '\nДоставка будет оплачена <b>за счёт получателя</b>'
            if data.get('media_id') == '' and data.get('media_count') == 0:
                data['media_id'] = data.get('media_id') + f'\n{msg.photo[-1].file_id}'
                data['media_count'] += 1
            else:
                data['media_id'] = data.get('media_id') + f'\n{msg.photo[-1].file_id}'
                data['media_count'] += 1
            if data.get('media_count') == int(data.get('media_amount')):
                media_group = []
                file_ids = data.get('media_id').strip().split("\n")
                for file_id in file_ids:
                    media = types.InputMediaPhoto(media=file_id)
                    media_group.append(media)
                messages = await msg.bot.send_media_group(msg.chat.id, media_group)
                data['group_message_id'] = messages
                await msg.answer(
                    f"Обновили фотографии! Проверьте корректность объявления:"
                    f"\n\n<b>Категория</b> - <em>'{data.get('category')}'</em>"
                    f"\n<b>Описание</b> - <em>'{data.get('caption')}'</em>"
                    f'{text}{text_2}'
                    f"\nФотографии, которые будут прикреплены к объявлению, <b>отправлены сообщением выше.</b>"
                    f"\n\nМожем размещать объявление?", reply_markup=inline.advert_confirmation())
                await state.set_state(Creation.changes.state)


async def handle_delivery_changes(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data == "ready":
            data['readiness'] = True
            await state.set_state(Creation.payer.state)
            await call.message.edit_text("Теперь определите, кто будет оплачивать доставку:",
                                         reply_markup=inline.delivery_payer())
            await state.set_state(Creation.confirm.state)
        else:
            media_group = []
            file_ids = data.get('media_id').strip().split("\n")
            for file_id in file_ids:
                media = types.InputMediaPhoto(media=file_id)
                media_group.append(media)
            await state.set_state(Creation.confirm.state)
            data['readiness'] = False
            await call.message.delete()
            await call.bot.send_media_group(call.message.chat.id, media_group)
            await call.message.answer(
                f"Проверьте корректность объявления:"
                f"\n\n<b>Категория</b> - <em>'{data.get('category')}'</em>"
                f"\n<b>Описание</b> - <em>'{data.get('caption')}'</em>"
                f"\n<b>Вещи можно забрать только самовывозом</b>"
                f"\nФотографии, которые будут прикреплены к объявлению, <b>отправлены сообщением выше.</b>"
                f"\n\nМожем размещать объявление?", reply_markup=inline.advert_confirmation())
            await Creation.next()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(start_creation, text='create')
    dp.register_callback_query_handler(handle_category, state=Creation.category)
    dp.register_message_handler(handle_caption, state=Creation.caption)
    dp.register_callback_query_handler(handle_media_amount, state=Creation.media_amount)
    dp.register_message_handler(handle_media, content_types=['photo'], state=Creation.media)
    dp.register_callback_query_handler(handle_readiness, state=Creation.media)
    dp.register_callback_query_handler(handle_payer, state=Creation.confirm)
    dp.register_callback_query_handler(finish_creation, state=Creation.changes)
    dp.register_callback_query_handler(handle_changing, state=Creation.payer)
    dp.register_callback_query_handler(handle_category_changes, state=Creation.category_changes)
    dp.register_message_handler(handle_caption_changes, state=Creation.caption_changes)
    dp.register_message_handler(handle_media_changes, content_types=['photo'], state=Creation.media_changes)
    dp.register_callback_query_handler(handle_delivery_changes, state=Creation.delivery_changes)

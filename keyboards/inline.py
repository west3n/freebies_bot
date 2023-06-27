from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import region, adverts


async def region_letter() -> InlineKeyboardMarkup:
    buttons = []
    for letter in await region.get_first_letters():
        buttons.append(InlineKeyboardButton(text=letter, callback_data=letter))
    kb = InlineKeyboardMarkup(row_width=7)
    kb.add(*buttons)
    return kb


async def region_list(letter) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for region_name in await region.get_regions_by_first_letter(letter):
        button = InlineKeyboardButton(text=region_name, callback_data=region_name)
        kb.add(button)
    button = InlineKeyboardButton(text="↩️ Назад", callback_data="back")
    kb.add(button)
    return kb


async def cities_list(region_name) -> InlineKeyboardMarkup:
    buttons = []
    for city in await region.get_cities_by_region(region_name):
        buttons.append(InlineKeyboardButton(text=city, callback_data=city))
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*buttons)
    button = InlineKeyboardButton(text="↩️ Назад", callback_data="back")
    kb.add(button)
    return kb


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🔍 Найти объявления', callback_data='find')],
        [InlineKeyboardButton('📝 Создать объявление', callback_data='create')],
        [InlineKeyboardButton('🪪 Мой профиль', callback_data='profile')]
    ])
    return kb


def profile_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📃 Мои объявления', callback_data='my_adverts'),
         InlineKeyboardButton('⭐ Избранное', callback_data='favorites')],
        [InlineKeyboardButton('🔀 Изменить регион проживания', callback_data='change_region')],
        [InlineKeyboardButton('↩️ Вернуться в главное меню', callback_data='main_menu')]
    ])
    return kb


def link_to_group(link) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('✅ Подписаться на группу', url=link)]
    ])
    return kb


def link_to_admin() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('✍️ Написать админу', url='https://t.me/maximumot')]
    ])
    return kb


async def get_category_list() -> InlineKeyboardMarkup:
    buttons = []
    for category in await adverts.get_category_list():
        buttons.append(InlineKeyboardButton(text=category, callback_data=category))
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*buttons)
    button = InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="main_menu")
    kb.add(button)
    return kb


async def get_category_search_list() -> InlineKeyboardMarkup:
    buttons = []
    for category in await adverts.get_category_list():
        buttons.append(InlineKeyboardButton(text=category, callback_data=category))
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*buttons)
    button = InlineKeyboardButton(text="🧸 Поиск по всем категориям", callback_data="all_categories")
    kb.add(button)
    button = InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="main_menu")
    kb.add(button)
    return kb


async def update_category_list() -> InlineKeyboardMarkup:
    buttons = []
    for category in await adverts.get_category_list():
        buttons.append(InlineKeyboardButton(text=category, callback_data=category))
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*buttons)
    return kb


def delivery_readiness() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('✅ Самовывоз или служба доставки', callback_data='ready')],
        [InlineKeyboardButton('❌ Только самовывоз', callback_data='not_ready')]
    ])
    return kb


def delivery_payer() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📦 Я хочу оплатить доставку', callback_data='payer_author')],
        [InlineKeyboardButton('🚚 Я хочу, чтобы доставку оплатил получатель', callback_data='payer_user')]
    ])
    return kb


def advert_confirmation() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('✅ Да, можете размещать', callback_data='confirm_advert')],
        [InlineKeyboardButton('❌ Нет, я хочу внести правки', callback_data='change_advert')]
    ])
    return kb


def advert_changing() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📂 Категория', callback_data='change_category'),
         InlineKeyboardButton('📃 Описание', callback_data='change_caption')],
        [InlineKeyboardButton('📷 Фотографии', callback_data='change_media'),
         InlineKeyboardButton('🚚 Доставка', callback_data='change_delivery')]
    ])
    return kb


def media_amount() -> InlineKeyboardMarkup:
    buttons = []
    for x in range(1, 11):
        buttons.append(InlineKeyboardButton(text=str(x), callback_data=str(x)))
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(*buttons)
    return kb


def search_all_exact() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🔍 Поиск по любым словам', callback_data='search_all')],
        [InlineKeyboardButton('📃 Поиск по конкретным словам', callback_data='search_exact')],
        [InlineKeyboardButton('↩️ Вернуться к выбору категории', callback_data='return_category')]
    ])
    return kb


def search_region(city) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'🏠 {city}', callback_data=city)],
        [InlineKeyboardButton('🔀 Выбрать другой населённый пункт', callback_data='other_city')],
        [InlineKeyboardButton('🇷🇺 Поиск по всей России', callback_data='all_cities')],
        [InlineKeyboardButton('↩️ Вернуться к выбору формата', callback_data='return_format')]
    ])
    return kb


def confirm_searching() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🔍 Начать поиск', callback_data='start_searching')],
        [InlineKeyboardButton('↩️ Вернуться к выбору региона', callback_data='return_region')],

    ])
    return kb


def advert_menu(username, results, current_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if username:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', url=f'https://t.me/{username}'))
    else:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', callback_data='contact_advert'))
    markup.add(InlineKeyboardButton('⭐️ Добавить в избранное', callback_data='favorite_advert')),
    markup.add(InlineKeyboardButton('⛔ Пожаловаться на содержание', callback_data='complain_advert'))
    if current_index == 0:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{len(results)}"),
            InlineKeyboardButton('🔽️ Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    elif current_index == len(results) - 1:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:-1")
        )
    else:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    markup.add()
    return markup


def advert_menu_favorite(username, results, current_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if username:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', url=f'https://t.me/{username}'))
    else:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', callback_data='contact_advert'))
    markup.add(InlineKeyboardButton('⛔ Пожаловаться на содержание', callback_data='complain_advert'))
    if current_index == 0:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{len(results)}"),
            InlineKeyboardButton('🔽️ Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    elif current_index == len(results) - 1:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:-1")
        )
    else:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    markup.add()
    return markup


def favorites_menu(username, results, current_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if username:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', url=f'https://t.me/{username}'))
    else:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', callback_data='contact_advert'))
    markup.add(InlineKeyboardButton('❌ Убрать из избранного', callback_data='favorite_remove')),
    if current_index == 0:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{len(results)}"),
            InlineKeyboardButton('🔽️ Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    elif current_index == len(results) - 1:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:-1")
        )
    else:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    markup.add()
    return markup


def favorites_menu_2(username, results, current_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if username:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', url=f'https://t.me/{username}'))
    else:
        markup.add(InlineKeyboardButton(f'📞 Связаться с владельцем', callback_data='contact_advert'))
    if current_index == 0:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{len(results)}"),
            InlineKeyboardButton('🔽️ Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    elif current_index == len(results) - 1:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:-1")
        )
    else:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    markup.add()
    return markup


def admin_complaint(ad_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🚮 Удалить объявление', callback_data=f'delete_advert_{ad_id}')],
        [InlineKeyboardButton('⛔ Заблокировать владельца и удалить объявление', callback_data=f'block_user_{ad_id}')],
        [InlineKeyboardButton('🤷 Ничего не делать', callback_data=f'pass_{ad_id}')]
    ])
    return kb


def admin_complaint_no_delete(ad_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('⛔ Заблокировать владельца', callback_data=f'block_user_{ad_id}')],
        [InlineKeyboardButton('🤷 Больше ничего не делать', callback_data=f'pass_{ad_id}')]
    ])
    return kb


def admin_complaint_no_block(ad_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🚮 Удалить объявление', callback_data=f'delete_advert_{ad_id}')],
        [InlineKeyboardButton('🤷 Больше ничего не делать', callback_data=f'pass_{ad_id}')]
    ])
    return kb


def admin_complaint_no_block_no_delete(ad_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🤷 Больше ничего не делать', callback_data=f'pass_{ad_id}')]
    ])
    return kb


def user_adverts_empty() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📝 Создать объявление', callback_data='create')],
        [InlineKeyboardButton('↩️ Вернуться в главное меню', callback_data='main_menu')]
    ])
    return kb


def user_adverts(ad_id, results, current_index) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton('🚮 Удалить объявление', callback_data=f'delete_advert_{ad_id}'))
    markup.row(InlineKeyboardButton('🔀 Изменить статус', callback_data=f'change_status_{ad_id}'))
    if current_index == 0:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{len(results)}"),
            InlineKeyboardButton('🔽️ Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    elif current_index == len(results) - 1:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:-1")
        )
    else:
        markup.row(
            InlineKeyboardButton("◀️ Назад", callback_data=f"prev:{current_index}"),
            InlineKeyboardButton('🔽 Главное меню', callback_data='main_menu_search'),
            InlineKeyboardButton("Вперед ▶️", callback_data=f"next:{current_index}")
        )
    markup.add()
    return markup


def yesno() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('✅ Да', callback_data='yes'),
         InlineKeyboardButton('❌ Нет', callback_data='no')]
    ])
    return kb


def new_status(key) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton('📣 Активное объявление', callback_data='active')
    button_2 = InlineKeyboardButton('👬 Найден получатель', callback_data='agreement')
    button_3 = InlineKeyboardButton('✅ Вещи переданы', callback_data='confirm')
    button_4 = InlineKeyboardButton('📝 Создать объявление', callback_data='create')
    if key == 'active':
        kb.row(button_2)
    elif key == 'agreement':
        kb.row(button_1, button_3)
    else:
        kb.row(button_4)
    kb.row(InlineKeyboardButton("◀️ Назад", callback_data='back'))
    kb.add()
    return kb


def rating(agreement_id) -> InlineKeyboardMarkup:
    buttons = []
    for number in range(1, 6):
        buttons.append(InlineKeyboardButton(text=f"{number}", callback_data=f"rating_{agreement_id}_{number}"))
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(*buttons)
    button = [InlineKeyboardButton("◀️ Отмена", callback_data='rating_cancel')]
    kb.add(*button)
    return kb

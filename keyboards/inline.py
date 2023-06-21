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
    button = InlineKeyboardButton(text="◀️ Назад", callback_data="back")
    kb.add(button)
    return kb


async def cities_list(region_name) -> InlineKeyboardMarkup:
    buttons = []
    for city in await region.get_cities_by_region(region_name):
        buttons.append(InlineKeyboardButton(text=city, callback_data=city))
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*buttons)
    button = InlineKeyboardButton(text="◀️ Назад", callback_data="back")
    kb.add(button)
    return kb


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🪪 Мой профиль', callback_data='profile'),
         InlineKeyboardButton('⭐ Избранное', callback_data='favorites')],
        [InlineKeyboardButton('🔍 Найти объявление', callback_data='find'),
         InlineKeyboardButton('📝 Создать объявление', callback_data='create')]
    ])
    return kb


def profile_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('📃 Мои объявления', callback_data='my_adverts')],
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
    button = InlineKeyboardButton(text="◀️ Вернуться в главное меню", callback_data="main_menu")
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

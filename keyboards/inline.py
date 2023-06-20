from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import region


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


def link_to_group() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('✅ Подписаться на группу', url='https://t.me/+MUSmeO2CMZdjODVi')]
    ])
    return kb

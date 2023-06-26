from aiogram import Dispatcher
import logging

from aiogram import types
from decouple import config
from handlers.commands import register as reg_handlers
from handlers.registration import register as reg_registration
from handlers.profile import register as reg_profile
from handlers.create import register as reg_create
from handlers.search import register as reg_search
from handlers.favorites import register as reg_favorites


bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Начало работы с ботом")
    ])


def register_handlers(dp: Dispatcher):
    reg_handlers(dp)
    reg_registration(dp)
    reg_profile(dp)
    reg_create(dp)
    reg_search(dp)
    reg_favorites(dp)

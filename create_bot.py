import config
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
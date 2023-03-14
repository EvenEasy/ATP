import asyncio
from aiogram import executor, types
from create_bot import bot, dp
from mainparser import ATP

atp = ATP()

loop = asyncio.get_event_loop()
loop.create_task(atp.follow_start_live())

@dp.message_handler(commands=['start'])
async def start(message : types.Message):
    print('/start - {0.username} - {0.id}'.format(message.from_user))
    await message.answer(f"Вітаю, <b>{message.from_user.full_name}</b> !", parse_mode='HTML')

if __name__ == "__main__":
    executor.start_polling(
        dp,
        loop=loop,
        skip_updates=True
    )
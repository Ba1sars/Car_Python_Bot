import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from handlers import router

from car_bot.config import BOT_API

bot = Bot(BOT_API)
dp = Dispatcher()


async def set_bot_command():
    commands = [
        BotCommand(command="/start", description="Запускает бота"),
        BotCommand(command="/howareyou", description="Бот ответит как у него дела"),
    ]
    await bot.set_my_commands(commands)


async def main():
    dp.include_router(router)
    await set_bot_command()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExit")

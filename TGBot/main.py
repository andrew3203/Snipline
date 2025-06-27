import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
import asyncio
from src.config import settings
from src.domain.process.process import UserFlow
from src.utils.file import get_all_json_file_names
from src.application import notifications
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
flow = UserFlow()

COMMAND_TO_SCENARIO = get_all_json_file_names("src/flows")

@dp.message(Command(*COMMAND_TO_SCENARIO))
async def command_handler(message: Message, command: CommandObject):
    await flow.run_scenario(
        user_id=message.from_user.id,
        flow_key=command.command,
        lang=message.from_user.language_code,
        command_args=command.args,
        first_name=message.from_user.first_name,
        username=message.from_user.username,
    )
    await flow.handle_message(message)

@dp.message()
async def message_handler(message: Message):
    await flow.handle_message(message)

@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    await flow.handle_callback(callback)

async def main():
    await flow.start()
    await notifications.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
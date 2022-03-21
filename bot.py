import logging
from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = '5196471994:AAHU1ih4FL1PGElxRIhVkKeomCYEpYXO50w'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["радостно", "уставше", "грустно", "игриво", "беспокойно"]
    keyboard_markup.row(*(types.KeyboardButton(text) for text in buttons))
    await message.answer("Привет!\nЭто бот с картинками милых животных, которые поднимут твое настроение.")
    await message.answer("Как вы себя чувствуете?", reply_markup=keyboard_markup)

if __name__ == '__main__':
    executor.start_polling(dp)


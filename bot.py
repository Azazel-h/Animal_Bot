import logging
import random

from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import BotCommand
from aiogram.utils import executor
import json

TOKEN = '5196471994:AAHU1ih4FL1PGElxRIhVkKeomCYEpYXO50w'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


available_moods = ["Радостно", "Уставше", "Грустно", "Игриво", "Беспокойно"]
available_animals = ["Котики", "Собачки", "Попугаи", "Морские свинки", "Хомяки"]


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать"),
    ]
    await bot.set_my_commands(commands)


class MoodBooster(StatesGroup):
    start_cmd = State()
    waiting_for_moods = State()
    waiting_for_animal = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(types.KeyboardButton("Начать"))
    await message.answer("Привет!\nЭто бот с картинками милых животных, которые поднимут твое настроение.",
                         reply_markup=keyboard_markup)
    await MoodBooster.start_cmd.set()


@dp.message_handler(state=MoodBooster.start_cmd)
async def process_start_command(message: types.Message):
    if message.text not in ["Начать", "/start", "Хочу еще"]:
        await message.answer("Пожалуйста, нажмите на кнопку ниже, чтобы начать")
        return
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(*(types.KeyboardButton(text) for text in available_moods))
    await message.answer("Как вы себя чувствуете?", reply_markup=keyboard_markup)
    await MoodBooster.next()


@dp.message_handler(state=MoodBooster.waiting_for_moods)
async def process_mood_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_moods:
        await message.answer("Пожалуйста, выберите ваше настроение из меню ниже")
        return
    await state.update_data(chosen_mood=message.text)
    data = await state.get_data()
    print(data)

    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(*(types.KeyboardButton(text) for text in available_animals))
    await message.answer("Выберите животное", reply_markup=keyboard_markup)
    await MoodBooster.next()


@dp.message_handler(state=MoodBooster.waiting_for_animal)
async def process_animal_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_animals:
        await message.answer("Пожалуйста, выберите животное из меню ниже")
        return
    await state.update_data(chosen_animal=message.text)
    data = await state.get_data()
    print(data)

    await process_sending(message.from_user.id, state)


async def process_sending(_id, state):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(types.KeyboardButton("Хочу еще", callback_data='more'))

    with open("text_data.json", "r", encoding='utf-8-sig') as read_file:
        data = json.load(read_file)

    user_data = await state.get_data()
    print(data)

    await bot.send_photo(_id, photo=open(f"pictures/{user_data['chosen_animal']}/{random.randint(0, 3)}.jpg", 'rb'),
                         caption=data[user_data['chosen_mood']][random.randint(0, 3)],
                         reply_markup=keyboard_markup)
    await state.finish()
    await MoodBooster.start_cmd.set()


if __name__ == '__main__':
    executor.start_polling(dp)
    set_commands(bot)

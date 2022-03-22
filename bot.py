import asyncio
import logging
import random
import json

from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from aiogram.utils import executor

# Bot connection
TOKEN = '5196471994:AAHU1ih4FL1PGElxRIhVkKeomCYEpYXO50w'

loop = asyncio.get_event_loop()
bot = Bot(token=TOKEN, loop=loop)
dp = Dispatcher(bot, storage=MemoryStorage())

# Logger setup
logging.basicConfig(level=logging.INFO)

# Buttons text lists
available_moods = ["Радостно", "Уставше", "Грустно", "Игриво", "Беспокойно"]
available_animals = ["Котики", "Собачки", "Попугаи", "Морские свинки", "Хомяки"]


class MoodBooster(StatesGroup):
    """
    FSM class to manage states
    """
    start_cmd = State()
    waiting_for_mood = State()
    waiting_for_animal = State()


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: types.Message) -> None:
    """
    Function for /start command. Sends "welcome" message and resets
    all the things and sets the first state
    :param message: User "/start" message
    """
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(types.KeyboardButton("Начать"))
    await message.answer(
        "Привет!\nЭто бот с картинками милых животных, "
        "которые поднимут твое настроение.",
        reply_markup=keyboard_markup)
    await MoodBooster.start_cmd.set()


@dp.message_handler(commands=['help'], state="*")
async def help_command(message: types.Message) -> None:
    """
    Function for /help command. Help you not to get lost.
    Sends you some instructions
    :param message: User "/help" message
    """
    await message.answer(
        "Просто следуйте указаниям и жмите на кнопки. У вас все получится!\n "
        "/start - Сбросит все ваши действия и запустит бота снова!")


@dp.message_handler(lambda message: message.text in ["Хочу еще", "Начать"],
                    state=MoodBooster.start_cmd)
async def process_start(message: types.Message) -> None:
    """
    Checks pushing start button or repeat button.
    :param message: Pressed button text
    :return:
    """
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(
        *(types.KeyboardButton(text) for text in available_moods))
    await message.answer("Как вы себя чувствуете?",
                         reply_markup=keyboard_markup)
    await MoodBooster.next()


@dp.message_handler(lambda message: message.text in available_moods,
                    state=MoodBooster.waiting_for_mood)
async def process_mood(message: types.Message, state: FSMContext) -> None:
    """
    Checks pushing mood button and updates user_data
    :param message: Pressed button text
    :param state: Current state
    """
    await state.update_data(chosen_mood=message.text)

    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(
        *(types.KeyboardButton(text) for text in available_animals))
    await message.answer("Выберите животное", reply_markup=keyboard_markup)
    await MoodBooster.next()


@dp.message_handler(lambda message: message.text in available_animals,
                    state=MoodBooster.waiting_for_animal)
async def process_animal(message: types.Message, state: FSMContext) -> None:
    """
    Checks pushing animal button and updates user_data.
    Calling the process_sending to send a picture
    :param message: Pressed button text
    :param state: Current state
    """
    await state.update_data(chosen_animal=message.text)
    await process_sending(message, state)
    await state.finish()
    await MoodBooster.start_cmd.set()


async def process_sending(message: types.Message, state: FSMContext) -> None:
    """
    Process of sending a picture and some text
    :param message: Last message from user
    :param state: Current state
    """
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(types.KeyboardButton("Хочу еще"))

    with open("static/text_data.json", "r", encoding='utf-8-sig') as read_file:
        data = json.load(read_file)

    user_data = await state.get_data()
    logging.info(f'{message.from_user.username} - {str(user_data)}')

    await bot.send_photo(message.from_user.id,
                         photo=open(f"pictures/{user_data['chosen_animal']}/"
                                    f"{random.randint(0, 3)}.jpg", 'rb'),
                         caption=data[user_data['chosen_mood']][
                             random.randint(0, 3)],
                         reply_markup=keyboard_markup)


@dp.message_handler(content_types=ContentType.ANY, state="*")
async def bad_input_handler(message: types.Message) -> None:
    """
    Hands bad input and send a warning
    :param message: Bad input message
    """
    await message.answer(
        "Неверный ввод!\n"
        "Пожалуйста, используйте кнопки ниже или существующие команды!")


async def shutdown(dispatcher: Dispatcher) -> None:
    """
    Shutdown actions
    :param dispatcher: Bot's dispatcher
    """
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)

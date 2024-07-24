import telebot
from telebot import types
import logging
from enum import Enum
from typing import Dict
from telebot.types import Message

bot = telebot.TeleBot("")

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class UserStates(Enum):
    START = 0
    WANT_EAT = 1
    WANT_SHIT = 2
    PUREE_EATEN = 3
    MEATBALL_EATEN = 4
    PANTS_DOWN = 5
    MAKE_SHIT = 6
    PANTS_UP = 7
    UNDEFINED = 8
    CODE_BROWN = 9


user_states: Dict[int, UserStates] = {}


def update_user_state(chat_id: int, new_state: UserStates):
    user_states[chat_id] = new_state


def get_user_state(chat_id: int):
    return user_states.get(chat_id, UserStates.START)


def handle_error(error: RuntimeError):
    logging.error(f"Ошибка: {str(error)}")


@bot.message_handler(commands=["start"])
def start(message: Message):
    chat_id = message.chat.id
    update_user_state(chat_id, UserStates.START)
    send_message_for_state(chat_id, UserStates.START)


@bot.message_handler(func=lambda message: message.text == "Покушац")
def want_eat(message: Message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.START:
            update_user_state(chat_id, UserStates.WANT_EAT)
            send_message_for_state(chat_id, UserStates.WANT_EAT)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Котлетку")
def meatball(message: Message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.WANT_EAT:
            update_user_state(chat_id, UserStates.MEATBALL_EATEN)
            send_message_for_state(chat_id, UserStates.MEATBALL_EATEN)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Пюрешку")
def puree(message: Message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.WANT_EAT:
            update_user_state(chat_id, UserStates.PUREE_EATEN)
            send_message_for_state(chat_id, UserStates.PUREE_EATEN)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Да")
def yes(message: Message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.PUREE_EATEN | UserStates.MEATBALL_EATEN:
            update_user_state(chat_id, UserStates.WANT_EAT)
            send_message_for_state(chat_id, UserStates.WANT_EAT)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Нет")
def no(message: Message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.PUREE_EATEN | UserStates.MEATBALL_EATEN:
            update_user_state(chat_id, UserStates.START)
            send_message_for_state(chat_id, UserStates.START)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Покакать")
def want_shit(message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.START:
            update_user_state(chat_id, UserStates.WANT_SHIT)
            send_message_for_state(chat_id, UserStates.WANT_SHIT)
        case UserStates.WANT_SHIT:
            send_message_for_state(chat_id, UserStates.CODE_BROWN)
            send_message_for_state(chat_id, current_state)
        case UserStates.PANTS_DOWN:
            update_user_state(chat_id, UserStates.MAKE_SHIT)
            send_message_for_state(chat_id, UserStates.MAKE_SHIT)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Снять штаны")
def pants_down(message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.WANT_SHIT:
            update_user_state(chat_id, UserStates.PANTS_DOWN)
            send_message_for_state(chat_id, UserStates.PANTS_DOWN)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


@bot.message_handler(func=lambda message: message.text == "Надеть штаны")
def pants_up(message):
    chat_id = message.chat.id
    current_state = get_user_state(chat_id)
    match current_state:
        case UserStates.MAKE_SHIT:
            send_message_for_state(chat_id, UserStates.PANTS_UP)
            update_user_state(chat_id, UserStates.START)
            send_message_for_state(chat_id, UserStates.START)
        case UserStates.PANTS_DOWN:
            update_user_state(chat_id, UserStates.WANT_SHIT)
            send_message_for_state(chat_id, UserStates.WANT_SHIT)
        case _:
            send_message_for_state(chat_id, UserStates.UNDEFINED)
            send_message_for_state(chat_id, current_state)


def send_message_for_state(chat_id: int, state: UserStates):
    match state:
        case UserStates.START:
            bot.send_message(
                chat_id,
                "Что вы хотите сделать?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Покушац"), types.KeyboardButton("Покакать")
                ),
            )
        case UserStates.WANT_EAT:
            bot.send_message(
                chat_id,
                "Что будем кушац?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Котлетку"), types.KeyboardButton("Пюрешку")
                ),
            )
        case UserStates.PUREE_EATEN | UserStates.MEATBALL_EATEN:
            product = "Пюрешка" if state == UserStates.PUREE_EATEN else "Котлетка"
            bot.send_message(
                chat_id,
                f"{product} скушана! Хотите добавки?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Да"), types.KeyboardButton("Нет")
                ),
            )
        case UserStates.WANT_SHIT:
            bot.send_message(
                chat_id,
                "Штаны надеты. Что делать дальше?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Снять штаны"),
                    types.KeyboardButton("Покакать"),
                    types.KeyboardButton("Надеть штаны"),
                ),
            )
        case UserStates.PANTS_DOWN:
            bot.send_message(
                chat_id,
                "Штаны сняты. Что делать дальше?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Снять штаны"),
                    types.KeyboardButton("Покакать"),
                    types.KeyboardButton("Надеть штаны"),
                ),
            )
        case UserStates.MAKE_SHIT:
            bot.send_message(
                chat_id,
                "Покакали. Что делать дальше?",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton("Снять штаны"),
                    types.KeyboardButton("Покакать"),
                    types.KeyboardButton("Надеть штаны"),
                ),
            )
        case UserStates.PANTS_UP:
            bot.send_message(chat_id, "Поздравляю! Вы покакали!")
        case UserStates.CODE_BROWN:
            bot.send_message(chat_id, "Бинго! Ты посрал не снимая свитера!")
        case _:
            bot.send_message(chat_id, "Я хз как тебе помочь, давай попробуем сначала?")


if __name__ == "__main__":
    bot.polling(none_stop=True)

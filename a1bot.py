from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from aiogram.types import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатура с вариантами целей обращения
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Купить квартиру для себя")],
        [KeyboardButton(text="Купить для инвестиции")],
        [KeyboardButton(text="Продать квартиру")],
        [KeyboardButton(text="Одобрить ипотеку")],
    ],
    resize_keyboard=True
)

# Клавиатуры для этапов сценария "Купить квартиру для себя"
buy_time_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="В ближайшие 2 месяца")],
        [KeyboardButton(text="В течение полугода")],
        [KeyboardButton(text="Только присматриваю")],
    ],
    resize_keyboard=True
)

city_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Казань")],
        [KeyboardButton(text="Москва")],
        [KeyboardButton(text="Петербург")],
        [KeyboardButton(text="Сочи")],
    ],
    resize_keyboard=True
)

flat_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Студия")],
        [KeyboardButton(text="1-комнатная")],
        [KeyboardButton(text="2-комнатная")],
        [KeyboardButton(text="3-комнатная")],
        [KeyboardButton(text="4-комнтаная")],
        [KeyboardButton(text="5-комнатная")],
        [KeyboardButton(text="Не определился")],
    ],
    resize_keyboard=True
)

first_payment_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="500 тыс - 1 млн")],
        [KeyboardButton(text="1 млн - 3 млн")],
        [KeyboardButton(text="Свыше 3 млн")],
    ],
    resize_keyboard=True
)

# Клавиатура для возврата в главное меню
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True
)

# Клавиатура для запроса номера телефона
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить номер телефона", request_contact=True)],
    ],
    resize_keyboard=True
)

user_states = {}

async def send_welcome(message: types.Message):
    user = message.from_user
    welcome_text = (
        f"*{user.first_name}*, рады Вас приветствовать и помочь с решением Вашего вопроса!\n\n"
        "Вы в боте агентства недвижимости A1 Brokers Group, но тут на связи живые люди👋🏼\n\n"
        "Сначала бот попросит Вас ответить на несколько коротких вопросов, а затем подключимся мы!\n\n"
        "Какова цель вашего обращения? 👇🏼"
    )
    await message.answer(welcome_text, reply_markup=main_keyboard, parse_mode="Markdown")
    user_states[user.id] = {"step": None, "data": {}}

async def handle_main_choice(message: types.Message):
    user = message.from_user
    if message.text == "Купить квартиру для себя":
        user_states[user.id] = {"step": 1, "data": {"purpose": "Купить квартиру для себя"}}
        await message.answer("Когда вы планируете покупку?", reply_markup=buy_time_keyboard)
    elif message.text == "Купить для инвестиции":
        user_states[user.id] = {"step": 101, "data": {"purpose": "Купить для инвестиции"}}
        await message.answer("Когда вы планируете покупку?", reply_markup=buy_time_keyboard)
    elif message.text in ["Продать квартиру", "Одобрить ипотеку"]:
        user_states[user.id] = {"step": 201, "data": {"purpose": message.text}}
        await message.answer(
            "Пожалуйста, опишите Ваш запрос, чтобы менеджер мог дать полезный и применимый для Вас ответ и найти решение",
            reply_markup=ReplyKeyboardRemove()
        )

async def handle_buy_time(message: types.Message):
    user = message.from_user
    if user.id not in user_states or user_states[user.id].get("step") != 1:
        return
    user_states[user.id]["data"]["buy_time"] = message.text
    user_states[user.id]["step"] = 2
    await message.answer("В каком городе вы ищете недвижимость?", reply_markup=city_keyboard)

async def handle_city(message: types.Message):
    user = message.from_user
    if user.id not in user_states or user_states[user.id].get("step") != 2:
        return
    user_states[user.id]["data"]["city"] = message.text
    user_states[user.id]["step"] = 3
    await message.answer("Какую квартиру Вы планируете покупать?", reply_markup=flat_type_keyboard)

async def handle_flat_type(message: types.Message):
    user = message.from_user
    if user.id not in user_states or user_states[user.id].get("step") != 3:
        return
    user_states[user.id]["data"]["flat_type"] = message.text
    user_states[user.id]["step"] = 4
    await message.answer("Какой первый взнос планируете вносить?", reply_markup=first_payment_keyboard)

async def handle_first_payment(message: types.Message):
    user = message.from_user
    if user.id not in user_states or user_states[user.id].get("step") != 4:
        return
    # Проверяем наличие username
    if not user.username and user_states[user.id]["data"].get("phone") is None:
        user_states[user.id]["step"] = 5
        await message.answer("Пожалуйста, отправьте свой номер телефона для связи, используя кнопку ниже:", reply_markup=phone_keyboard)
        return
    user_states[user.id]["data"]["first_payment"] = message.text
    user_states[user.id]["step"] = None
    thank_text = (
        f"*{user.first_name}*, спасибо!\n\n"
        "Передаю информацию менеджеру, чтобы Вы могли обсудить подробности!\n\n"
        "Наш график работы:\n\nЕжедневно с 09 до 21ч по московскому времени"
    )
    await message.answer(thank_text, reply_markup=main_menu_keyboard, parse_mode="Markdown")
    # Отправка данных менеджерам
    manager_ids = [6413686861, 762315344]
    data = user_states[user.id]["data"]
    username = user.username or "-"
    info = (
        f"Пользователь: {user.first_name} (@{username}) ({user.id})\n"
        f"Цель: Купить квартиру для себя\n"
        f"Когда планирует покупку: {data.get('buy_time')}\n"
        f"Город: {data.get('city')}\n"
        f"Тип квартиры: {data.get('flat_type')}\n"
        f"Первый взнос: {data.get('first_payment')}"
        + (f"\nТелефон: {data.get('phone')}" if data.get('phone') else "")
    )
    for manager_id in manager_ids:
        await bot.send_message(manager_id, info)

async def handle_first_payment_invest(message: types.Message):
    user = message.from_user
    if user.id not in user_states or user_states[user.id].get("step") != 104:
        return
    if not user.username and user_states[user.id]["data"].get("phone") is None:
        user_states[user.id]["step"] = 105
        await message.answer("Пожалуйста, отправьте свой номер телефона для связи, используя кнопку ниже:", reply_markup=phone_keyboard)
        return
    user_states[user.id]["data"]["first_payment"] = message.text
    user_states[user.id]["step"] = None
    thank_text = (
        f"*{user.first_name}*, спасибо!\n\n"
        "Передаю информацию менеджеру, чтобы Вы могли обсудить подробности!\n\n"
        "Наш график работы:\n\nЕжедневно с 09 до 21ч по московскому времени"
    )
    await message.answer(thank_text, reply_markup=main_menu_keyboard, parse_mode="Markdown")
    # Отправка данных менеджерам
    manager_ids = [6413686861, 762315344]
    data = user_states[user.id]["data"]
    username = user.username or "-"
    info = (
        f"Пользователь: {user.first_name} (@{username}) ({user.id})\n"
        f"Цель: Купить для инвестиции\n"
        f"Когда планирует покупку: {data.get('buy_time')}\n"
        f"Город: {data.get('city')}\n"
        f"Тип квартиры: {data.get('flat_type')}\n"
        f"Первый взнос: {data.get('first_payment')}"
        + (f"\nТелефон: {data.get('phone')}" if data.get('phone') else "")
    )
    for manager_id in manager_ids:
        await bot.send_message(manager_id, info)

async def handle_phone(message: types.Message):
    user = message.from_user
    step = user_states.get(user.id, {}).get("step")
    if step not in [5, 105]:
        return
    phone = None
    if message.contact and message.contact.phone_number:
        phone = message.contact.phone_number
    elif message.text and message.text.startswith("+"):
        phone = message.text
    if not phone:
        await message.answer("Пожалуйста, используйте кнопку для отправки номера телефона.")
        return
    user_states[user.id]["data"]["phone"] = phone
    # Возвращаемся к завершению сценария
    if step == 5:
        await handle_first_payment(message)
    elif step == 105:
        await handle_first_payment_invest(message)

async def handle_free_text(message: types.Message):
    user = message.from_user
    if user.id not in user_states or user_states[user.id].get("step") != 201:
        return
    user_states[user.id]["data"]["request_text"] = message.text
    user_states[user.id]["step"] = None
    thank_text = (
        f"*{user.first_name}*, спасибо!\n\n"
        "Передаю информацию менеджеру, чтобы Вы могли обсудить подробности!\n\n"
        "Наш график работы:\n\nЕжедневно с 09 до 21ч по московскому времени"
    )
    await message.answer(thank_text, reply_markup=main_menu_keyboard, parse_mode="Markdown")
    # Отправка данных менеджеру
    manager_id = 6413686861
    data = user_states[user.id]["data"]
    username = user.username or "-"
    info = (
        f"Пользователь: {user.first_name} (@{username}) ({user.id})\n"
        f"Цель: {data.get('purpose')}\n"
        f"Запрос: {data.get('request_text')}"
    )
    await bot.send_message(manager_id, info)

async def cmd_start(message: types.Message):
    await send_welcome(message)

async def buy_flat_for_self(message: types.Message):
    await handle_main_choice(message)

async def buy_flat_for_investment(message: types.Message):
    await handle_main_choice(message)

async def sell_flat(message: types.Message):
    await handle_main_choice(message)

async def approve_mortgage(message: types.Message):
    await handle_main_choice(message)

async def process_buy_time(message: types.Message):
    user = message.from_user
    if user.id not in user_states:
        return
    purpose = user_states[user.id].get("data", {}).get("purpose")
    if purpose == "Купить квартиру для себя":
        await handle_buy_time(message)
    elif purpose == "Купить для инвестиции":
        await handle_buy_time_invest(message)

async def process_city(message: types.Message):
    user = message.from_user
    if user.id not in user_states:
        return
    purpose = user_states[user.id].get("data", {}).get("purpose")
    if purpose == "Купить квартиру для себя":
        await handle_city(message)
    elif purpose == "Купить для инвестиции":
        await handle_city_inвест(message)

async def process_flat_type(message: types.Message):
    user = message.from_user
    if user.id not in user_states:
        return
    purpose = user_states[user.id].get("data", {}).get("purpose")
    if purpose == "Купить квартиру для себя":
        await handle_flat_type(message)
    elif purpose == "Купить для инвестиции":
        await handle_flat_type_invest(message)

async def process_first_payment(message: types.Message):
    user = message.from_user
    if user.id not in user_states:
        return
    purpose = user_states[user.id].get("data", {}).get("purpose")
    if purpose == "Купить квартиру для себя":
        await handle_first_payment(message)
    elif purpose == "Купить для инвестиции":
        await handle_first_payment_invest(message)

async def echo_all(message: types.Message):
    user = message.from_user
    if message.text == "В главное меню":
        await send_welcome(message)
        return
    if user.id not in user_states:
        return
    step = user_states[user.id].get("step")
    if step == 201:
        await handle_free_text(message)
    else:
        await message.answer("Не совсем понял вас. Можете переформулировать?")

# В самом низу файла добавим запуск polling
async def main():
    from aiogram import Router
    router = Router()
    # Регистрируем универсальный хендлер
    router.message.register(cmd_start, F.text == "/start")
    router.message.register(buy_flat_for_self, F.text == "Купить квартиру для себя")
    router.message.register(buy_flat_for_investment, F.text == "Купить для инвестиции")
    router.message.register(sell_flat, F.text == "Продать квартиру")
    router.message.register(approve_mortgage, F.text == "Одобрить ипотеку")
    router.message.register(process_buy_time, F.text.in_(["В ближайшие 2 месяца", "В течение полугода", "Только присматриваю"]))
    router.message.register(process_city, F.text.in_(["Казань", "Москва", "Петербург", "Сочи"]))
    router.message.register(process_flat_type, F.text.in_(["Студия", "1-комнатная", "2-комнатная", "3-комнатная", "4-комнтаная", "5-комнатная", "Не определился"]))
    router.message.register(process_first_payment, F.text.in_(["500 тыс - 1 млн", "1 млн - 3 млн", "Свыше 3 млн"]))
    router.message.register(echo_all)
    router.message.register(handle_phone, F.contact | (F.text.regexp(r"^\\+\\d{10,15}$")))
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

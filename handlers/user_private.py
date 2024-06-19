from aiogram.filters import CommandStart
from aiogram.types.web_app_info import WebAppInfo
from database.session import Database
from database.models import Admin
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message,
                           ReplyKeyboardMarkup,
                           KeyboardButton)
from aiogram import (Router,
                     F)
from aiogram.fsm.state import (State,
                               StatesGroup)

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! Добро пожаловать в наш магазин.\n"
        f"Перейдите в наш магазин, нажав на кнопку ниже:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(
                text="Открыть магазин",
                web_app=WebAppInfo(
                    url='https://127.0.0.1:8000'
                )
            )]
        ],
            resize_keyboard=True
        )
    )

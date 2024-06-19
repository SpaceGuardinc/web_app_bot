from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           WebAppInfo)

admin_start_panel = reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text="Добавить товар"
        ),
            KeyboardButton(
                text="Посмотреть товары"
            )],
        [KeyboardButton(
            text="Открыть магазин",
            web_app=WebAppInfo(
                url='https://127.0.0.1:8000'
            )
        )]
    ],
    resize_keyboard=True
)

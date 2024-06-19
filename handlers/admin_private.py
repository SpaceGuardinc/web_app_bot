from string import punctuation
import os
from dotenv import (find_dotenv,
                    load_dotenv)
from aiogram.types.web_app_info import WebAppInfo
from database.orm_query import orm_add_product, orm_get_products, orm_delete_product
from database.engine import Database
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message,
                           ReplyKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardRemove, CallbackQuery)

from for_handlers.admin_inline_keyboard import get_callback_buttons
from for_handlers.admin_start_keyboard import admin_start_panel
from for_handlers.messages import get_shop_message
from aiogram import (Router,
                     F)
from aiogram.fsm.state import (State,
                               StatesGroup)
from database.models import (Admin,
                             User)
from aiogram.filters import (CommandStart,
                             Command,
                             StateFilter)
import aiohttp
from aiogram import Bot

admin_private_router = Router()
db = Database()
bot = Bot(token=os.getenv("API_TOKEN"))


async def is_admin(telegram_id: int):
    admin = await db.session_maker().query(Admin).filter_by(admin_telegram_id=telegram_id).first()
    if admin:
        return True


async def get_or_create_user(telegram_id: int):
    user = await db.session_maker().query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        print(f"Создаем пользователя с ID {telegram_id}")
        user = User(telegram_id=telegram_id)
        await db.session_maker().add(user)
        await db.session_maker().commit()
    else:
        print(f"Пользователь с ID {telegram_id} уже существует")
    return user


class AddProduct(StatesGroup):
    product_name = State()
    product_description = State()
    product_size = State()
    product_brand = State()
    product_sex = State()
    product_category = State()
    product_price = State()
    product_photo = State()

    texts = {
        'AddProduct:product_name': 'Введите название заново',
        'AddProduct:product_description': 'Введите описание заново',
        'AddProduct:product_size': 'Введите размер заново',
        'AddProduct:product_brand': 'Введите бренд заново',
        'AddProduct:product_sex': 'Введите пол заново',
        'AddProduct:product_category': 'Введите категорию заново',
        'AddProduct:product_price': 'Введите цену заново',
        'AddProduct:product_photo': 'Этот стейт последний',

    }


@admin_private_router.message(CommandStart())
async def start(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    user = get_or_create_user(user_id)
    if is_admin(user_id):
        await message.answer(
            f"Привет, {user_name}! Добро пожаловать в наш магазин.\n"
            f"Вы администратор. Вы можете создавать товары в базе данных.",
            reply_markup=admin_start_panel
        )
    else:
        await message.answer(
            f"Привет, {user_name}! Добро пожаловать в наш магазин.\n"
            f"Перейдите в наш магазин, нажав на кнопку ниже:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
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


@admin_private_router.message(F.text == "Посмотреть товары")
async def starring_at_product(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        for product in await orm_get_products(session):
            await message.answer_photo(
                product.product_photo,
                caption=f"Название: {product.product_name}\n"
                        f"Описание: {product.product_description}\n"
                        f"Стоимость: {product.product_price}\n"
                        f"Бренд: {product.product_brand}\n"
                        f"Пол: {product.product_sex}\n"
                        f"Категория: {product.product_category}\n"
                        f"Размер: {product.product_size}",
                reply_markup=get_callback_buttons(buttons={
                    'Удалить товар': f'delete_{product.product_id}',
                    'Изменить товар': f'edit_{product.product_id}'
                })
            )
        await message.answer("Список товаров")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    await callback.answer("Товар удален")
    await callback.message.answer("Товар удален")


# Код ниже для машины состояний (FSM)

@admin_private_router.message(StateFilter(None), F.text == "Добавить товар")
async def answer(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer(
            f"Введите название товара:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(AddProduct.product_name)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(StateFilter('*'), Command("отмена"))
@admin_private_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        current_state = await state.get_state()
        if current_state is None:
            return

        await state.clear()
        await message.answer(
            "Действия отменены",
            reply_markup=admin_start_panel
        )
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(Command("назад"))
@admin_private_router.message(F.text.casefold() == "назад")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        current_state = await state.get_state(message)

        if current_state == AddProduct.product_name:
            await message.answer(
                'Предыдущего шага нет, или введите название товара или напишите "отмена"'
            )
            return

        previous = None
        for step in AddProduct.__all_states__:
            if step.state == current_state:
                await state.set_state(previous)
                await message.answer(
                    f"Вы вернулись к прошлому шагу \n "
                    f"{AddProduct.texts[previous.state]}")
                return
            previous = step
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_name, F.text)
async def add_name(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_name=message.text)
        await message.answer("Введите описание товара")
        await state.set_state(AddProduct.product_description)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_name)
async def add_name(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_description, F.text)
async def add_description(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_description=message.text)
        await message.answer("Введите размер товара")
        await state.set_state(AddProduct.product_size)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_description)
async def add_description(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_size, F.text)
async def add_size(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_size=message.text)
        await message.answer("Введите бренд товара")
        await state.set_state(AddProduct.product_brand)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_size)
async def add_size(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_brand, F.text)
async def add_brand(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_brand=message.text)
        await message.answer("Введите пол товара")
        await state.set_state(AddProduct.product_sex)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_brand)
async def add_brand(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_sex, F.text)
async def add_sex(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_sex=message.text)
        await message.answer("Введите категорию товара")
        await state.set_state(AddProduct.product_category)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_sex)
async def add_sex(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_category, F.text)
async def add_category(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_category=message.text)
        await message.answer("Введите цену товара")
        await state.set_state(AddProduct.product_price)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_category)
async def add_category(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message()
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_price, F.text)
async def add_price(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await state.update_data(product_price=message.text)
        await message.answer("Загрузите изображение товара")
        await state.set_state(AddProduct.product_photo)
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_price)
async def add_price(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, введите текст заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_photo, F.photo)
async def add_image(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if is_admin(message.from_user.id):
        photo: PhotoSize = message.photo[-1]
        # Получаем объект файла фотографии
        file = await bot.get_file(photo.file_id)
        # Получаем содержимое файла
        photo_data = await bot.download_file(file.file_path)
        photo_data = photo_data.read()  # Преобразуем в bytes
        data = await state.get_data()
        try:
            # Передаем идентификатор фотографии и ее данные в функцию orm_add_product
            await orm_add_product(session, data, photo.file_id, photo_data)
            await message.answer(
                "Товар добавлен",
                reply_markup=admin_start_panel
            )
            # Очищаем состояние после успешного добавления товара
            await state.clear()
        except Exception as e:
            await message.answer(
                f"Ошибка: \n{str(e)}",
                reply_markup=admin_start_panel
            )
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message(AddProduct.product_photo)
async def add_image(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Вы ввели недопустимые данные, пришлите фото заново")
    else:
        shop_message = await get_shop_message(message)
        await message.answer(shop_message)


@admin_private_router.message()
async def handle_all_messages(message: Message) -> None:
    shop_message = await get_shop_message(message)
    await message.answer(shop_message)

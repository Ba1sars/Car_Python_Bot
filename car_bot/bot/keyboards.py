from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from car_bot.database.database_commands import fetch_factory
from aiogram.fsm.context import FSMContext

marque_array = set([i for i in fetch_factory("marque", None, None) if i])


async def inline_marque_buttons():
    keyboard = InlineKeyboardBuilder()
    for marque in marque_array:
        keyboard.add(InlineKeyboardButton(
            text=str(marque),
            callback_data=f"marque_{marque}"
        ))
    return keyboard.adjust(2).as_markup()


async def inline_model_buttons(state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    user_data = await state.get_data()
    model_array = set(fetch_factory(
        user_data["user_marque"],
        "model",
        None
    ))
    for model in model_array:
        keyboard.add(InlineKeyboardButton(
            text=str(model),
            callback_data=f"model_{model}"
        ))
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_marque"
    ))
    return keyboard.adjust(2).as_markup()


async def inline_series_with_publish_year_buttons(state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    user_data = await state.get_data()
    try:
        model = int(user_data["user_model"])
    except Exception:
        model = user_data["user_model"]
    series_array = set(fetch_factory(
        user_data["user_marque"],
        model,
        "series_with_publish_year"
    ))
    for series in series_array:
        keyboard.add(InlineKeyboardButton(
            text=str(series),
            callback_data=f"series_year_{series}"
        ))
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_model"
    ))
    return keyboard.adjust(2).as_markup()


async def inline_first_photo_link_buttons(state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    user_data = await state.get_data()
    version = f"Версия {user_data['current_index'] + 1}"
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_series_year"
    ))
    keyboard.add(InlineKeyboardButton(
        text="Выбрать",
        callback_data=f"photo_link_{version}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="Вперёд ➡️",
        callback_data="next_photo"
    ))
    return keyboard.adjust(3).as_markup()


async def inline_next_photo_link_buttons(state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    user_data = await state.get_data()
    version = f"Версия {user_data['current_index'] + 1}"
    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_previous_photo"
    ))
    keyboard.add(InlineKeyboardButton(
        text="Выбрать",
        callback_data=f"photo_link_{version}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="Вперёд ➡️",
        callback_data="next_photo"
    ))
    return keyboard.adjust(3).as_markup()

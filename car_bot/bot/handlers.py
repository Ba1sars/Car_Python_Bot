from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb


class User_Dashcam(StatesGroup):
    user_marque = State()
    user_model = State()
    user_series = State()
    user_publish_year = State()
    user_dashcam = State()
    user_photo_link = State()
    user_choice = State()
    to_show = State()


router = Router()


@router.message(Command("howareyou"))
async def how_to(message: Message):
    await message.answer("Всё замечательно, ведь я вам помогаю !")


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(User_Dashcam.user_marque)
    await message.reply(
        "Привет! Выбери марку машины !", reply_markup=await kb.inline_marque_buttons()
    )


@router.message(F.sticker)
async def ans_to(message: Message):
    await message.answer("У меня нет глаз! Я не вижу картинки :)")


@router.callback_query(F.data.startswith("marque_"))
async def marque(callback: CallbackQuery, state: FSMContext):
    await state.update_data(user_marque=callback.data.split("_")[-1])
    user_data = await state.get_data()
    await callback.answer(f'Вы выбрали марку машины - {user_data["user_marque"]}')
    await callback.message.edit_text(
        "Теперь выберите модель машины:",
        reply_markup=await kb.inline_model_buttons(state),
    )


@router.callback_query(F.data.startswith("model_"))
async def model(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User_Dashcam.user_model)
    await state.update_data(user_model=callback.data.split("_")[-1])
    user_data = await state.get_data()
    await callback.answer(f'Вы выбрали модель машины - {user_data["user_model"]}')
    await callback.message.edit_text(
        "Теперь выберите серию:",
        reply_markup=await kb.inline_series_with_publish_year_buttons(state),
    )


@router.callback_query(F.data.startswith("series_year_"))
async def series(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User_Dashcam.user_series)
    await state.update_data(user_series=callback.data.split("_")[-1])
    user_data = await state.get_data()
    try:
        model = int(user_data["user_model"])
    except Exception as e:
        model = user_data["user_model"]
    await callback.answer(f'Вы выбрали такую серию машины - {user_data["user_series"]}')
    found_dashcam = kb.fetch_factory(
        user_data["user_marque"], model, user_data["user_series"]
    )
    dashcam_name, photo_link_V1, photo_link_V2, photo_link_V3 = found_dashcam[0]
    photo_links = [
        link for link in [photo_link_V1, photo_link_V2, photo_link_V3] if link
    ]
    await state.update_data(user_dashcam=dashcam_name)
    await state.update_data(photo_links=photo_links)
    await state.update_data(current_index=0)

    if len(photo_links) == 1:
        await state.update_data(user_photo_link=photo_links[0])
        await state.update_data(user_choice="Версия 1")
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo_links[0],
            caption=f"<b>Отлично!</b>\nВам подходит такой регистратор:\nНазвание: <b>{dashcam_name}</b>\nВерсия: <b>1</b>\n"
            f'Свяжитесь с нами для оформления заказа.\nТелефон: <a href="tel:+78745168742">+7 (874) 516-87-42</a>\n'
            "Telegram - @lorem_ipsum",
            parse_mode="HTML",
        )
        await callback.answer()
        await state.clear()
    else:
        current_index = 0
        current_photo = photo_links[current_index]
        version = f"Версия {current_index + 1}"
        await state.update_data(to_show=version)
        await state.update_data(user_photo_link=current_photo)
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=current_photo,
            caption=f"<b>{version}</b>\nНазвание: <b>{dashcam_name}</b>\n"
            f"Вам было подобрано несколько версий одного регистратора.\nВыберите интересующую вас версию.\n",
            parse_mode="HTML",
            reply_markup=await kb.inline_first_photo_link_buttons(state),
        )


@router.callback_query(F.data == "next_photo")
async def next_photo(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_index = user_data["current_index"]
    photo_links = user_data["photo_links"]
    if current_index < len(photo_links) - 1:
        current_index += 1
        await state.update_data(current_index=current_index)
        current_photo = photo_links[current_index]
        version = f"Версия {current_index + 1}"
        await state.update_data(to_show=version)
        await state.update_data(user_photo_link=current_photo)
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=current_photo,
            caption=f'<b>{version}</b>\nНазвание: <b>{user_data["user_dashcam"]}</b>\n'
            f"Вам было подобрано несколько версий одного регистратора.\nВыберите интересующую вас версию.\n",
            parse_mode="HTML",
            reply_markup=await kb.inline_next_photo_link_buttons(state),
        )
    else:
        await callback.answer("Это последняя фотография!")


@router.callback_query(F.data.startswith("photo_link_"))
async def chosen_photo_link(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await callback.message.delete()
    await callback.message.answer_photo(
        photo=user_data["user_photo_link"],
        caption=f"Отлично!\nВы выбрали регистратор.\nНазвание: <b>{user_data['user_dashcam']}</b>\n<b>{user_data['to_show']}</b>\n"
        f'Свяжитесь с нами для оформления заказа.\nТелефон: <a href="tel:+78745168742">+7 (874) 516-87-42</a>\n'
        "Telegram - @lorem_ipsum",
        parse_mode="HTML",
    )
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "back_to_marque")
async def back_to_marque(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User_Dashcam.user_marque)
    user_data = await state.get_data()
    if "user_model" in user_data:
        await state.update_data(user_model=None)
    await callback.answer("Возвращаемся к выбору марки")
    await callback.message.edit_text(
        "Выберите марку машины:", reply_markup=await kb.inline_marque_buttons()
    )


@router.callback_query(F.data == "back_to_model")
async def back_to_model(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User_Dashcam.user_model)
    user_data = await state.get_data()
    if "user_series" in user_data:
        await state.update_data(user_series=None)
    await callback.answer("Возвращаемся к выбору модели")
    await callback.message.edit_text(
        "Выберите модель машины:", reply_markup=await kb.inline_model_buttons(state)
    )


@router.callback_query(F.data == "back_to_series_year")
async def back_to_series(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User_Dashcam.user_dashcam)
    user_data = await state.get_data()
    if "user_dashcam" in user_data:
        await state.update_data(user_series=None)
    if "photo_links" in user_data:
        await state.update_data(photo_links=None)
    if "to_show" in user_data:
        await state.update_data(to_show=None)
    if "current_index" in user_data:
        await state.update_data(current_index=None)
    await callback.message.delete()
    await callback.answer("Возвращаемся к выбору серии")
    await callback.message.answer(
        "Выберите серию машины:",
        reply_markup=await kb.inline_series_with_publish_year_buttons(state),
    )


@router.callback_query(F.data == "back_to_previous_photo")
async def back_to_previous_photo(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    current_index = user_data["current_index"]
    photo_links = user_data["photo_links"]
    if current_index > 0:
        current_index -= 1
        await state.update_data(current_index=current_index)
        current_photo = photo_links[current_index]
        version = f"Версия {current_index + 1}"
        await state.update_data(to_show=version)
        await state.update_data(user_photo_link=current_photo)
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=current_photo,
            caption=f'<b>{version}</b>\nНазвание: <b>{user_data["user_dashcam"]}</b>\n'
            f"Вам было подобрано несколько версий одного регистратора.\nВыберите интересующую вас версию.\n",
            parse_mode="HTML",
            reply_markup=await kb.inline_first_photo_link_buttons(state),
        )
    else:
        await callback.answer("Это первая фотография!")

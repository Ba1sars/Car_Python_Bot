import keyboards as kb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from car_bot.config import (EMAIL, MONJARO_DOC_PATH, MONJARO_VIDEO_PATH,
                            TEL_NUMBER, TELEGRAMM_TAG, WEB_SITE_LINK,
                            WEB_SITE_NAME, WHATSAPP_LINK, WHATSAPP_TEL)

VIDEO_FILE_ID = None
DOC_FILE_ID = None


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


# START OF START COMMAND BLOCK
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Нажмите на кнопку <b>Меню</b> и выберите нужную вам функцию !",
        parse_mode="HTML",
    )


# END OF START COMMAND BLOCK


# START OF HOWAREYOU COMMAND BLOCK
@router.message(Command("howareyou"))
async def how_to(message: Message):
    await message.answer("Всё замечательно, ведь я вам помогаю !")


# END OF HOWAREYOU COMMAND BLOCK


# START OF FINDDASHCAM COMMAND BLOCK
@router.message(Command("finddashcam"))
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
    except Exception:
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
            caption=f"<b>Отлично!</b>\nВам подходит такой регистратор:\nНазвание - <b>{dashcam_name}</b>\nВерсия - <b>1</b>\n",
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
            f"Вам было подобрано несколько версий одного регистратора.\nВыберите интересующую вас версию.\n"
            f'Свяжитесь с нами для оформления заказа.\nТелефон - <a href = "tel:{TEL_NUMBER}">{TEL_NUMBER}</a>\n'
            f"Telegram - {TELEGRAMM_TAG}\n"
            f"Whatsapp - <a href={WHATSAPP_LINK}>{WHATSAPP_TEL}</a>\n",
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
        caption=f"Отлично!\nВы выбрали регистратор.\nНазвание - <b>{user_data['user_dashcam']}</b>\n<b>{user_data['to_show']}</b>\n"
        f'Свяжитесь с нами для оформления заказа.\nТелефон - <a href = "tel:{TEL_NUMBER}">{TEL_NUMBER}</a>\n'
        f"Telegram - {TELEGRAMM_TAG}\n"
        f"Whatsapp - <a href={WHATSAPP_LINK}>{WHATSAPP_TEL}</a>\n",
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


# END OF FINDDASHCAM COMMAND BLOCK


# START OF SALE COMMAND BLOCK
@router.message(Command("sale"))
async def sale_start(message: Message):
    await message.answer("ПОКА БЛОК В РАЗРАБОТКЕ. БЛОК ДЛЯ АКЦИЙ НА РЕГИСТРАТОРЫ !")


# END OF SALE COMMAND BLOCK


# START OF REGISTRATION COMMAND BLOCK
@router.message(Command("registration"))
async def reg_start(message: Message):
    await message.answer("ПОКА БЛОК В РАЗРАБОТКЕ. БЛОК ДЛЯ РЕГИСТРАЦИИ НА УСТАНОВКУ")


# END OF REGISTRATION COMMAND BLOCK


# START OF SUPPORT COMMAND BLOCK
@router.message(Command("support"))
async def support_start(message: Message):
    await message.answer(
        "Выберите один из вариантов:", reply_markup=await kb.start_support_inline()
    )


@router.callback_query(F.data == "monjaro_support_video")
async def monjaro_video(callback: CallbackQuery):
    global VIDEO_FILE_ID

    await callback.answer()
    await callback.message.delete()

    if VIDEO_FILE_ID:
        await callback.message.answer_video(
            video=VIDEO_FILE_ID,
            caption="Видео по установке регистратора Geely Monjaro",
            parse_mode="HTML",
        )
    else:
        video = FSInputFile(MONJARO_VIDEO_PATH)
        msg = await callback.message.answer_video(
            video=video,
            caption="Видео по установке регистратора Geely Monjaro",
            parse_mode="HTML",
        )
        VIDEO_FILE_ID = msg.video.file_id


@router.callback_query(F.data == "monjaro_support_doc")
async def monjaro_document(callback: CallbackQuery):
    global DOC_FILE_ID

    await callback.answer()
    await callback.message.delete()

    if DOC_FILE_ID:
        await callback.message.answer_document(
            document=DOC_FILE_ID,
            caption="PDF инструкция по мобильному приложению SkyCam",
            parse_mode="HTML",
        )
    else:
        doc = FSInputFile(MONJARO_DOC_PATH)
        msg = await callback.message.answer_document(
            document=doc,
            caption="PDF инструкция по мобильному приложению SkyCam",
            parse_mode="HTML",
        )
        DOC_FILE_ID = msg.document.file_id


# END OF SUPPORT COMMAND BLOCK


# START OF CONTACTS COMMAND BLOCK
@router.message(Command("contacts"))
async def contacts_start(message: Message):
    await message.answer(
        "Для связи с нами можете использовать эти способы:\n"
        f"Телефон - <a href = 'tel: {TEL_NUMBER}'>{TEL_NUMBER}</a>\n"
        f"Telegram - {TELEGRAMM_TAG}\n"
        f"Whatsapp - <a href={WHATSAPP_LINK}>{WHATSAPP_TEL}</a>\n"
        f"Email - <a href = 'mailto: {EMAIL}'>{EMAIL}</a>\n"
        f"Сайт - <a href={WEB_SITE_LINK}>{WEB_SITE_NAME}</a>",
        parse_mode="HTML",
    )


# END OF CONTACTS COMMAND BLOCK

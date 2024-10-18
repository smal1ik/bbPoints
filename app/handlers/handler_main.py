from aiogram import Router
from aiogram.filters.command import Command
from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload, encode_payload
from app.database.requests import *
from app.utils.state import User
from app.utils.utils import *
import app.keyboards.keyboard_main as kb

router_main = Router()


@router_main.message(Command('start'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    await state.set_state(User.start)
    args = command.args
    if args:
        ref = decode_payload(args)
        if ref == str(message.from_user.id):  # Своя же рефка
            ref = 0
        else:
            user_refs = await get_user(ref)  # Есть ли вообще в бд такой пользователь для рефки
            if not user_refs:
                ref = 0
    else:
        ref = 0

    user = await get_user(message.from_user.id)
    if not user:
        await message.answer('Приветственное сообщение')
        await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, int(ref))
    elif ref:
        await message.answer("Ты не можешь быть рефералом, тк бот уже запущен")

    ref = encode_payload(message.from_user.id)
    await message.answer('Меню', reply_markup=kb.get_menu_btn(ref))


@router_main.callback_query(F.data == 'menu')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.start)
    ref = encode_payload(callback.from_user.id)
    await callback.message.answer('Меню', reply_markup=kb.get_menu_btn(ref))


# ===========================================ЧЕК=========================================================
@router_main.callback_query(F.data == 'receipt')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.load_image_check)
    await callback.message.answer("Загрузи чёткую фотографию чека чтобы было видно куар-код",
                                  reply_markup=kb.single_menu_btn)


@router_main.message(User.load_image_check, F.photo)
async def answer_message(message: types.Message, state: FSMContext):
    await message.bot.download(file=message.photo[-1].file_id, destination=f'users_check/{message.from_user.id}.jpg')
    id_check = read_qrcode(message.from_user.id)
    if id_check:
        res = await get_check(id_check)
        if res:
            await message.answer("Чек уже загружали до этого\nПопробуй другой чек",
                                          reply_markup=kb.single_menu_btn)
        else:
            await add_check(id_check)

            # Функция, которая считает сколько баллов нужно добавить. Так же она работает с API ФНС.

            await message.answer("Отлично, ты заработала ХХ баллов")
            await state.set_state(User.start)
            ref = encode_payload(message.from_user.id)
            await message.answer('Меню', reply_markup=kb.get_menu_btn(ref))
    else:
        await message.answer("Не удалось распознать куар-код\nПопробуй ещё раз",
                             reply_markup=kb.single_menu_btn)


# ================================Проверить упоминание в посте===================================================
@router_main.callback_query(F.data == 'mention')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Перешли сюда пост из канала",
                                  reply_markup=kb.single_menu_btn)
    await state.set_state(User.wait_repost)


@router_main.message(User.wait_repost, F.forward_from_chat[F.type == "channel"].as_("channel"))
async def answer_message(message: types.Message, state: FSMContext):
    text = message.text.lower()
    id_post = message.forward_from_message_id
    id_channel = message.forward_from_chat.id
    channel = await get_channel(id_channel)
    if not channel:
        await add_channel(id_channel)
        count_post = 0
    else:
        count_post = channel.number_post
    post = await get_post(id_channel, id_post)

    if id_post <= 30:
        await message.answer("Маленькая группа, меньше 30 постов")
    elif bb_post_check(text):
        await message.answer("В посте нет упоминания")
    elif count_post >= 3:
        await message.answer("За неделю уже было принято 3 поста")
    elif post:
        await message.answer("Данный пост уже был принят")
    else:
        await message.answer("Пост принят")
        await add_post(id_channel, id_post)
        await add_number_post_channel(id_channel)

    await state.set_state(User.start)
    ref = encode_payload(message.from_user.id)
    await message.answer('Меню', reply_markup=kb.get_menu_btn(ref))

@router_main.message(User.wait_repost)
async def answer_message(message: types.Message, state: FSMContext):
    await message.answer('Нужно переслать сообщение из канала', reply_markup=kb.single_menu_btn)
# ===========================================Конкурс=========================================================

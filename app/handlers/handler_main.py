from datetime import timedelta

from aiogram.filters.command import Command
from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload, encode_payload
from arq import ArqRedis

from app.database.requests import *
from app.fns import api
from app.utils import copy
from app.utils.state import User
from app.utils.utils import *
import app.keyboards.keyboard_main as kb
from decouple import config

ID_CHANNEL = int(config('ID_CHANNEL'))
ID_CHAT = int(config('ID_CHAT'))
router_main = Router()


@router_main.message(Command('test'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id == message.chat.id:
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
            await bot.set_chat_menu_button(message.from_user.id, menu_button=kb.web_app_button)
            await message.answer(copy.start_msg)
            await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, int(ref))
        elif ref:
            await message.answer("Не могу начислить ВВ-баллы за твой переход по ссылке, так как бот уже был запущен тобой ранее 🔗")

        ref = encode_payload(message.from_user.id)
        await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))


@router_main.callback_query(F.data == 'menu')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.start)
    ref = encode_payload(callback.from_user.id)
    await callback.message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))

# ===========================================ПОДЕЛИТЬСЯ=========================================================
@router_main.callback_query(F.data == 'share')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    ref = encode_payload(callback.from_user.id)
    await callback.message.answer("Отправляй ссылку на бота лояльности BBCore своим друзьям и получай 20 ВВ-баллов за каждый запуск бота по твоей ссылке ✌🏻", reply_markup=kb.get_share_btn(ref))



# ===========================================ЧЕК=========================================================
@router_main.callback_query(F.data == 'receipt')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.load_image_check)
    await callback.message.answer(copy.check_start_msg,
                                  reply_markup=kb.single_menu_btn)


@router_main.message(User.load_image_check, F.photo)
async def answer_message(message: types.Message, state: FSMContext):
    await message.bot.download(file=message.photo[-1].file_id, destination=f'users_check/{message.from_user.id}.jpg')
    id_check = read_qrcode(message.from_user.id)
    if id_check:
        res = await get_check(id_check)
        if res:
            await message.answer("Этот чек уже был загружен! Попробуй прислать другой 🙌",
                                 reply_markup=kb.single_menu_btn)
        else:
            await add_check(id_check)

            # Функция, которая считает сколько баллов нужно добавить. Так же она работает с API ФНС.
            api.get_items_check()
            await message.answer("Отлично, ты заработала ХХ баллов")
            await state.set_state(User.start)
            ref = encode_payload(message.from_user.id)
            await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))
    else:
        await message.answer("Мне не удалось распознать QR-код, попробуй ещё раз 🔍",
                             reply_markup=kb.single_menu_btn)


# ================================Проверить упоминание в посте===================================================
@router_main.callback_query(F.data == 'mention')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(copy.mention_msg,
                                  reply_markup=kb.single_menu_btn)
    await state.set_state(User.wait_repost)


@router_main.message(User.wait_repost, F.forward_from_chat[F.type == "channel"].as_("channel"),
                     ((F.text) | (F.caption)))
async def answer_message(message: types.Message, state: FSMContext):
    if message.text:
        text = message.text.lower()
    else:
        text = message.caption.lower()
    id_post = message.forward_from_message_id
    id_channel = message.forward_from_chat.id
    channel = await get_channel(id_channel)
    if not channel:
        await add_channel(id_channel)
        count_post = 0
    else:
        count_post = channel.number_post
    post = await get_post(id_channel, id_post)
    # if id_post <= 30:
    #     await message.answer("Маленькая группа, меньше 30 постов")
    # elif bb_post_check(text):
    #     await message.answer("В посте нет упоминания")
    # elif count_post >= 3:
    #     await message.answer("За неделю уже было принято 3 поста")
    # elif post:
    #     await message.answer("Данный пост уже был принят")
    if id_post <= 30 or bb_post_check(text) or count_post >= 3 or post:
        await message.answer(copy.error_post_msg)
    else:
        await message.answer("Поздравляю! Ты заработала свои 20 ВВ-баллов за этот постик 💙")
        await add_post(id_channel, id_post)
        await add_number_post_channel(id_channel)
        api.add_points(message.from_user.id, 40)

    await state.set_state(User.start)
    ref = encode_payload(message.from_user.id)
    await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))


@router_main.message(User.wait_repost, ((F.text) | (F.caption)))
async def answer_message(message: types.Message, state: FSMContext):
    await message.answer('Нужно переслать сообщение из канала', reply_markup=kb.single_menu_btn)


# ===========================================Конкурс=========================================================
@router_main.callback_query((F.data == 'contest') | (F.data == 'back'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.start)
    btns, check = await kb.get_sn_btn(callback.from_user.id)
    if check:
        msg = copy.sn_msg
    else:
        msg = copy.new_sn_msg

    await callback.message.answer(msg, reply_markup=btns)


@router_main.callback_query(F.data.contains('my'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    sn = callback.data.split('_')[1]
    link = (await get_social_network(callback.from_user.id, sn)).social_network_link
    msg = f"Привязанный аккаунт:\n{link}"
    await state.set_data({'link': link, 'name_sn': sn})
    await callback.message.answer(msg, reply_markup=kb.sn_link_btn, disable_web_page_preview=True)


@router_main.callback_query(F.data == 'disconnection')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    msg = f"Ты уверена, что хочешь отвязать аккаунт? 廊"
    await callback.message.answer(msg, reply_markup=kb.sure_btn)


@router_main.callback_query(F.data == 'yes_sure')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    name_sn = (await state.get_data())['name_sn']
    await del_social_networks(callback.from_user.id, name_sn)
    btns, check = await kb.get_sn_btn(callback.from_user.id)
    if check:
        msg = copy.sn_msg
    else:
        msg = copy.new_sn_msg

    await callback.message.answer(msg, reply_markup=btns)


@router_main.callback_query(F.data.contains('connect'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    sn = callback.data.split('_')[1]
    msg = f"Кидай ссылку на свой аккаунт 🔗"
    await callback.message.answer(msg, reply_markup=kb.single_menu_btn)
    await state.set_state(User.wait_link)
    await state.set_data({"connect": sn})


@router_main.message(User.wait_link)
async def answer_message(message: types.Message, state: FSMContext):
    await state.set_state(User.start)
    sn = (await state.get_data())['connect']
    link = message.text.replace('https://', '')
    result = await search_sn_link(link)
    if not sn.lower() in link.lower():
        msg = """Ссылка не подходит!\nУбедись, что это ссылка на твой аккаунт в соцсети, которую ты изначально выбрала⛓️‍💥"""
        await message.answer(msg)
    elif result:
        msg = """Ссылка не подходит!\nУбедись, чтобы эта ссылка не была привязана с другой страницы⛓️‍💥"""
        await message.answer(msg)
    else:
        await add_social_network(message.from_user.id, sn, link)
        msg = f"Супер! Ты успешно привязала свой аккаунт ко мне 甆"
        await message.answer(msg)

    btns, check = await kb.get_sn_btn(message.from_user.id)

    if check:
        msg = copy.sn_msg
    else:
        msg = copy.new_sn_msg

    await message.answer(msg, reply_markup=btns)


@router_main.callback_query(F.data == 'flood')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.wait_link_video)
    msg = "Ура! Очень рад за тебя 💋\n\nПришли мне ссылку на видео, его проверят и в случае, если всё супер — начислят тебе баллы 😮‍💨"
    await callback.message.answer(msg, reply_markup=kb.single_back_btn)


@router_main.message(User.wait_link_video)
async def answer_message(message: types.Message, state: FSMContext, bot: Bot):
    await state.set_state(User.start)
    data_state = await state.get_data()
    sn = data_state['name_sn']
    link = data_state['link']
    link_video = message.text.replace('https://', '')
    result = await search_link_video(link_video)
    if not sn.lower() in link_video.lower():
        msg = """Упс! Видео не засчитано😭\n\nПроверь, что ты прислала ссылку на видео из выбранной ранее соцсети 🔍"""
        await message.answer(msg)
    elif result:
        msg = """Упс! Видео не засчитано😭\n\nПроверь, чтобы эта ссылка ещё не была использована ранее 🔍"""
        await message.answer(msg)
    else:
        await add_link_video(message.from_user.id, link_video)
        msg = f"Твоё видео проходит проверку, нужно немного подождать 羅"
        await message.answer(msg)

        msg = f"""
Видео {sn} на проверку

Пользователь:
{message.from_user.id}
{message.from_user.first_name}
{message.from_user.username}
Ссылка на {link}

{link_video}   
        """

        await bot.send_message(-4585659208,
                               msg,
                               reply_markup=kb.get_points_btn(message.from_user.id),
                               disable_web_page_preview=True)

    btns, check = await kb.get_sn_btn(message.from_user.id)

    msg = copy.sn_msg

    await message.answer(msg, reply_markup=btns)


@router_main.callback_query(F.data.contains('points'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, points, tg_id = callback.data.split('__')
    await callback.message.edit_reply_markup()
    if points == '0':
        await bot.send_message(tg_id, copy.cancel_msg)
    else:
        msg = f"Молодец! Тебе уже зачислили баллы за этот видосик, можешь проверять 😈"
        await bot.send_message(tg_id, msg)
        api.add_points(int(tg_id), int(points))


# ===========================================Комментарии из чата========================================================


@router_main.channel_post(F.chat.id == ID_CHANNEL)
async def answer_message(message: types.Message):
    print("Новый пост")
    add_new_id_post(message.message_id)


@router_main.message(F.chat.id == ID_CHAT, F.text, F.reply_to_message, F.from_user.is_bot == False)  # ID ЧАТА
async def answer_message(message: types.Message, state: FSMContext, bot: Bot, arqredis: ArqRedis):
    user = await get_user(message.from_user.id)
    if (message.reply_to_message.forward_origin.message_id in list_channel_message) and user and not user.send_comment:
        await bot.send_message(message.from_user.id, copy.comment_msg)
        api.add_points(message.from_user.id, 10)
        await user_send_comment(message.from_user.id)
        await arqredis.enqueue_job(
            'reset_send_comment', _defer_by=timedelta(hours=1), telegram_id=message.from_user.id
        )
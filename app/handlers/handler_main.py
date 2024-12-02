from datetime import timedelta, datetime

from aiogram.filters.command import Command
from aiogram import types, F, Router, Bot, BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile, FSInputFile
from aiogram.utils.deep_linking import create_start_link, decode_payload, encode_payload
from arq import ArqRedis

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from app.database.requests import *
from app.fns import fns_api
from app.utils import copy
from app.utils.state import User
from app.utils.utils import *
import app.keyboards.keyboard_main as kb
from decouple import config

ID_CHANNEL = int(config('ID_CHANNEL'))
ID_CHAT = int(config('ID_CHAT'))
synonyms = {'яблоко': 'Золотое Яблоко',
            'лэтуаль': 'Лэтуаль',
            'магнит': 'Магнит',
            'рив': 'Рив Гош',
            'ozon': 'OZON',
            'wildberries': 'wildberries',
            'купер': 'купер',
            'мегамеркет': 'мегамеркет',
            None: 'Другие магазины'}
router_main = Router()

class AntiManyReply(BaseMiddleware):
    def __init__(self) -> None:
        self.cache = set()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.id in self.cache:
            return
        self.cache.add(event.chat.id)
        result = await handler(event, data)
        self.cache.remove(event.chat.id)
        return result

router_main.message.middleware(AntiManyReply())


@router_main.message(Command('statistics'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    stats = await get_analytics()
    msg = f"""Всего пользователей: {stats[0]}
Пришедших по рефералке: {stats[1]}
Пришедших из sociallead: {stats[2]}
Засчитано комментариев: {stats[3]}
Засчитано постов: {stats[4]}
Всего постов скинуто: {stats[5]}
Сколько аккаунтов каждого вида привязали
{stats[6][0][0]}: {stats[6][0][1]}
{stats[6][1][0]}: {stats[6][1][1]}
{stats[6][2][0]}: {stats[6][2][1]}
{stats[6][3][0]}: {stats[6][3][1]}
Сколько видео залетело по каждой соц сети
{stats[7][0][0]}: {stats[7][0][1]}
{stats[7][1][0]}: {stats[7][1][1]}
{stats[7][2][0]}: {stats[7][2][1]}

Сколько чеков загружено всего: {stats[8]}
Сколько чеков по магазинам
{synonyms[stats[9][0][0]]}: {stats[9][0][1]}
{synonyms[stats[9][1][0]]}: {stats[9][1][1]}
{synonyms[stats[9][2][0]]}: {stats[9][2][1]}
{synonyms[stats[9][3][0]]}: {stats[9][3][1]}
{synonyms[stats[9][4][0]]}: {stats[9][4][1]}
{synonyms[stats[9][5][0]]}: {stats[9][5][1]}
{synonyms[stats[9][6][0]]}: {stats[9][6][1]}
{synonyms[stats[9][7][0]]}: {stats[9][7][1]}
{synonyms[stats[9][8][0]]}: {stats[9][8][1]}
Сумма товаров бб по всем чекам: {stats[10]}
Сколько баллов в общем засчитали за чеки: {stats[11]}
"""
    await message.answer(msg)


@router_main.message(Command("info_user"))
async def cmd_start(message: types.Message, state: FSMContext):
    _, user_id = message.text.split()
    logs = (await info_user(int(user_id)))[0]
    msg = ""
    for log in logs:
        msg += f"{log[0]}: {log[1]}\n"
    await message.answer(msg[:-1])
@router_main.message(Command('filter_account'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    await message.answer("Скинь ссылку, которую необходимо заблокировкать\nДля выхода напиши /end")
    await state.set_state(User.admin)

@router_main.message(Command('end'))
async def message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    ref = encode_payload(message.from_user.id)
    await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))
    await state.set_state(User.start)


@router_main.message(User.admin)
async def answer_message(message: types.Message, state: FSMContext):
    link = message.text.replace('https://', '')
    try:
        await add_social_network(message.from_user.id, "Bloger", link)
        await message.answer("Ссылка добавлена, можешь продолжать скидывать\nДля выхода напиши /end")
    except:
        await message.answer("Что то пошло не так, напиши админу")
        await state.set_state(User.start)
        ref = encode_payload(message.from_user.id)
        await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))


@router_main.message(Command('new_list_posts'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    posts_id = get_id_posts()
    posts_id = [str(elem) for elem in posts_id]
    await message.answer(" ".join(posts_id))
    await state.set_state(User.admin_new_posts)


@router_main.message(User.admin_new_posts)
async def message(message: types.Message, state: FSMContext):
    posts_id = message.text
    rewrite_id_posts(posts_id)
    ref = encode_payload(message.from_user.id)
    await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))
    await state.set_state(User.start)


@router_main.message(Command('start'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id == message.chat.id:
        await state.set_state(User.start)
        args = command.args
        ref = 0
        if args and len(args) != 24:
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
            if args and len(args) == 24 and ref == 0:
                ref = 1
                api.postback(args)
            await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, int(ref))
        elif ref:
            await message.answer("Не могу начислить ВВ-баллы за твой переход по ссылке, так как бот уже был запущен тобой ранее 🔗")

        ref = encode_payload(message.from_user.id)
        await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref), menu_button=kb.web_app_button)


@router_main.callback_query(F.data == 'new_start')
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if callback.from_user.id == callback.message.chat.id:
        await state.set_state(User.start)
        ref = 0

        user = await get_user(callback.from_user.id)

        if not user:
            await bot.set_chat_menu_button(callback.from_user.id, menu_button=kb.web_app_button)
            await add_user(callback.from_user.id, callback.from_user.first_name, callback.from_user.username, int(ref))
        elif ref:
            await callback.message.answer("Не могу начислить ВВ-баллы за твой переход по ссылке, так как бот уже был запущен тобой ранее 🔗")

        ref = encode_payload(callback.from_user.id)
        await callback.message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))


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
    count_check = (await state.get_data())
    if not count_check.get('count_check'):
        count_check = 0
    else:
        count_check = count_check.get('count_check')
    await message.bot.download(file=message.photo[-1].file_id, destination=f'users_check/{message.from_user.id}.jpg')
    id_check, data_check = read_qrcode(message.from_user.id)

    if id_check:
        dead_date = datetime.strptime("20241105", "%Y%m%d")
        check_date = datetime.strptime(id_check[0:8], "%Y%m%d")
        if (check_date - dead_date).days < 0:
            await message.answer(
                "Упс, кажется, твой чек слишком старый 💔 Отправь, пожалуйста, свежий чек, чтобы мы смогли распознать его ✍🏻",
                reply_markup=kb.single_menu_btn)
            return
        res = await get_check(id_check)
        if res:
            await message.answer("Этот чек уже был загружен! Попробуй прислать другой 🙌",
                                 reply_markup=kb.single_menu_btn)
        else:
            # Функция, которая считает сколько баллов нужно добавить. Так же она работает с API ФНС.
            items, retail_place = fns_api.get_items_check(data_check)
            if items is None:
                await message.answer("Ох, кажется, очень много запросов на проверки чеки!\n\nСегодня мы не можем принять твой чек, попробуй отправить его завтра 🫶",
                                     reply_markup=kb.single_menu_btn)
            else:
                n_point, sum_bb = check_items(items)
                if n_point is None:
                    await add_check(id_check)
                    await message.answer("В этом чеке нет товаров от Beauty Bomb 😔 Попробуй прислать другой чек!",
                                         reply_markup=kb.single_menu_btn)
                else:
                    api.add_points(message.from_user.id, n_point)
                    await insert_point_log(message.from_user.id, "чек", n_point, check_id=id_check)
                    retail_name = get_name_retail(retail_place.lower())
                    await add_check(id_check, retail_name, sum_bb, n_point)
                    await message.answer("Просто супер! Поздравляю, твоя копилка ВВ-баллов пополнилась 🥳")
                    await state.set_state(User.start)
                    ref = encode_payload(message.from_user.id)
                    await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))
                    await state.set_data({'count_check': 0})
    else:
        count_check += 1
        await state.set_data({'count_check': count_check})

        if count_check >= 3:
            await message.answer("Упс! Кажется, я не могу распознать информацию на твоём чеке 🥲\n\nНапиши, пожалуйста, сообщение со всеми данными из чека по инструкции далее❤️")
            await message.answer_photo(FSInputFile("users_check/check_example.png"))

            await message.answer("Укажи точную дату покупки и время покупки (дд.мм.гг чч:мм) 🕰")

            await state.set_state(User.check_date)
            await state.set_data({'count_check': 0})
        else:
            await message.answer("Мне не удалось распознать QR-код, попробуй ещё раз 🔍",
                                 reply_markup=kb.single_menu_btn)

@router_main.message(User.check_date, F.text)
async def answer_message(message: types.Message, state: FSMContext):
    date_text = message.text.split()
    if len(date_text) != 2 or len(date_text[1].split(':')) != 2:
        await message.answer("Неверный формат")
    else:
        day, month, year = date_text[0].split('.')
        date = f"20{year}-{month}-{day}T{date_text[1]}:00"

        dead_date = datetime.strptime("20241105", "%Y%m%d")
        check_date = datetime.strptime(date[0:10], "%Y-%m-%d")
        if (check_date - dead_date).days < 0:
            await message.answer(
                "Упс, кажется, твой чек слишком старый 💔 Отправь, пожалуйста, свежий чек, чтобы мы смогли распознать его ✍🏻",
                reply_markup=kb.single_menu_btn)
            return

        await state.set_data({"data_check": [date]})
        await message.answer("Укажи сумма покупки. Обязательно прописывай точную сумму с копейками через точку «.» 💕")
        await state.set_state(User.check_summ)


@router_main.message(User.check_summ, F.text)
async def answer_message(message: types.Message, state: FSMContext):
    sum_text = message.text
    if not '.' in sum_text:
        sum_text += ".00"
    data_check = (await state.get_data())['data_check']
    data_check.append(sum_text)
    await state.set_data({'data_check': data_check})
    await message.answer("Укажи следующие данные: ФН")
    await state.set_state(User.check_fn)

@router_main.message(User.check_fn, F.text)
async def answer_message(message: types.Message, state: FSMContext):
    fn = message.text
    data_check = (await state.get_data())['data_check']
    data_check.append(fn)
    await state.set_data({'data_check': data_check})
    await message.answer("Укажи следующие данные: ФД")
    await state.set_state(User.check_fd)

@router_main.message(User.check_fd, F.text)
async def answer_message(message: types.Message, state: FSMContext):
    fd = message.text
    data_check = (await state.get_data())['data_check']
    data_check.append(fd)
    await state.set_data({'data_check': data_check})
    await message.answer("Укажи следующие данные: ФП")
    await state.set_state(User.check_fs)

@router_main.message(User.check_fs, F.text)
async def answer_message(message: types.Message, state: FSMContext):
    fs = message.text
    data_check = (await state.get_data())['data_check']
    data_check.append(fs)
    data_check.append('1')
    id_check = data_check[0].replace('-', '').replace(':', '')[:-2] + data_check[3] + data_check[4]
    res = await get_check(id_check)
    if res:
        await message.answer("Этот чек уже был загружен! Попробуй прислать другой 🙌",
                             reply_markup=kb.single_menu_btn)
    else:
        items, retail_place = fns_api.get_items_check(data_check)
        if items is None:
            await message.answer("Мнe не удалось найти чек, возможно была допущена ошибка 🔍",
                                 reply_markup=kb.single_menu_btn)
        else:
            n_point, sum_bb = check_items(items)
            if n_point is None:
                await add_check(id_check)
                await message.answer("В этом чеке нет товаров от Beauty Bomb 😔 Попробуй прислать другой чек!",
                                     reply_markup=kb.single_menu_btn)
            else:
                api.add_points(message.from_user.id, n_point)
                await insert_point_log(message.from_user.id, "чек", n_point, check_id=id_check)
                retail_name = get_name_retail(retail_place.lower())
                await add_check(id_check, retail_name, sum_bb, n_point)
                await message.answer("Просто супер! Поздравляю, твоя копилка ВВ-баллов пополнилась 🥳")
    await state.set_state(User.start)
    ref = encode_payload(message.from_user.id)
    await message.answer(copy.menu_msg, reply_markup=kb.get_menu_btn(ref))

# ================================Проверить упоминание в посте===================================================
@router_main.callback_query(F.data == 'mention')
async def answer_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(copy.mention_msg,
                                  reply_markup=kb.single_menu_btn)
    await state.set_state(User.wait_repost)


@router_main.message(User.wait_repost, F.forward_from_chat[F.type == "channel"].as_("channel"),
                     ((F.text) | (F.caption)))
async def answer_message(message: types.Message, state: FSMContext):
    await state.set_state(User.start)
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
        if not channel.tg_id:
            await update_tg_id_channel(id_channel, message.from_user.id)
        count_post = channel.number_post
    post = await get_post(id_channel, id_post)
    if id_post < 30:
        await message.answer(copy.error_post_msg)
        await message.answer("Не могу начислить ВВ-баллы за этот пост, так как пост с упоминанием должен быть минимум 30-м на твоём канале 🥺💙")
    elif bb_post_check(text):
        await message.answer("Не могу начислить ВВ-баллы за этот пост, ведь в нём нет упоминания Beauty Bomb 🥹")
    elif count_post >= 3:
        await message.answer("Не могу начислить ВВ-баллы за этот пост, так как ты прислала уже три поста на этой неделе 🥺\nПришли этот пост на следующей неделе, чтобы получить 20 ВВ-баллов!")
    elif post:
        await message.answer("Не могу начислить ВВ-баллы за этот пост, так как они уже начислены за него другому пользователю 🥺")
    else:
        await message.answer("Поздравляю! Ты заработала свои 20 ВВ-баллов за этот постик 💙")
        await add_post(id_channel, id_post)
        await add_number_post_channel(id_channel)
        api.add_points(message.from_user.id, 20)
        await insert_point_log(message.from_user.id, "пост", 20, channel_id=id_channel)

    await add_count_channel_post(id_channel)
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
    msg = f"Ты уверена, что хочешь отвязать аккаунт? 🤔"
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
        msg = f"Супер! Ты успешно привязала свой аккаунт ко мне 🩷"
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
        msg = f"Твоё видео проходит проверку, нужно немного подождать ⌛️"
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

        await bot.send_message(-1002475070676,
                               msg,
                               reply_markup=kb.get_points_btn(message.from_user.id, sn),
                               disable_web_page_preview=True)

    btns, check = await kb.get_sn_btn(message.from_user.id)

    msg = copy.sn_msg

    await message.answer(msg, reply_markup=btns)


@router_main.callback_query(F.data.contains('points'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, sn, points, tg_id = callback.data.split('__')
    await callback.message.edit_reply_markup()
    if points == '0':
        await bot.send_message(tg_id, copy.cancel_msg)
    else:
        msg = f"Молодец! Тебе уже зачислили баллы за этот видосик, можешь проверять 😈"
        await update_number_accept_video(sn)
        await bot.send_message(tg_id, msg)
        api.add_points(int(tg_id), int(points))
        await insert_point_log(tg_id, "видео", int(points))


# ===========================================Комментарии из чата========================================================


@router_main.channel_post(F.chat.id == ID_CHANNEL)
async def answer_message(message: types.Message):
    if not message.pinned_message and (message.text or message.caption):
        print("Новый пост")
        add_new_id_post(message.message_id)


@router_main.message(F.chat.id == ID_CHAT, F.text, F.reply_to_message, F.from_user.is_bot == False)  # ID ЧАТА
async def answer_message(message: types.Message, state: FSMContext, bot: Bot, arqredis: ArqRedis):
    try:
        print(list_channel_message)
        user = await get_user(message.from_user.id)
        if message.reply_to_message.forward_origin and (message.reply_to_message.forward_origin.message_id in list_channel_message) and user and not user.send_comment:
            print(message.reply_to_message.forward_origin.message_id)
            await bot.send_message(message.from_user.id, copy.comment_msg)
            api.add_points(message.from_user.id, 10)
            await insert_point_log(message.from_user.id, "комментарий", 10)
            await user_send_comment(message.from_user.id)
            await arqredis.enqueue_job(
                'reset_send_comment', _defer_by=timedelta(hours=1), telegram_id=message.from_user.id
            )
    except Exception as e:
       print(e)

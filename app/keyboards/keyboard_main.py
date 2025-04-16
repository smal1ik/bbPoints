from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

from app.database.requests import get_social_networks

from decouple import config

ID_POST_REVIEW = int(config('ID_POST_REVIEW'))

sn_list = ['Likee', 'TikTok', 'VK']

web_app_info = types.WebAppInfo(url="https://beauty-bomb-app.ru/your-web-app/?action=wptelegram_login_webapp&redirect_to=https://beauty-bomb-app.ru")
web_app_button = types.menu_button_web_app.MenuButtonWebApp(web_app=web_app_info, text='START', type='web_app')



sn_link_btn = InlineKeyboardBuilder()
sn_link_btn.row(
    types.InlineKeyboardButton(
        text="Моё видео залетело!",
        callback_data="flood")
)
sn_link_btn.row(
    types.InlineKeyboardButton(
        text="Отвязать аккаунт",
        callback_data="disconnection")
)
sn_link_btn.row(
    types.InlineKeyboardButton(
        text="Назад",
        callback_data="back")
)
sn_link_btn = sn_link_btn.as_markup()


sure_btn = InlineKeyboardBuilder()
sure_btn.row(
    types.InlineKeyboardButton(
        text="Да",
        callback_data="yes_sure")
)
sure_btn.row(
    types.InlineKeyboardButton(
        text="Назад",
        callback_data="back")
)
sure_btn = sure_btn.as_markup()


review_btn = InlineKeyboardBuilder()
review_btn.row(
    types.InlineKeyboardButton(
        text="Написать отзыв",
        url=f'https://t.me/beautybomb/{ID_POST_REVIEW}')
)
review_btn.row(
    types.InlineKeyboardButton(
        text="В меню",
        callback_data="menu")
)
review_btn = review_btn.as_markup()


def get_menu_btn(ref: str):
    menu_btn = InlineKeyboardBuilder()
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Загрузить чек",
            callback_data="receipt")
    )
    # menu_btn.row(
    #     types.InlineKeyboardButton(
    #         text="Фото у стенда",
    #         callback_data="photo_stend"
    #     )
    # )
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Проверить упоминание в посте",
            callback_data="mention")
    )
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Конкурс #BBCore",
            callback_data="contest")
    )
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Поделиться ботом",
            callback_data="share")
    )
    # menu_btn.row(
    #     types.InlineKeyboardButton(
    #         text="Написать отзыв",
    #         callback_data="review")
    # )
    menu_btn = menu_btn.as_markup()
    return menu_btn


def get_share_btn(ref: str):
    url = f"t.me/beauty_bomb_bot?start={ref}"
    share_btn = InlineKeyboardBuilder()
    share_btn.row(
        types.InlineKeyboardButton(
            text="Поделиться ботом",
            url=f'https://telegram.me/share/url?url={url}')
    )
    share_btn.row(
        types.InlineKeyboardButton(
            text="В меню",
            callback_data="menu")
    )
    share_btn = share_btn.as_markup()
    return share_btn


single_menu_btn = InlineKeyboardBuilder()
single_menu_btn.row(
    types.InlineKeyboardButton(
    text="В меню",
    callback_data="menu")
)
single_menu_btn = single_menu_btn.as_markup()

single_back_btn = InlineKeyboardBuilder()
single_back_btn.row(
    types.InlineKeyboardButton(
    text="Назад",
    callback_data="back")
)
single_back_btn = single_back_btn.as_markup()


async def get_check_photo_link_btn(tg_id):
    check_photo_link_btn = InlineKeyboardBuilder()
    check_photo_link_btn.row(
        types.InlineKeyboardButton(
            text="Засчитать",
            callback_data=f"photolink__accept__{tg_id}")
    )
    check_photo_link_btn.row(
        types.InlineKeyboardButton(
            text="Отказ",
            callback_data=f"photolink__cancel__{tg_id}")
    )
    check_photo_link_btn = check_photo_link_btn.as_markup()
    return check_photo_link_btn

async def get_sn_btn(tg_id: int):
    check = False
    result = await get_social_networks(tg_id)
    social_networks = []
    for elem in result:
        social_networks.append(elem.social_network)
    sn_btn = InlineKeyboardBuilder()
    for elem in sn_list:
        if elem in social_networks:
            sn_btn.row(
                types.InlineKeyboardButton(
                    text=f"Мой {elem}",
                    callback_data=f"my_{elem}")
            )
            check = True
        else:
            sn_btn.row(
                types.InlineKeyboardButton(
                    text=f"Привязать {elem}",
                    callback_data=f"connect_{elem}")
            )

    sn_btn.row(
        types.InlineKeyboardButton(
            text="В меню",
            callback_data="menu")
    )
    sn_btn = sn_btn.as_markup()
    return sn_btn, check

list_point = ['100', '200', '400', '800', '1500']
def get_points_btn(tg_id: int, sn: str):
    points_btn = InlineKeyboardBuilder()
    for elem in list_point:
        points_btn.row(
            types.InlineKeyboardButton(
                text=elem,
                callback_data=f"points__{sn}__{elem}__{tg_id}")
        )
    points_btn.row(
        types.InlineKeyboardButton(
            text='Отказ',
            callback_data=f"points__{sn}__0__{tg_id}")
    )
    points_btn = points_btn.as_markup()
    return points_btn


def get_check_robot_btn(ref):
    check_robot_btn = InlineKeyboardBuilder()
    check_robot_btn.row(
        types.InlineKeyboardButton(
            text="Я не робот",
            callback_data=f"not_robot_{ref}")
    )
    check_robot_btn = check_robot_btn.as_markup()
    return check_robot_btn

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

from app.database.requests import get_social_networks
sn_list = ['Likee', 'TikTok', 'VK', 'Instagram']

web_app_info = types.WebAppInfo(url="https://t.me/beauty_bomb_bot/BeautyBombApp")
web_app_button = types.menu_button_web_app.MenuButtonWebApp(web_app=web_app_info, text='START', type='web_app')



sn_link_btn = InlineKeyboardBuilder()
sn_link_btn.row(
    types.InlineKeyboardButton(
        text="ВИДО ЗАЛИТЕЛО!!!",
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


def get_menu_btn(ref: str):
    text = "Присоединяйся в бота"
    menu_btn = InlineKeyboardBuilder()
    # menu_btn.row(
    #     types.InlineKeyboardButton(
    #         text="Загрузить чек",
    #         callback_data="receipt")
    # )
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Проверить упоминание в посте",
            callback_data="mention")
    )
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Конкурс",
            callback_data="contest")
    )
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Поделиться ботом",
            url=f'https://t.me/share/url?url=t.me/smallik1_bot?start={ref}&text={text}')
    )
    menu_btn = menu_btn.as_markup()
    return menu_btn


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
def get_points_btn(tg_id: int, link_video):
    points_btn = InlineKeyboardBuilder()
    for elem in list_point:
        points_btn.row(
            types.InlineKeyboardButton(
                text=elem,
                callback_data=f"points__{elem}__{tg_id}__{link_video}")
        )
    points_btn.row(
        types.InlineKeyboardButton(
            text='Отказ',
            callback_data=f"points__0__{tg_id}__{link_video}")
    )
    points_btn = points_btn.as_markup()
    return points_btn

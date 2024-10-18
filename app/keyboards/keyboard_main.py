from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def get_menu_btn(ref: str):
    menu_btn = InlineKeyboardBuilder()
    menu_btn.row(
        types.InlineKeyboardButton(
            text="Загрузить чек",
            callback_data="receipt")
    )
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
            url=f'https://t.me/share/url?url=t.me/smallik1_bot?start={ref}\n\nПрисоединяйся в бота')
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

# link_SN_btn = InlineKeyboardBuilder()
# link_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="Привязать Likee",
#     callback_data="likee")
# )
# link_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="Привязать TikTok",
#     callback_data="tiktok")
# )
# link_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="Привязать ВК",
#     callback_data="vk")
# )
# link_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="Привязать Instagram",
#     callback_data="instagram")
# )
# link_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="В меню",
#     callback_data="menu")
# )
# link_SN_btn = link_SN_btn.as_markup()

# my_SN_btn = InlineKeyboardBuilder()
# my_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="Мой Likee",
#     callback_data="likee")
# )
# my_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="Мой TikTok",
#     callback_data="tiktok")
# )
# my_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="мой ВК",
#     callback_data="vk")
# )
# my_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="мой Instagram",
#     callback_data="instagram")
# )
# my_SN_btn.row(
#     types.InlineKeyboardButton(
#     text="В меню",
#     callback_data="menu")
# )
# my_SN_btn = my_SN_btn.as_markup()
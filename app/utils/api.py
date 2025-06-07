import requests
import re
from app.database.requests import active_user, insert_point_log, get_current_daily_quests, get_user, \
    add_count_daily_comments, user_set_daily, count_number_completed_quest

url = "https://beauty-bomb-app.ru/wp-json/games/v1/update_points/"


async def add_points(telegram_id: int, points: int, type_quest: int = 0) -> None:
    if type_quest != 0:
        current_daily = await get_current_daily_quests()
        if current_daily and type_quest == current_daily.type_quest:
            user = await get_user(telegram_id)
            if user and not user.daily_check:
                if type_quest == 1:
                    number_comment = int(re.findall(r'\d+', current_daily.name_quest)[0])
                    if number_comment == user.count_daily_comment + 1:
                        points += 100
                        await user_set_daily(telegram_id)
                        await count_number_completed_quest()
                    await add_count_daily_comments(telegram_id)

                else:
                    points += 100
                    await user_set_daily(telegram_id)
                    await count_number_completed_quest()
    print(points)
    data = {
        'user': str(telegram_id),
        'points': points
    }
    response = requests.post(url=url, data=data)
    return response

def postback(clickid):
    url = f"https://offers-socialjet-cpa.affise.com/postback?clickid={clickid}"
    response = requests.get(url=url)
    return response.status_code

async def add_refs(tg_id, user_refs):
    await add_points(user_refs, 20, 3)
    await add_points(tg_id, 20)
    await active_user(user_refs)
    await insert_point_log(user_refs, "рефка", 20)
    await insert_point_log(tg_id, "рефка", 20)

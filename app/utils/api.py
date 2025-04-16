import requests

from app.database.requests import active_user, insert_point_log

url = "https://beauty-bomb-app.ru/wp-json/games/v1/update_points/"


async def add_points(telegram_id: int, points: int) -> None:
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
    await add_points(user_refs, 20)
    await add_points(tg_id, 20)
    await active_user(user_refs)
    await insert_point_log(user_refs, "рефка", 20)
    await insert_point_log(tg_id, "рефка", 20)

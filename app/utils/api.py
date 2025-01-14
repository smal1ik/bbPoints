import requests

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

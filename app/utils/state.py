from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from decouple import config
class User(StatesGroup):
    start = State()
    load_image_check = State()
    wait_repost = State()
    wait_link = State()
    wait_link_video = State()
    admin = State()
    end = State()

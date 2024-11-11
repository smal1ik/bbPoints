from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from decouple import config
class User(StatesGroup):
    start = State()
    load_image_check = State()
    wait_repost = State()
    wait_link = State()
    wait_link_video = State()
    check_date = State()
    check_summ = State()
    check_fn = State()
    check_fd = State()
    check_fs = State()
    admin = State()
    end = State()

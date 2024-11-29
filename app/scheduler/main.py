from datetime import timedelta

from aiogram import Bot
from arq import cron
from arq.connections import RedisSettings, ArqRedis
from decouple import config as env_config
from sqlalchemy import BigInteger

from app.database.requests import user_reset_send_comment, reset_all_channel


async def startup(ctx):
    ctx['bot'] = Bot(token=env_config('BOT_TOKEN'))


async def shutdown(ctx):
    await ctx['bot'].session.close()


async def reset_send_comment(ctx, telegram_id):
    await user_reset_send_comment(telegram_id)


async def reset_post(ctx):
    print("Сброс всем отправленных постов")
    await reset_all_channel()

class workersettings:
    max_tries = 3
    redis_settings = RedisSettings(host='185.247.185.138', port=6379, password='356211kKmM', database=1, username='default')
    on_startup = startup
    on_shutdown = shutdown
    allow_abort_jobs = True
    functions = [reset_send_comment, reset_post,]
    cron_jobs = [
        cron(reset_post, minute=0, hour=0, day=None, month=None, weekday=0)
    ]
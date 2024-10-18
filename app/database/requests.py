from app.database.models import User, async_session, Point, SocialNetwork, Check, Channel, Post
from sqlalchemy import select, BigInteger, update, delete, func


async def add_user(tg_id: BigInteger, first_name: str, username: str, user_refs: BigInteger):
    """
    Функция добавляет пользователя в БД
    """
    async with async_session() as session:
        if not first_name:
            first_name = 'None'
        if not username:
            username = 'None'
        session.add(User(tg_id=tg_id, first_name=first_name, username=username, user_refs=user_refs))
        session.add(Point(tg_id=tg_id))
        await session.commit()

        #ПОМЕНЯТЬ НА АПИ ОТ ВОЛОДИ
        if user_refs:
            await add_points(user_refs, 5)


async def add_points(tg_id: BigInteger, n_points):
    """
        Функция добавляет n баллов пользователю
    """
    async with async_session() as session:
        result = await session.scalar(select(Point).where(Point.tg_id == tg_id))

        await session.execute(update(Point).where(Point.tg_id == tg_id).values(
            number_points=result.number_points + n_points)
        )
        await session.commit()


async def get_user(tg_id: BigInteger):
    """
    Получаем пользователя по tg_id
    """
    async with async_session() as session:
        tg_id = int(tg_id)
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
        return result


async def add_check(check_id: str):
    """
    Функция добавляет чек в БД
    """
    async with async_session() as session:
        session.add(Check(check_id=check_id))
        await session.commit()


async def get_check(check_id: str):
    """
        Получаем чек по check_id
    """
    async with async_session() as session:
        result = await session.scalar(select(Check).where(Check.check_id == check_id))
    return result


async def add_channel(channel_id: BigInteger):
    async with async_session() as session:
        session.add(Channel(channel_id=channel_id))
        await session.commit()


async def add_number_post_channel(channel_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(Channel).where(Channel.channel_id == channel_id))
        await session.execute(update(Channel).where(Channel.channel_id == channel_id).values(
            number_post=result.number_post + 1)
        )
        await session.commit()


async def get_channel(channel_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(Channel).where(Channel.channel_id == channel_id))
    return result


async def add_post(channel_id: BigInteger, post_id: BigInteger):
    async with async_session() as session:
        session.add(Post(channel_id=channel_id, post_id=post_id))
        await session.commit()

async def get_post(channel_id: BigInteger, post_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(Post).where(Post.channel_id == channel_id, Post.post_id == post_id))
    return result

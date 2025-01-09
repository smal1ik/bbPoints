from app.database.models import User, async_session, Point, SocialNetwork, Check, Channel, Post, LinkVideo, \
    NumberAcceptVideo, PointsLog, LinkPhoto
from sqlalchemy import select, BigInteger, update, delete, func

from app.utils import api

async def insert_point_log(tg_id: BigInteger, from_points: str, number_points: int,
                           channel_id: BigInteger = 0, check_id: str = ''):

    async with async_session() as session:
        session.add(PointsLog(tg_id=tg_id, from_points=from_points, number_points=number_points,
                              channel_id=channel_id, check_id=check_id))

        await session.commit()

async def add_user(tg_id: BigInteger, first_name: str, username: str, user_refs: BigInteger):
    """
    Функция добавляет пользователя в БД
    """
    async with async_session() as session:
        if not first_name:
            first_name = 'None'
        if not username:
            username = 'None'
        session.add(User(tg_id=tg_id, first_name=first_name, username=username, user_refs=user_refs, count_comment_cyberbomb=1))
        session.add(Point(tg_id=tg_id))
        await session.commit()

        #ПОМЕНЯТЬ НА АПИ ОТ ВОЛОДИ
        if user_refs:
            api.add_points(user_refs, 20)
            api.add_points(tg_id, 20)
            await insert_point_log(user_refs, "рефка", 20)
            await insert_point_log(tg_id, "рефка", 20)

async def user_send_comment(tg_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
        await session.execute(update(User).where(User.tg_id == tg_id).values(
            send_comment=True, count_comment=result.count_comment + 1)
        )
        await session.commit()

async def get_count_comment_cyberbomb(tg_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
    if result:
        return result.count_comment_cyberbomb
    return None

async def add_count_comment_cyberbomb(tg_id: BigInteger, n):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
        await session.execute(update(User).where(User.tg_id == tg_id).values(
            count_comment_cyberbomb=result.count_comment_cyberbomb + n)
        )
        await session.commit()

async def substract_count_comment_cyberbomb(tg_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
        await session.execute(update(User).where(User.tg_id == tg_id).values(
            count_comment_cyberbomb=result.count_comment_cyberbomb - 1)
        )
        await session.commit()

async def user_reset_send_comment(tg_id: BigInteger):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(
            send_comment=False)
        )
        await session.commit()


# НЕ НУЖНО
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


async def add_check(check_id: str, retail_name=None, sum_bb=None, n_point=None):
    """
    Функция добавляет чек в БД
    """
    async with async_session() as session:
        session.add(Check(check_id=check_id, name_shop=retail_name, price_bb=sum_bb, points=n_point))
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
        

async def update_tg_id_channel(channel_id: BigInteger, tg_id: BigInteger):
    async with async_session() as session:
        await session.execute(update(Channel).where(Channel.channel_id == channel_id).values(
            tg_id=tg_id)
        )
        await session.commit()

async def reset_all_channel():
    async with async_session() as session:
        await session.execute(update(Channel).where(True).values(
            number_post=0)
        )
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

async def add_count_channel_post(channel_id: BigInteger):
    async with async_session() as session:
        result = await session.scalar(select(Channel).where(Channel.channel_id == channel_id))
        await session.execute(update(Channel).where(Channel.channel_id == channel_id).values(
            count_post=result.count_post + 1)
        )
        await session.commit()


async def add_social_network(tg_id: BigInteger, social_network: str, social_network_link: str):
    async with async_session() as session:
        session.add(SocialNetwork(tg_id=tg_id, social_network=social_network, social_network_link=social_network_link))
        await session.commit()


async def get_social_networks(tg_id: BigInteger):
    async with async_session() as session:
        result = await session.scalars(select(SocialNetwork).where(SocialNetwork.tg_id == tg_id))
    return result.fetchall()

async def get_social_network(tg_id: BigInteger, social_network):
    async with async_session() as session:
        result = await session.scalar(select(SocialNetwork).where(SocialNetwork.tg_id == tg_id,
                                                                   SocialNetwork.social_network == social_network))
    return result

async def search_sn_link(social_network_link):
    async with async_session() as session:
        result = await session.scalar(select(SocialNetwork).where(SocialNetwork.social_network_link == social_network_link))
    return result


async def del_social_networks(tg_id: BigInteger, social_network: str):
    async with async_session() as session:
        result = await session.execute(delete(SocialNetwork).where(SocialNetwork.tg_id == tg_id,
                                                                  SocialNetwork.social_network == social_network))
        await session.commit()
    return result


async def add_link_video(tg_id: BigInteger, link_video: str):
    async with async_session() as session:
        session.add(LinkVideo(tg_id=tg_id, link_video=link_video))
        await session.commit()

async def search_link_video(link_video):
    async with async_session() as session:
        result = await session.scalar(select(LinkVideo).where(LinkVideo.link_video == link_video))
    return result

async def add_link_photo(tg_id: BigInteger, link_photo: str):
    async with async_session() as session:
        session.add(LinkPhoto(tg_id=tg_id, link_photo=link_photo))
        await session.commit()

async def search_link_photo(link_photo):
    async with async_session() as session:
        result = await session.scalar(select(LinkPhoto).where(LinkPhoto.link_photo == link_photo))
    return result

async def update_number_accept_video(social_network: str):
    async with async_session() as session:
        result = await session.scalar(select(NumberAcceptVideo).where(NumberAcceptVideo.social_network == social_network))
        await session.execute(update(NumberAcceptVideo).where(NumberAcceptVideo.social_network == social_network).values(
            number=result.number + 1)
        )
        await session.commit()


async def get_analytics():
    results = []
    async with async_session() as session:
        results.append((await session.execute(func.count(User.id))).scalar())
        results.append((await session.execute(select(func.count()).where(User.user_refs != 0, User.user_refs != 1))).scalar())
        results.append((await session.execute(select(func.count()).where(User.user_refs == 1))).scalar())
        results.append((await session.execute(func.sum(User.count_comment))).scalar())
        results.append((await session.execute(func.count(Post.id))).scalar())
        results.append((await session.execute(func.sum(Channel.count_post))).scalar())
        results.append((
            await session.execute(
                select(SocialNetwork.social_network, func.count(SocialNetwork.id)).group_by(SocialNetwork.social_network)
            )).fetchall())
        results.append((
            await session.execute(
                select(NumberAcceptVideo.social_network, NumberAcceptVideo.number)
            )).fetchall())

        # Сколько чеков загружено всего
        results.append((await session.execute(func.count(Check.id))).scalar())
        # Сколько чеков по магазинам
        results.append((
           await session.execute(
               select(Check.name_shop, func.count(Check.id)).where(Check.points > 0).group_by(
                   Check.name_shop)
           )).fetchall())
        # На какую общую сумму товаров бб было во всех чеках
        results.append((await session.execute(func.sum(Check.price_bb))).scalar())
        # Сколько баллов в общем засчитали за чеки
        results.append((await session.execute(func.sum(Check.points))).scalar())
    return results

async def info_user(tg_id: BigInteger):
    results = []
    async with async_session() as session:
        results.append((await session.execute(
                               select(PointsLog.from_points, func.count(PointsLog.id), func.sum(PointsLog.number_points)).where(PointsLog.tg_id == tg_id).group_by(
                                   PointsLog.from_points)
                           )).fetchall())

    return results

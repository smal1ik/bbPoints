from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from decouple import config
from app.utils.state import User

engine = create_async_engine(config('POSTGRESQL'), echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    user_refs = mapped_column(BigInteger, nullable=True) # рефка
    send_comment = mapped_column(Boolean, default=False)
    count_comment: Mapped[int] = mapped_column(default=0, nullable=True)


class Point(Base):
    __tablename__ = 'points'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    number_points = mapped_column(BigInteger, default=0)


class Check(Base):
    __tablename__ = 'checks'
    id: Mapped[int] = mapped_column(primary_key=True)
    check_id: Mapped[str] = mapped_column()


class Channel(Base):
    __tablename__ = 'channels'
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id = mapped_column(BigInteger)
    number_post: Mapped[int] = mapped_column(default=0)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id = mapped_column(BigInteger)
    post_id = mapped_column(BigInteger)


class SocialNetwork(Base):
    __tablename__ = 'social_networks'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    social_network: Mapped[str] = mapped_column()
    social_network_link: Mapped[str] = mapped_column()


class LinkVideo(Base):
    __tablename__ = 'links_videos'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    link_video: Mapped[str] = mapped_column()


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


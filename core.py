import asyncio
from datetime import datetime, timedelta
from pyrogram import Client
from sqlalchemy import create_async_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    """Модель пользователя для отображения в базе данных"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    status = Column(String)
    status_updated_at = Column(DateTime)


async def process_messages():
    """Функция для обработки сообщений"""
    while True:
        # получаем "готовых для получения сообщений" пользователей
        alive_users = session.query(User).filter(User.status == 'alive').all()

        for user in alive_users:
            if should_cancel_message(user):
                # если обнаружены ключевые слова, помечаем пользователя как завершенного
                user.status = 'finished'
                user.status_updated_at = datetime.utcnow()
                session.commit()
                continue

            # отправляем первое сообщение
            await send_message(user, "Первое сообщение клиента")
            await asyncio.sleep(6 * 60)

            # Отправляем второе сообщение и проверяем наличие триггера
            await send_message(user, "Текст2 ")
            await asyncio.sleep(39 * 60)

            # отправляем третье сообщение
            await send_message(user, "Текст3 ")
            await asyncio.sleep((1 * 24 + 2) * 3600)

            # помечаем пользователя как завершенного
            user.status = 'finished'
            user.status_updated_at = datetime.utcnow()
            session.commit()

        # получаем пользователей со статусом 'dead' и обрабатываем ошибки
        dead_users = session.query(User).filter(User.status == 'dead').all()
        for dead_user in dead_users:
            # обработка ошибок для пользователя со статусом 'dead'
            # например, отправка уведомления администратору или перенос в специальный лог
            print(f"User {dead_user.id} is dead. Handling error...")

            # помечаем пользователя как завершенного
            dead_user.status = 'finished'
            dead_user.status_updated_at = datetime.utcnow()
            session.commit()

        # ждем перед следующей итерацией
        await asyncio.sleep(1)


# глобальное множество ключевых слов
KEYWORDS = {"прекрасно", "ожидать"}


def should_cancel_message(user):
    """Функция для проверки триггеров и отмены отправки при необходимости"""
    messages = get_user_messages(user)

    for message in messages:
        if any(keyword in message for keyword in KEYWORDS):
            return True

    return False


async def send_message(user, message):
    """Функция для отправки сообщения пользователю"""
    try:
        # отправляем сообщение пользователю через Pyrogram
        await app.send_message(user.id, message)
        print(f"Сообщение отправлено пользователю {user.id}")
    except Exception as e:
        # обрабатываем возможные ошибки при отправке сообщения
        print(f"Не удалось отправить сообщение {user.id}: {e}")


async def get_user_messages(user):
    """Функция для получения сообщений пользователя"""
    # здесь должна быть реализация получения сообщений пользователя из базы данных
    # в данном примере просто возвращается список сообщений для пользователя
    # в реальной реализации здесь может быть запрос к базе данных или к API мессенджера
    messages = [
        "Текст1",
        "Текст2",
        "Текст3"
    ]
    return messages


# пнициализация клиента Pyrogram
api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"
app = Client("my_account", api_id=api_id, api_hash=api_hash)

# инициализация базы данных с использованием asyncpg
engine = create_async_engine('postgresql+asyncpg://username:password@localhost/my_database')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
session = Session()

# добавление пользователей для теста
user1 = User(id=1, created_at=datetime.utcnow(), status='alive', status_updated_at=datetime.utcnow())
session.add(user1)
session.commit()

# запуск задачи по обработке сообщений
asyncio.run(process_messages())

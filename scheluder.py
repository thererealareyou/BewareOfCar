import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.blocking import BlockingScheduler

# Настройка базы данных
Base = declarative_base()
engine = create_engine('sqlite:///scheduled_messages.db')
Session = sessionmaker(bind=engine)


class ScheduledMessage(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    send_time = Column(DateTime)


# Создание таблицы
Base.metadata.create_all(engine)


def add_messages():
    """Добавляет 3 сообщения с задержкой 10, 20, 30 секунд"""
    session = Session()
    now = datetime.now()

    messages = [
        ("Сообщение 1 (через 10 сек)", now + timedelta(seconds=10)),
        ("Сообщение 2 (через 20 сек)", now + timedelta(seconds=20)),
        ("Сообщение 3 (через 30 сек)", now + timedelta(seconds=30)),
    ]

    for text, send_time in messages:
        session.add(ScheduledMessage(text=text, send_time=send_time))

    session.commit()
    print("3 сообщения добавлены в очередь!")


if __name__ == "__main__":
    add_messages()
from sqlalchemy import create_engine, Column, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    idTelegram = Column(Integer, unique=True, nullable=False)
    channels = Column(JSON, nullable=False, default=list)
    last_sent_time = Column(JSON, nullable=True, default=dict)
    filters = Column(JSON, nullable=True, default=list)


class Database:
    def __init__(self, db_path="sqlite:///rss_bot.db"):
        self.engine = create_engine(db_path)
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_channel(self, user_id, channel):
        with self.Session() as session:
            try:

                user = session.query(User).filter_by(idTelegram=user_id).first()
                if not user:
                    user = User(idTelegram=user_id, channels=[], last_sent_time={})
                    session.add(user)

                if channel not in user.channels:
                    user.channels.append(channel)
                    session.commit()
                else:
                    raise ValueError(f"Канал {channel} уже добавлен.")
            except Exception as e:
                print(f"Ошибка при добавлении канала: {e}")
                session.rollback()
                raise

    def get_channels(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if user:
                return user.channels
            return []
        except Exception as e:
            print(f"Ошибка при получении каналов пользователя: {e}")
            return []
        finally:
            session.close()

    def get_all_users_and_channels(self):
        session = self.Session()
        try:
            users = session.query(User).all()
            return [(user.idTelegram, user.channels) for user in users]
        except Exception as e:
            print(f"Ошибка при получении всех пользователей и их каналов: {e}")
            return []
        finally:
            session.close()

    def remove_channel(self, user_id, channel):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if user and channel in user.channels:
                user.channels.remove(channel)
                session.commit()
            else:
                raise ValueError(f"Канал {channel} не найден у пользователя.")
        except Exception as e:
            print(f"Ошибка при удалении канала: {e}")
            session.rollback()
        finally:
            session.close()

    def get_last_sent_time(self, user_id, channel):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if user and user.last_sent_time:
                return user.last_sent_time.get(channel)
            return None
        except Exception as e:
            print(f"Ошибка при получении времени последней отправки: {e}")
            return None
        finally:
            session.close()

    def update_last_sent_time(self, user_id, channel):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if not user:
                raise ValueError("Пользователь не найден.")

            if not user.last_sent_time:
                user.last_sent_time = {}

            user.last_sent_time[channel] = datetime.utcnow().isoformat()
            session.commit()
        except Exception as e:
            print(f"Ошибка при обновлении времени последней отправки: {e}")
            session.rollback()
        finally:
            session.close()

    def add_filter(self, user_id, filter_word):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if not user:
                raise ValueError("Пользователь не найден.")

            if not user.filters:
                user.filters = []

            if filter_word not in user.filters:
                user.filters.append(filter_word)
                session.commit()
            else:
                raise ValueError("Фильтр уже существует.")
        except Exception as e:
            print(f"Ошибка при добавлении фильтра: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def remove_filter(self, user_id, filter_word):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if not user:
                raise ValueError("Пользователь не найден.")

            if user.filters and filter_word in user.filters:
                user.filters.remove(filter_word)
                session.commit()
            else:
                raise ValueError("Фильтр не найден.")
        except Exception as e:
            print(f"Ошибка при удалении фильтра: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_filters(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(idTelegram=user_id).first()
            if user and user.filters:
                return user.filters
            return []
        except Exception as e:
            print(f"Ошибка при получении фильтров пользователя: {e}")
            return []
        finally:
            session.close()

    def close(self):
        pass

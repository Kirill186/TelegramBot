import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    idTelegram = Column(Integer, unique=True, nullable=False)
    channels = Column(Text, nullable=False, default='[]')
    last_sent_time = Column(Text, nullable=True, default='{}')
    filters = Column(Text, nullable=True, default='[]')


class Database:
    def __init__(self, db_path="sqlite:///rss_bot.db"):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _load_json_field(self, field_value, default):
        """Загрузить JSON-данные из строки."""
        try:
            return json.loads(field_value) if field_value else default
        except json.JSONDecodeError:
            return default

    def _dump_json_field(self, data):
        """Сериализовать данные в JSON-строку."""
        return json.dumps(data)

    def add_channel(self, user_id, channel):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if not user:
                    user = User(idTelegram=user_id, channels=self._dump_json_field([]), last_sent_time=self._dump_json_field({}))
                    session.add(user)

                channels = self._load_json_field(user.channels, [])
                if channel not in channels:
                    channels.append(channel)
                    user.channels = self._dump_json_field(channels)
                    session.commit()
                else:
                    raise ValueError(f"Канал {channel} уже добавлен.")
            except Exception as e:
                print(f"Ошибка при добавлении канала: {e}")
                session.rollback()
                raise

    def get_channels(self, user_id):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if user:
                    return self._load_json_field(user.channels, [])
                return []
            except Exception as e:
                print(f"Ошибка при получении каналов пользователя: {e}")
                return []

    def get_all_users_and_channels(self):
        session = self.Session()
        try:
            users = session.query(User).all()
            result = []
            for user in users:
                try:
                    channels = json.loads(user.channels)  # Преобразование JSON-строки в список
                except json.JSONDecodeError:
                    print(f"Ошибка декодирования JSON для пользователя {user.idTelegram}")
                    channels = []
                result.append((user.idTelegram, channels))
            return result
        except Exception as e:
            print(f"Ошибка при получении всех пользователей и их каналов: {e}")
            return []
        finally:
            session.close()

    def remove_channel(self, user_id, channel):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if user:
                    channels = self._load_json_field(user.channels, [])
                    if channel in channels:
                        channels.remove(channel)
                        user.channels = self._dump_json_field(channels)
                        session.commit()
                    else:
                        raise ValueError(f"Канал {channel} не найден у пользователя.")
            except Exception as e:
                print(f"Ошибка при удалении канала: {e}")
                session.rollback()

    def get_last_sent_time(self, user_id, channel):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if user:
                    last_sent_time = self._load_json_field(user.last_sent_time, {})
                    return last_sent_time.get(channel)
                return None
            except Exception as e:
                print(f"Ошибка при получении времени последней отправки: {e}")
                return None

    def update_last_sent_time(self, user_id, channel):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if not user:
                    raise ValueError("Пользователь не найден.")

                last_sent_time = self._load_json_field(user.last_sent_time, {})
                last_sent_time[channel] = datetime.utcnow().isoformat()
                user.last_sent_time = self._dump_json_field(last_sent_time)
                session.commit()
            except Exception as e:
                print(f"Ошибка при обновлении времени последней отправки: {e}")
                session.rollback()

    def add_filter(self, user_id, filter_word):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if not user:
                    raise ValueError("Пользователь не найден.")

                filters = self._load_json_field(user.filters, [])
                if filter_word not in filters:
                    filters.append(filter_word)
                    user.filters = self._dump_json_field(filters)
                    session.commit()
                else:
                    raise ValueError("Фильтр уже существует.")
            except Exception as e:
                print(f"Ошибка при добавлении фильтра: {e}")
                session.rollback()

    def remove_filter(self, user_id, filter_word):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if not user:
                    raise ValueError("Пользователь не найден.")

                filters = self._load_json_field(user.filters, [])
                if filter_word in filters:
                    filters.remove(filter_word)
                    user.filters = self._dump_json_field(filters)
                    session.commit()
                else:
                    raise ValueError("Фильтр не найден.")
            except Exception as e:
                print(f"Ошибка при удалении фильтра: {e}")
                session.rollback()

    def get_filters(self, user_id):
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(idTelegram=user_id).first()
                if user:
                    return self._load_json_field(user.filters, [])
                return []
            except Exception as e:
                print(f"Ошибка при получении фильтров пользователя: {e}")
                return []

    def close(self):
        pass

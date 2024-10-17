import mysql.connector
import json
from mysql.connector import Error
from datetime import datetime


class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = self.connect()

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            if connection.is_connected():
                print("Успешное подключение к базе данных")
                return connection
        except Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            return None

    def add_channel(self, user_id, channel_url):
        cursor = self.connection.cursor()
        try:
            # Проверяем, есть ли пользователь в базе данных
            query_check_user = "SELECT idTelegram FROM Users WHERE idTelegram = %s"
            cursor.execute(query_check_user, (user_id,))
            result = cursor.fetchone()

            if result:
                # Если пользователь существует, обновляем его каналы
                query_update = """
                    UPDATE Users
                    SET channels = JSON_ARRAY_APPEND(channels, '$', %s)
                    WHERE idTelegram = %s
                """
                cursor.execute(query_update, (channel_url, user_id))
            else:
                # Если пользователя нет, создаем новую запись
                query_insert = """
                    INSERT INTO Users (idTelegram, channels)
                    VALUES (%s, JSON_ARRAY(%s))
                """
                cursor.execute(query_insert, (user_id, channel_url))

            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при добавлении канала: {e}")
        finally:
            cursor.close()

    def get_channels(self, user_id):
        cursor = self.connection.cursor()
        try:
            query = "SELECT JSON_UNQUOTE(channels) FROM Users WHERE idTelegram = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result:
                channels_json = result[0]
                channels = json.loads(channels_json)
                return channels
            return []
        except Exception as e:
            print(f"Ошибка при получении каналов пользователя: {e}")
            return []
        finally:
            cursor.close()

    def get_all_users_and_channels(self):
        cursor = self.connection.cursor()
        try:
            query = """
            SELECT idTelegram, JSON_UNQUOTE(channels) as channels 
            FROM Users
            WHERE JSON_LENGTH(channels) > 0
            """
            cursor.execute(query)
            result = cursor.fetchall()

            # Преобразуем JSON-каналы в Python список для каждого пользователя
            users_and_channels = []
            for row in result:
                user_id = row[0]
                channels_json = row[1]
                channels = json.loads(channels_json)  # Конвертируем JSON строку в список
                users_and_channels.append((user_id, channels))

            return users_and_channels
        except Exception as e:
            print(f"Ошибка при получении пользователей и каналов: {e}")
            return []
        finally:
            cursor.close()

    def remove_channel(self, user_id, channel_url):
        cursor = self.connection.cursor()
        try:
            # Получаем текущие каналы пользователя
            channels = self.get_channels(user_id)

            if channel_url in channels:
                channels.remove(channel_url)

                # Обновляем поле JSON в базе данных
                query_update = """
                    UPDATE Users
                    SET channels = %s
                    WHERE idTelegram = %s
                """
                new_channels_json = json.dumps(channels)
                cursor.execute(query_update, (new_channels_json, user_id))
                self.connection.commit()
        except Exception as e:
            print(f"Ошибка при удалении канала: {e}")
        finally:
            cursor.close()

    def get_last_sent_time(self, user_id, channel_url):
        with self.connection.cursor() as cursor:
            query = "SELECT last_sent_time FROM Users WHERE idTelegram = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result and result[0]:
                last_sent_time = json.loads(result[0])
                return last_sent_time.get(channel_url)
            return None

    def update_last_sent_time(self, user_id, channel_url):
        with self.connection.cursor() as cursor:
            query = "SELECT last_sent_time FROM Users WHERE idTelegram = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                last_sent_time = json.loads(result[0])
            else:
                last_sent_time = {}

            # Обновляем время для конкретного канала
            last_sent_time[channel_url] = datetime.utcnow().isoformat()

            query = "UPDATE Users SET last_sent_time = %s WHERE idTelegram = %s"
            cursor.execute(query, (json.dumps(last_sent_time), user_id))
            self.connection.commit()

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Подключение к базе данных закрыто")
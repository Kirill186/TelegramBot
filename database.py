import json
import os

class Database:
    def __init__(self, path):
        self.path = path
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as file:
                self.data = json.load(file)
        else:
            self.data = {}

    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self.data, file)

    def add_channel(self, user_id, channel_url):
        if user_id not in self.data:
            self.data[user_id] = []
        self.data[user_id].append(channel_url)
        self.save()

    def get_channels(self, user_id):
        return self.data.get(user_id, [])

    def remove_channel(self, user_id, channel_url):
        if user_id in self.data and channel_url in self.data[user_id]:
            self.data[user_id].remove(channel_url)
            self.save()

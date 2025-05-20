from typing import Dict, List


class Messages:

    def __init__(self):
        self.messages: Dict[str, Dict] = {}

    def add_message(self, message, id):
        self.messages[id] = message

    def get_message(self, id):
        return self.messages.get(id)

    def delete_message(self, id):
        if id in self.messages:
            del self.messages[id]
        else:
            raise KeyError(f"Message with id {id} not found.")

    def get_all_messages(self):
        return self.messages.values()

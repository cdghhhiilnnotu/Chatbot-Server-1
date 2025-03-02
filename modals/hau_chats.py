import json
import os
from typing import List, Dict
from datetime import datetime
from modules.configs import CHATS_PATH

class HAUChat:
    def __init__(self, chat_id: str = "", created_at: str = "", messages: List[Dict] = None):
        if messages is None:
            messages = []
        self.chat_id = chat_id
        self.created_at = created_at
        self.messages = messages

    def __repr__(self):
        return (f"HAUChat(chat_id={self.chat_id}, created_at={self.created_at}, "
                f"messages={self.messages})")

    def add_message(self, sender: str, content: str):
        # Add timestamp for each message
        chat_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages.append({"type": sender, "text": content, "chat_at": chat_at})

    def to_dict(self) -> Dict:
        return {
            "chat_id": self.chat_id,
            "created_at": self.created_at,
            "messages": self.messages
        }

    @classmethod
    def from_dict(cls, data: Dict):
        chat_id = data.get("chat_id", "")
        created_at = data.get("createdAt", "")
        messages = data.get("messages", [])
        return cls(chat_id=chat_id, created_at=created_at, messages=messages)

    def to_json(self, json_path: str):
        """
        Save or append the HAUChat object's data to a JSON file with UTF-8 encoding.
        
        Args:
            json_path (str): Path to the JSON file where the data will be written.
        """
        new_data = {
            self.chat_id: {
                "createdAt": self.created_at,
                "messages": self.messages
            }
        }
        
        # Check if the file exists and read its content
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # Update the existing data with the new chat data
        existing_data.update(new_data)
        
        # Write the merged data back to the file
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)

    @classmethod
    def from_json(cls, chat_id: str, json_path: str):
        """
        Load a HAUChat object from a JSON file with UTF-8 encoding. If chat_id does not exist, 
        add a new entry with the provided chat_id.
        
        Args:
            chat_id (str): The chat ID to load or add.
            json_path (str): Path to the JSON file to read/write.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}  # If the file does not exist, create a new one.

        # Check if the chat_id exists in the data
        if chat_id not in data:
            # If it does not exist, create a new chat entry
            print(f"Chat ID '{chat_id}' not found. Creating a new entry.")
            new_chat = cls(chat_id=chat_id, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # Add the new chat to the data
            data[chat_id] = {
                "createdAt": new_chat.created_at,
                "messages": new_chat.messages
            }
            # Save the updated data back to the file with UTF-8 encoding
            with open(json_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return new_chat

        # If the chat_id exists, load the chat data
        chat_data = data[chat_id]
        return cls.from_dict({
            "chat_id": chat_id,
            "createdAt": chat_data["createdAt"],
            "messages": chat_data["messages"]
        })

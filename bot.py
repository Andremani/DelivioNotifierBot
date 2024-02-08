from config import BOT_TOKEN
from config import BOT_URL
import json
import requests
from sqlite_api import SqliteDb

class TelegramBot():
    def send_message(self, chat_id, message):
        url = f"{BOT_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={message}&parse_mode=HTML"
        response = requests.post(url, timeout=7)
        print(response.text)

        json_root = json.loads(response.text)
        if json_root["ok"] == False:
            print(f'Telegram message delivery to {chat_id} failed due to: {json_root["description"]}')
            if json_root["description"] == "Forbidden: bot was blocked by the user":
                with SqliteDb() as db:
                    db.remove_subscriber(chat_id) # rn user is removed here and added in update_subscribers once again (because no offset)

    def broadcast_message(self, chat_ids_list, message):
        print(f"Broadcasting to {len(chat_ids_list)} subscriber(s)...")
        for chat_id in chat_ids_list:
            self.send_message(chat_id, message)

    def get_updates(self):
        #TODO If a lot of messages - save 'update_id' from telegram_update_response in file and load here to paste in next line (value+1)
        #TODO If a lot of messages (more than 100 per cycle) - add update cycling until telegram response will be empty (or almost empty)

        offset = 0 
        url = f"{BOT_URL}{BOT_TOKEN}/getUpdates?offset={offset}";

        response = requests.get(url, timeout=7)
        print(f"Getting updates from Telegram API...\nResponse <{response.status_code}> \n")
        print(response.text + "\n\n")

        json_root = json.loads(response.text)
        result = json_root["result"]
        
        updated_chats = set()
        for update in result:
            if "message" in update:
                print(f'{update["message"]}')
                chat_id = update["message"]["chat"]["id"]
                updated_chats.add(chat_id)
                print(f'{chat_id}\n')

        return updated_chats
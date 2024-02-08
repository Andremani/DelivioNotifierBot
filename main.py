from delivio_scraper import DelivioScraper
from sqlite_api import SqliteDb
#from restaurant_info import RestaurantInfo
from bot import TelegramBot
import schedule
import time

def search_for_new_restaurants(old_restaurants_info, restaurants_dictionary):
    difference = []
    match = False

    old_restaurants_ids = []
    for item in old_restaurants_info:
        old_restaurants_ids.append(item[0])

    new_id_list = list(restaurants_dictionary.keys())

    for new_id in new_id_list:
        match = False
        for old_id in old_restaurants_ids:
            if new_id == old_id:
                match = True
                break
        if match == False:
            difference.append(restaurants_dictionary[new_id])
    return difference

def print_new_restaurants(new_restaurants):
    if len(new_restaurants) > 0:
        print("\n---===---")
        print("New restaurants:")
        print("---===---", end = "\n\n")
        for restaurant in new_restaurants:
            print(restaurant.name)
            print("   " + str(restaurant.id) + " - " + restaurant.slug)
        print("\n---===---", end = "\n\n")
    else:
        print("No new restaurants!")

def find_new_restaurants():
    with SqliteDb() as db:
        scraper = DelivioScraper()

        scraped_restaurants_dictionary = scraper.run()
        print(scraped_restaurants_dictionary)
    
        old_restaurants_info = db.select_existing_restaurants()
        print(f"old_restaurants_info: \n{old_restaurants_info}\n\n")

        new_restaurants = search_for_new_restaurants(old_restaurants_info, scraped_restaurants_dictionary)
        print_new_restaurants(new_restaurants)

        db.put_new_restaurants_in_database(new_restaurants)

        return new_restaurants

def update_subscribers():
    with SqliteDb() as db:
        bot = TelegramBot()

        new_chats = bot.get_updates()
        if(len(new_chats > 0)):
            print(f"new_chats: {new_chats}")
        db.put_new_subscribers_in_database(new_chats)

def create_new_restaurants_message(new_restaurants):
    if len(new_restaurants) < 1:
        message = "На Delivio.by новых ресторанов нет :("
        return message
    restaurant_names = []
    for restaurant in new_restaurants:
        restaurant_names.append(restaurant.name)
    restraunt_names_string = "\n".join(restaurant_names)
    message = "<b>На Delivio.by появились новые рестораны!</b>\n\n" + restraunt_names_string
    return message

def new_restaurants_broadcast(new_restaurants):
    with SqliteDb() as db:
        bot = TelegramBot()
    
        all_chat_ids = db.select_subscribers()
        print(f"all_chat_ids: \n{all_chat_ids}\n\n")
        message = create_new_restaurants_message(new_restaurants)
        bot.broadcast_message(all_chat_ids, message)

def main():
    new_restaurants = find_new_restaurants()
    update_subscribers()

    if len(new_restaurants) > 0:
        new_restaurants_broadcast(new_restaurants)
    else:
        print("No new restaurants. No broadcasting")

if __name__ == '__main__':
    main()
from math import ceil
from time import sleep
import random
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin
from restaurant_info import RestaurantInfo
from config import INITIAL_DELIVIO_PAGE

#with open("DelivioScrappedJSONPageExample.json", "r") as json_file:
#    json_hardcoded_response = json_file.readlines()
#    json_file.close()

class DelivioScraper():

    def __init__(self, *args, **kwargs):
        self.__restaurants_dictionary = {}
        self.__last_url = None
        self.__next_url = None

    def parse_json(self, json_root):
        json_restaurant_list = json_root["hydra:member"]
        for restaurant in json_restaurant_list:
            self.__restaurants_dictionary[restaurant["id"]] = RestaurantInfo(restaurant["id"], restaurant["name"], restaurant["slug"])

    def run(self):
        HOST_URL = "https://delivio.by"
        START_URL = "https://delivio.by/be/api/restaurants"

        hardcoded_fake_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        user_agent = UserAgent(fallback=hardcoded_fake_user_agent)

        HEADERS = { 
	        "User-Agent": user_agent.random,
	        "Referer": "https://delivio.by/",
            #"If-None-Match": "686897696a7c876b7e", #use ETag sent by server and process code 304 (Not Modified) to optimize
        } 
        PROXIES = { 
	        "http" : "154.85.58.149:80",
            "http" : "188.87.137.45:3128",
        } 
        PARAMS = {
            "collapse_network" : True,
            "geolocation" : "53.902639, 27.557109",
            "itemsPerPage" : 12,
            "page" : INITIAL_DELIVIO_PAGE,
            "type" : 1,
        }

        response = requests.get(START_URL, params=PARAMS, headers=HEADERS, proxies=PROXIES, timeout=7)
        print(f"Response <{response.status_code}> \n\n")
        print(response.text + "\n\n")

        if(not response.ok):
            return

        json_root = json.loads(response.text)
        self.__last_url = json_root["hydra:view"]["hydra:last"]

        ###Getting total amount of pages by another method
        #items_per_call = 12;
        #total_items = int(json_root["hydra:totalItems"])
        #total_calls =  ceil(total_items / items_per_call)
        #print(total_calls)

        while True:
            self.parse_json(json_root)

            previous_next_url = self.__next_url
            if "hydra:next" in json_root["hydra:view"]:
                self.__next_url = json_root["hydra:view"]["hydra:next"]
            else:
                print("No next page exists")
                break

            print(f"previous_next_url: {previous_next_url}")
            print(f"self.__last_url: {self.__last_url}")
            print(f"self.__next_url: {self.__next_url}")

            if previous_next_url == self.__last_url:
                break

            delay = 1 + random.random() * 1.5
            print(f"Sleep start ({delay} s)")
            sleep(delay)
            print("Sleep end")

            url = urljoin(HOST_URL, self.__next_url)
            response = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=7)
            print(f"Response <{response.status_code}> \n\n")
            print(response.text + "\n\n")

            json_root = json.loads(response.text)

        print("\n\n---\n\n")
        print(len(self.__restaurants_dictionary))
        print("\n\n---\n\n")
        return self.__restaurants_dictionary
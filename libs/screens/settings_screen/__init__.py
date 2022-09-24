from kivymd.uix.screen import MDScreen
from libs.components.menu_item import MenuItemSettings
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.clock import Clock

import requests
from functions import get_from_database, update_in_database
from bs4 import BeautifulSoup
import threading
from functools import partial
import json
from libs.components.menu_item import DislikedFood

class SettingsScreen(MDScreen):
    menus = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menus = {
                        "Meni 1": ["food-drumstick-outline"],
                        "Meni 2": ["carrot"],
                        "Meni 3": ["food-steak"],
                        "Meni 4": ["food-croissant"],
                        "Meni 5": ["bowl-mix-outline"],
                        "Meni 6": ["basketball"],
                        "Odjava": ["close"]
                        } # {"meni 1": ["icon-name": Str, meal_id: Int, selected: Bool]}

    def on_enter(self):
        app = MDApp.get_running_app()
        if not app.logged_in:
            app.show_dialog("Error", "Please login!")
            return
        threading.Thread(target=self.load_menus).start()
        threading.Thread(target=self.load_disliked_foods).start()

    def load_menus(self, *args):
        app = MDApp.get_running_app()
        Clock.schedule_once(app.show_spinner)
        def clear(*args):
            self.ids.menus.clear_widgets()
        Clock.schedule_once(clear)
        # login
        session = requests.Session()
        login_url = "https://www.easistent.com/p/ajax_prijava"
        meals_url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_seznam"
        username = get_from_database("user_info", 1)[1]
        password = get_from_database("user_info", 1)[2]
        data = {
                "uporabnik":username,
                "geslo":password,
                "pin":"",
                "captcha":"",
                "koda":""
                }
        login = session.post(login_url, data=data)

         # added selected
        meal_selected = get_from_database("user_info", 1)[4] # "Meni 1" or "Meni 2" ...
        if not meal_selected == None:
            self.menus[meal_selected].append(True)
        else:
            self.menus["Odjava"].append(True)
        # get menu ids
        if len(self.menus["Meni 1"]) <= 2:
            response = session.get(meals_url)
            soup = BeautifulSoup(response.content, "html.parser")
            meals_ids = []
            for i in range(6):
                meal_id = soup.find(class_=id).find_all("tr")[i + 1]
                if i == 0:
                    meal_id = meal_id.find_all("td")[1].get("id")
                else:
                    meal_id = meal_id.findChildren()[0].get("id")
                meal_id = meal_id.split("-")[4]
                meals_ids.append(int(meal_id))
            # added id
            pos = 0
            for i in self.menus.keys():
                if i == "Odjava":
                    if len(self.menus[i]) < 2:
                        self.menus[i].append(False)
                        self.menus[i].append(0)
                    else:
                        self.menus[i].append(0)
                elif len(self.menus[i]) < 2:
                    self.menus[i].append(False)
                    self.menus[i].append(meals_ids[pos])
                else:
                    self.menus[i].append(meals_ids[pos])
                pos += 1

        for menu in self.menus.keys():
            def add_item(menus, menu, *args):
                # app.root.ids.settings.ids.menus.add_widget(MenuItemSettings(text=menu, icon=self.menus[menu][0], id=self.menus[menu][2], selected=self.menus[menu][1]))
                app.root.ids.settings.ids.menus.add_widget(MenuItemSettings(text=menu, icon=menus[menu][0], id=menus[menu][2], selected=menus[menu][1]))
            Clock.schedule_once(partial(add_item, self.menus, menu))
        Clock.schedule_once(partial(app.close_spinner))

    def load_disliked_foods(self):
        def clear(*args):
            self.ids.disliked_foods_menu.clear_widgets()
        Clock.schedule_once(clear)
        db_foods = get_from_database("user_info", 1)[3]
        if db_foods == None:
            db_foods = "[]"
        db_foods = json.loads(db_foods)
        for food in db_foods:
            def add_to_screen(food, *args):
                self.ids.disliked_foods_menu.add_widget(DislikedFood(text=food))
            Clock.schedule_once(partial(add_to_screen, food))


    def add_disliked_food(self):
        foods = self.ids.disliked_foods.text
        foods = foods.split(",")
        #add to database
        db_foods = get_from_database("user_info", 1)[3]
        if db_foods == None:
            db_foods = "[]"
        db_foods = json.loads(db_foods)
        db_foods += foods
        update_in_database("user_info", "disliked_foods", (json.dumps(db_foods), 1))
        threading.Thread(target=self.load_disliked_foods).start()

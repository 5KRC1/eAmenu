from kivymd.uix.screen import MDScreen
from kivymd.utils import asynckivy
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock, mainthread

from libs.components.menu_item import MenuItemMain

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from functools import partial
import threading
from functions import get_from_database
'''
TODO
- enable user to change meal on click of card
- do TODO comments
- create loading spinner
- create login

- add automatic meal changer (check once a day (or so) for meals)
'''

class MainScreen(MDScreen):
    date_of_menu = ObjectProperty() # type: DateTime |
    week_of_menu = NumericProperty() # type: int | used for fetching next week's data
    week_one_day_one = ObjectProperty() # type: DateTime | first day of week one => to calculate week_num
    meals_ids = ObjectProperty() # type: Array | consists of meal ids

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        date_today = datetime.now()
        self.date_of_menu = date_today
        if self.date_of_menu.strftime("%w") == "6": # if day is saturday
            self.date_of_menu = self.date_of_menu + timedelta(days=2)
        elif self.date_of_menu.strftime("%w") == "0": # if day is sunday
            self.date_of_menu = self.date_of_menu + timedelta(days=1)

        # get week number
        curr_month = int(date_today.strftime("%m"))
        curr_year = int(date_today.strftime("%Y"))
        if curr_month < 9:
            curr_year -= 1
        first_day_school = datetime(curr_year, 9, 1)
        first_day = int(first_day_school.strftime("%w"))
        if not first_day == 1:
            if first_day > 1 and first_day < 6:
                first_day_school -= timedelta(days=first_day - 1)
            elif first_day == 6:
                first_day_school += timedelta(days=2)
            elif first_day == 0:
                first_day_school += timedelta(days=1)

        # self.week_one_day_one = datetime(2022, 8, 29) # start of week one
        self.week_one_day_one = first_day_school

    def on_enter(self):
        app = MDApp.get_running_app()
        if not app.logged_in:
            app.show_dialog("Error", "Please login!")
            # app.root.ids.manager.current = "login"
            return
        # app.root.ids.main.ids.menu_list.clear_widgets()
        threading.Thread(target=self.load_menus).start()

    def load_menus(self):
        app = MDApp.get_running_app()
        def clear(*args):
            app.root.ids.main.ids.menu_list.clear_widgets()
        Clock.schedule_once(clear)
        app.show_spinner()
        meals_url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_seznam"
        login_url = "https://www.easistent.com/p/ajax_prijava"
        meals_icons = [
                "food-drumstick-outline", 
                "carrot", 
                "food", 
                "food-croissant", 
                "bowl-mix-outline", 
                "basketball"
                ]
        meals = {}
        id = "ednevnik-seznam_ur_teden"
        today = str(self.date_of_menu.strftime("%Y-%m-%d"))
       
        # login
        session = requests.Session()
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

        # get menu ids
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
            meals_ids.append(meal_id)

        for i in range(6):
            meals.update({meals_ids[i]:meals_icons[i]})

        # get menu data
        week_num = int(str((self.date_of_menu - self.week_one_day_one + timedelta(days=1)) / 7).split(" ")[0])
        data = {
                "qversion": 1, #num of tries
                "teden": week_num, #num of week before (if 4 will get 5)
                "smer": "naprej" # direction
                }
        headers = {
                "Content-Type": "application/x-www-form-urlencoded"
                }
        site = session.post(meals_url, data=data, headers=headers)
        soup = BeautifulSoup(site.content, "html.parser")

        # testing
        # meal_id = f"{id}46247-{str(today)}-0"
        # meal = soup.find("td", {"id": meal_id})
        
        data = []

        for meal in meals.keys():
            meal_id = f"{id}-td-malica-{meal}-{today}-0"
            try:
                meal_html = soup.find("td", id=meal_id)
            except:
                app.show_dialog("Error", "Please try restarting!")
                return
            # if len(meal_html.find("div").find_all("div")) < 3 and len(meal_html.find("div").find_all("span")) == 0:
                # app.show_dialog("Error", "Could not fetch!")
                # app.close_spinner()
                # return
            meal_secondary_text = meal_html.find("div").find_all("div")[1].text.strip()
            meal_text = meal_html.find("div").find_all("div")[0].text.strip()
            if len(str(datetime.now() - self.date_of_menu).split(" ")) > 1 and int(str(datetime.now() - self.date_of_menu).split(" ")[0]) < 0:
                meal_selected = meal_html.find("div").find_all("div")[2].find_all("span")[0].text.strip() \
                        if not meal_html.find("div").find_all("div")[2].find("span") == None \
                        else ""
            else:
                meal_selected = meal_html.find("div").find("span").text.strip() \
                        if not meal_html.find("div").find("span") == None \
                        else ""
            obj = {"text": meal_text, "secondary_text": meal_secondary_text, "icon": meals[meal], "meal_id": int(meal), "selected": True if meal_selected in ["Prijavljen", "Naročen", "Nepravočasna odjava"] else False}
            data.append(obj)
        self.create_cards(data)
        def change_date(*args):
            app.root.ids.main.ids.date_label.text = str(self.date_of_menu.strftime("%d. %b. %y"))
        Clock.schedule_once(change_date)
        app.close_spinner()
    
    @mainthread
    def create_cards(self, data):
        for item in data:
            widget = MenuItemMain(text=item["text"], secondary_text=item["secondary_text"], icon=item["icon"], meal_id=item["meal_id"], selected=item["selected"])
            self.ids.menu_list.add_widget(widget)

    def date_forward(self):
        app = MDApp.get_running_app()
        print("date forward")
        self.date_of_menu += timedelta(days=1)
        # date %w => vals=[0-6]; 0=Sunday; 6=Saturday
        # if date lands on weekend => no data => forward to monday
        if self.date_of_menu.strftime("%w") == "6":
            self.date_of_menu = self.date_of_menu + timedelta(days=2)
        elif self.date_of_menu.strftime("%w") == "0":
            self.date_of_menu = self.date_of_menu + timedelta(days=1)
        def clear(*args):
            app.root.ids.main.ids.menu_list.clear_widgets()
        # Clock.schedule_once(clear)
        self.load_menus()

    def date_backward(self):
        app = MDApp.get_running_app()
        print("date backward")
        self.date_of_menu -= timedelta(days=1)
        # date %w => vals=[0-6]; 0=Sunday; 6=Saturday
        # if date lands on weekend => no data => forward to monday
        if self.date_of_menu.strftime("%w") == "6":
            self.date_of_menu = self.date_of_menu - timedelta(days=1)
        elif self.date_of_menu.strftime("%w") == "0":
            self.date_of_menu = self.date_of_menu - timedelta(days=2)
        def clear(*args):
            app.root.ids.main.ids.menu_list.clear_widgets()
        # Clock.schedule_once(clear)
        self.load_menus()

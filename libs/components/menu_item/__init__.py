from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock

from datetime import datetime, timedelta
import requests
import threading
from functions import update_in_database, get_from_database
import json

class MenuItemMain(MDCard):
    # menu items on main screen
    meal_id = NumericProperty() # type: int | id of displayed meal
    text = StringProperty() # type: str | displays meal-type
    secondary_text = StringProperty() # type: str | displays meal contents
    selected = BooleanProperty() # type: bool | if selected => yellow else => blue
    icon = StringProperty() # type: str | meal icon

    def prijava_odjava(self, action):
        app = MDApp.get_running_app()
        # login
        login_url = "https://www.easistent.com/p/ajax_prijava"
        session = requests.Session()
        data = {
                "uporabnik":"skrjancmatic14@gmail.com",
                "geslo":"Ririn#14",
                "pin":"",
                "captcha":"",
                "koda":""
                }
        login = session.post(login_url, data=data)

        # prijava
        url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_prijava"
        data = {
                "tip_prehrane": "malica",
                "id_lokacija": "0",
                "akcija": f"{action}", # either "prijava" or "odjava"
                "id_meni": f"{self.meal_id}", # meals ids (see main_screen)
                "datum": f"{app.root.ids.main.date_of_menu.strftime('%Y-%m-%d')}" # date (MainScreen().date_of_menu)
                }
        headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
                }
        try:
            response = session.post(url, data=data, headers=headers)
            if not response.json()["status"]: # "ok" if successful "" if unsuccessful
                raise Exception("Unable to execute")
            def update_ui_success(*args):
                app.root.ids.main.ids.menu_list.clear_widgets()
                app.root.ids.main.load_menus()
            Clock.schedule_once(update_ui_success)
        except:
            # TODO: show dialog with error
            print("unable")
            return

class MenuItemSettings(MDCard):
    # menu items on settings screen
    id = NumericProperty() # type: int | id of meal
    text = StringProperty() # type: str | displays meal-type
    secondary_text = StringProperty() # type: str | displays meal contents
    selected = BooleanProperty() # type: bool | if selected => yellow else => blue
    icon = StringProperty() # type: str | meal icon

    def choose_menu(self, menu):
        app = MDApp.get_running_app()
        update_in_database("user_info", "menu_option", (menu.text, 1))
        settings = app.root.ids.settings
        for item in settings.menus.keys():
            settings.menus[item][1] = False
        settings.menus[menu.text][1] = True
        settings.load_menus()

class DislikedFood(MDCard):
    text = StringProperty()

    def remove_disliked_food(self, food): # food: str
        db_foods = get_from_database("user_info", 1)[3]
        db_foods = json.loads(db_foods)
        db_foods_new = []
        for item in db_foods:
            if not item == food:
                db_foods_new.append(item)
        update_in_database("user_info", "disliked_foods", (json.dumps(db_foods_new), 1))
        app = MDApp.get_running_app()
        app.root.ids.settings.load_disliked_foods()

from kivymd.app import MDApp 
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

import requests
from functions import update_in_database
from functools import partial

class LoginScreen(MDScreen):

    def login(self):
        app = MDApp.get_running_app()
        #get data
        username = self.ids.username.text
        password = self.ids.password.text
        #try login
        login_url = "https://www.easistent.com/p/ajax_prijava"
        session = requests.Session()
        data = {
                "uporabnik":username,
                "geslo":password,
                "pin":"",
                "captcha":"",
                "koda":""
                }
        try:
            login = session.post(login_url, data=data)
            if not login.json()["status"] == "ok":
                # raise Exception("oops something went wrong")
                app.show_dialog("Error", "Wrong credentials")
                return
            #TODO: save info to sqlite
            update_in_database("user_info", "username", (username, 1))
            update_in_database("user_info", "password", (password, 1))
            app.logged_in = True
            # app.root.ids.manager.current = "main"
        except:
            app.show_dialog("Error", "Wrong credentials")
            return

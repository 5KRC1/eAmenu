from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy import platform
from kivy.properties import BooleanProperty
from kivy.clock import mainthread

from libs.components.content_navigation_drawer import ContentNavigationDrawer
from libs.components.spinner import Spinner

import sqlite3

class Main(MDApp):
    # TODO: add sqlite3
    spinner = ""
    logged_in = BooleanProperty(False)
    
    def build(self):
        if not platform == "android":
            Window.size = [300, 600]
            self.icon = "./assets/images/eAmenu_icon.png"
        self.initialize_database()
        self.theme_cls.material_style = "M3"
        colors = {
                "Blue": {
                    "200": "#3e53d7",
                    "500": "#3e53d7",
                    "700": "#3e53d7",
                    },
                "Red": {
                    "200": "#C25554",
                    "500": "#C25554",
                    "700": "#C25554",
                    "A700": "#C25554"
                    },
                "Light": {
                    "StatusBar": "#E0E0E0",
                    "AppBar": "#3e53d7",
                    "Background": "#ffffff",
                    "CardsDialogs": "#FFFFFF",
                    "FlatButtonDown": "#CCCCCC",
                    }
                }
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        self.load_kvs()
        return Builder.load_file("kivy.kv")

    def on_start(self):
        if platform == "android":
            self.start_service()
        ContentNavigationDrawer().load_tabs()

    def load_kvs(self):
        # components
        Builder.load_file("libs/components/toolbar/toolbar.kv")
        Builder.load_file("libs/components/content_navigation_drawer/content_navigation_drawer.kv")
        Builder.load_file("libs/components/menu_item/menu_item.kv")
        Builder.load_file("libs/components/spinner/spinner.kv")

        # screens
        Builder.load_file("libs/screens/main_screen/main_screen.kv")
        Builder.load_file("libs/screens/settings_screen/settings_screen.kv")
        Builder.load_file("libs/screens/login_screen/login_screen.kv")

    def initialize_database(self):
        '''Creates Tables In Database'''
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS user_info(id INTEGER NOT NULL PRIMARY KEY, username, password, disliked_foods, menu_option)""")
        c.execute("""SELECT * FROM user_info""")
        user_info = c.fetchall()
        if not user_info:
            c.execute("""INSERT INTO user_info(username, password, disliked_foods, menu_option) VALUES(?, ?, ?, ?)""", (None, None, None, None))
        elif user_info[0][1] == None:
            self.logged_in = False
        else:
            self.logged_in = True if not user_info[0] == None else False
        conn.commit()
        conn.close()

    #dialogs
    @mainthread
    def show_dialog(self, status, message, *args):
        button = MDRaisedButton(text="OK", on_release=self.close_dialog)
        button.elevation = 0
        self.dialog = MDDialog(
                md_bg_color=self.theme_cls.bg_light,
                title=status,
                text=message,
                buttons=[
                    button
                    ],
                auto_dismiss=False
                )
        self.dialog.open()

    @mainthread
    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        return

    @mainthread
    def show_spinner(self, *args):
        self.spinner = Spinner(
                spinning=True,
                auto_dismiss=False,
                )
        self.spinner.open()

    @mainthread
    def close_spinner(self, *args):
        self.spinner.spinning = False
        self.spinner.dismiss()

    # background service
    def start_service(self):
        from jnius import autoclass
        service = autoclass("org.dasadweb.eamenu.ServiceMeni")
        mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
        service.start(mActivity, "")
        return service

if __name__ == "__main__":
    Main().run()

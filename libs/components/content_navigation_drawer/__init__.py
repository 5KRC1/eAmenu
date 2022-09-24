from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem
from kivy.properties import StringProperty
from kivymd.app import MDApp

class ContentNavigationDrawer(MDBoxLayout):
    def load_tabs(self):
        app = MDApp.get_running_app()
        tabs = {
                "Home": ["main", "home-outline"],
                "Settings": ["settings", "cog-outline"]
                }
        for tab in tabs.keys():
            app.root.ids.content_drawer.ids.tabs.add_widget(Tab(text=tab, icon=tabs[tab][1], screen=tabs[tab][0]))
        app.root.ids.content_drawer.ids.tabs.children[-1].text_color = app.theme_cls.primary_color

class Tab(OneLineIconListItem):
    screen = StringProperty()
    icon = StringProperty()

    def set_color_item(self, instance_item):
        app = MDApp.get_running_app()
        for item in app.root.ids.content_drawer.ids.tabs.children:
            if item.text_color == app.theme_cls.primary_color:
                item.text_color = app.theme_cls.text_color
                break
        instance_item.text_color = app.theme_cls.primary_color   

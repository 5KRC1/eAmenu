from kivymd.uix.dialog import MDDialog
from kivy.properties import BooleanProperty

class Spinner(MDDialog):
    '''Loading Spinner Dialog'''
    spinning = BooleanProperty(False)

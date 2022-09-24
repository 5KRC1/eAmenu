from time import sleep
import logging
from datetime import datetime, timedelta
import json
from functions import get_from_database
import requests
from bs4 import BeautifulSoup

# from jnius import autoclass
# PythonService = autoclass("org.kivy.android.PythonService")
# PythonService.mService.setAutoRestartService(True)

print("===========started=========")
while True:
    #run service
    if get_from_database("user_info", 1)[2] == None:
        print("not logged in!")
        sleep(1800)
        continue
    # login
    login_url = "https://www.easistent.com/p/ajax_prijava"
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
    try:
        login = session.post(login_url, data=data)
    except:
        print("error logging in!")
        sleep(1800)
        continue

    # get menu ids
    meals_url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_seznam"
    try:
        response = session.get(meals_url)
    except:
        print("error getting ids!")
        sleep(1800)
        continue
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

    # get menu data
    date_today = datetime.now()
    date_of_menu = date_today + timedelta(days=8) #date 8 days in advance (can only change meal a week in advance)
    if date_of_menu.strftime("%w") == "6": # if day is saturday
        date_of_menu = date_of_menu + timedelta(days=2)
    elif date_of_menu.strftime("%w") == "0": # if day is sunday
        date_of_menu = date_of_menu + timedelta(days=1)

    # if mont is lower than september -1 year
    curr_month = int(date_of_menu.strftime("%m"))
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
    week_one_day_one = first_day_school

    week_num = int(str((date_of_menu - week_one_day_one + timedelta(days=1)) / 7).split(" ")[0])
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

    id = "ednevnik-seznam_ur_teden"
    today = str(date_of_menu.strftime("%Y-%m-%d"))
    for meal_id in meals_ids:
        meal_html_id = f"{id}-td-malica-{meal_id}-{today}-0"
        #TODO: check if meal selected
        meal_html = soup.find("td", id=meal_html_id)
        # if not len(str(datetime.now() - date_of_menu).split(" ")) > 1 and int(str(datetime.now() - date_of_menu).split(" ")[0]) < 0:
            # meal_selected = meal_html.find("div").find("span").text.strip() 
            # meal_selected = meal_html.find("div").find_all("div")[2].find_all("span")[0].text.strip() 
                    # if not meal_html.find("div").find_all("div")[2] == None \
                    # else ""
        # else:
            # meal_selected = meal_html.find("div").find("span").text.strip() 
                    # if not meal_html.find("div").find("span") == None \
                    # else ""
        meal_selected_helper = meal_html.find(id=f"dijaki-prehrana-{today}-{meal_id}-0-akcija")
        if len(meal_selected_helper.findChildren()) > 1:
            meal_selected = meal_html.find(id=f"dijaki-prehrana-{today}-{meal_id}-0-akcija").findChildren()[1].text.strip()
        else:
            meal_selected = meal_html.find(id=f"dijaki-prehrana-{today}-{meal_id}-0-akcija").findChildren()[0].text.strip()
        meal_text = meal_html.find("div").find_all("div")[1].text.strip()
        if meal_selected in ["Naročen"]:
        # if yes => check if disliked_foods
            disliked_foods = get_from_database("user_info", 1)[3]
            if disliked_foods == None:
                print("no disliked foods!")
                sleep(1800)
                continue
            disliked_foods = json.loads(disliked_foods)
            for food in disliked_foods:
                if food.upper() in meal_text:
                #   if yes => change to selected menu
                    selected_menu = get_from_database("user_info", 1)[4]
                    if selected_menu == "Odjava":
                        url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_prijava"
                        print(selected_menu, date_of_menu.strftime("%Y-%m-%d"))
                        data = {
                                "tip_prehrane": "malica",
                                "id_lokacija": "0",
                                "akcija": "odjava", # either "prijava" or "odjava"
                                "id_meni": f"{meal_id}", # meals ids (see main_screen)
                                "datum": f"{date_of_menu.strftime('%Y-%m-%d')}" # date (MainScreen().date_of_menu)
                                }
                        headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "X-Requested-With": "XMLHttpRequest"
                                }
                        try:
                            response = session.post(url, data=data, headers=headers)
                            if not response.json()["status"]: # "ok" if successful "" if unsuccessful
                                print(response.json())
                                raise Exception("Unable to execute")
                            #break for loop
                            print("odjava")
                            break
                        except:
                            # TODO: show dialog with error
                            print("error changing meals")

                    selected_menu = meals_ids[int(selected_menu[-1]) - 1]

                    # prijava
                    url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_prijava"
                    print(selected_menu, date_of_menu.strftime("%Y-%m-%d"))
                    data = {
                            "tip_prehrane": "malica",
                            "id_lokacija": "0",
                            "akcija": "prijava", # either "prijava" or "odjava"
                            "id_meni": f"{selected_menu}", # meals ids (see main_screen)
                            "datum": f"{date_of_menu.strftime('%Y-%m-%d')}" # date (MainScreen().date_of_menu)
                            }
                    headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "X-Requested-With": "XMLHttpRequest"
                            }
                    try:
                        response = session.post(url, data=data, headers=headers)
                        if not response.json()["status"]: # "ok" if successful "" if unsuccessful
                            print(response.json())
                            raise Exception("Unable to execute")
                        #break for loop
                        print("meals changed")
                        break
                    except:
                        # TODO: show dialog with error
                        print("error changing meals")

                #   if no => leave as is and continue
            # if no => check another meal_id
    sleep(86400)
    # sleep(5)

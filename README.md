![eAmenu logo](https://github.com/5KRC1/eAmenu/blob/master/assets/images/eAmenu_logo.png "eAmenu logo")
# eAmenu
The "bill of fare" for eAsistent school meals.

## Description (What, why and how)
I got tired of always frogetting to check if I liked the meals I was assigned to in eAsistent.
Because you are only able to change meals a week in advance and they are only shown 14 days in advance, you are required to do this every single week (util you finish school).

It can show you all the meals for that day, as far in the future as eAsistent allows, and as far in the past as it allows.
On top of that it can remember the foods you do not like (they must me spelled the exact way they are in eAsistent) and switch to selected meal or sign you out for that day.
It also sends a notification of any changes, so in case you do not agree with the changes, you can always overwrite them in eAsistent.

It is built with python. It requires [Kivy](https://github.com/kivy/kivy), [KivyMD](https://github.com/kivymd/KivyMD),
[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) and [Buildozer](https://github.com/kivy/buildozer) (for Android).
The service also runs in the background (on Android) with python for android.

## Install
### Android
#### APK
Download the apk file [here](https://www.dasadweb.tk/files/eAmenu.apk).

#### Buildozer
Follow linux/windows terminal instructions first.
Then connect your phone via USB and in its settings [enable "USB Debugging"](https://www.lifewire.com/enable-usb-debugging-android-4690927) (developer options).
After run the following in the command prompt.
```
buildozer android debug deploy run
```
This will create .buildozer (hidden) and bin folder. Inside bin folder there is also APK file, but the previous command should already deploy it on your phone.

### Linux
Purely GUI. Service does not run in the background (it does not change meals yet)!
In your terminal clone this project with the following command.
```
git clone https://github.com/5KRC1/eAmenu
```
Next let's navigate into the newly created folder.
```
cd eAmenu
```
Here, either in python virtual environment (recommended) or just system python, run the following to install needed requirements.
```
pip install -r requirements.txt
```
(virtual environment) or
```
pip3 install -r requirements.txt
```
After the installation is complete, simply run main.py.
```
python main.py
```
(virtual environment) or
```
python3 main.py
```

### Windows
Working on it...

## Use
Gathering screenshots...

## ToDo
- Finish README
- Improve performance on Android
- run service on other platforms

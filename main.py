import os
import re
import json
import threading
import urllib.request
import urllib.parse
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.clock import Clock, mainthread

# Security & Child Safety Guard
BLOCKED_KEYWORDS = re.compile(
    r"\b(porn|xxx|sex|nude|naked|erotic|nsfw|adult|hentai|penis|vagina|boobs|breast|"
    r"intercourse|fetish|orgasm|strip|masturbat|escort|gambling|casino|betting|hack)\b",
    re.IGNORECASE
)

# App Global State
class AppState:
    selected_lang = "English"
    selected_code = "en"
    selected_grade = "Classes 3-5"

# CBSE & Financial Literacy Curriculum
CBSE_DATA = {
    "Pre-Nursery / KG": [
        {
            "subject": "Financial Literacy",
            "topic": "The Magic Piggy Bank",
            "image": "assets/money.png",
            "content": "Coin by coin, save every day!\nDrop your spare coins into your piggy bank to build strong saving habits.",
            "question": "Where is the best place to keep your spare coins safe?",
            "options": ["In a Piggy Bank", "Throwing on the floor"],
            "correct": 0,
            "reward": "Smart Saver Piggy Badge",
            "praise": "Super saver! You are building great financial habits!"
        },
        {
            "subject": "Rhymes & Phonics",
            "topic": "The Solar System",
            "image": "assets/sun.png",
            "content": "The Sun is bright and warm, providing light and energy to our entire Earth!",
            "question": "Which big shining star gives warmth to Earth?",
            "options": ["The Sun", "The Moon"],
            "correct": 0,
            "reward": "Little Astronomer Badge",
            "praise": "Brilliant! You know our glowing Sun!"
        },
        {
            "subject": "Good Manners & Hygiene",
            "topic": "Polite Magic Words",
            "image": "assets/manners.png",
            "content": "Say 'Please' when asking for help, 'Thank You' when receiving a gift, and 'Sorry' when making a mistake.",
            "question": "What should you say when someone shares a toy with you?",
            "options": ["Thank You!", "Give Me More!"],
            "correct": 0,
            "reward": "Golden Courtesy Crown",
            "praise": "Wonderful manners! You are a polite superstar!"
        }
    ],
    "Classes 1-2": [
        {
            "subject": "Financial Literacy",
            "topic": "Needs vs. Wants",
            "image": "assets/money.png",
            "content": "A NEED is essential (healthy food, books, clean water).\nA WANT is nice to have but not essential (extra toys, candy).\nAlways fulfill Needs before Wants!",
            "question": "Which of these is a basic NEED for every student?",
            "options": ["Healthy Food & Books", "Extra Toy Cars"],
            "correct": 0,
            "reward": "Smart Decision Master Badge",
            "praise": "Excellent! You understand Needs vs. Wants!"
        },
        {
            "subject": "Nature & Science",
            "topic": "Photosynthesis",
            "image": "assets/plant.png",
            "content": "Green leaves use sunlight, water, and air to produce food for the plant.",
            "question": "What green pigment in leaves absorbs sunlight?",
            "options": ["Chlorophyll", "Melanin"],
            "correct": 0,
            "reward": "Botanist Explorer Badge",
            "praise": "Awesome science! Chlorophyll powers plant life!"
        },
        {
            "subject": "Junior Cooking & Safety",
            "topic": "No-Flame Fruit Salad",
            "image": "assets/fruit.png",
            "content": "Wash apples and bananas thoroughly, slice them using child-safe plastic cutlery, and add fresh lemon juice!",
            "question": "What is the crucial first step before preparing food?",
            "options": ["Washing hands with soap", "Eating immediately"],
            "correct": 0,
            "reward": "Junior MasterChef Medal",
            "praise": "Great hygiene! Clean hands make healthy food!"
        }
    ],
    "Classes 3-5": [
        {
            "subject": "Financial Intelligence",
            "topic": "The Power of Budgeting",
            "image": "assets/money.png",
            "content": "A Budget tracks where money goes: Income - Expenses = Savings.\nTracking expenses prevents debt and builds future security.",
            "question": "If you receive 100 rupees and spend 60 rupees, what is your savings?",
            "options": ["40 Rupees", "160 Rupees"],
            "correct": 0,
            "reward": "Junior Budget Master Trophy",
            "praise": "Outstanding math! You managed your budget perfectly!"
        },
        {
            "subject": "Universe & Space Science",
            "topic": "The Red Planet",
            "image": "assets/planets.png",
            "content": "Mars appears reddish because its surface rocks and dust are rich in iron oxide.",
            "question": "Which planet is famously known as the Red Planet?",
            "options": ["Mars", "Venus"],
            "correct": 0,
            "reward": "Cosmic Voyager Trophy",
            "praise": "Phenomenal! Mars has iron-rich red soil!"
        }
    ],
    "Classes 6-8": [
        {
            "subject": "Banking & Cyber Security",
            "topic": "Digital Banking Safety",
            "image": "assets/money.png",
            "content": "Banks pay Simple Interest on deposits: SI = (P * R * T) / 100.\nNever share OTP, PIN, or passwords with anyone.",
            "question": "What is the most important rule of digital banking safety?",
            "options": ["Never share OTP or PIN", "Share PIN on social media"],
            "correct": 0,
            "reward": "Cyber Banking Sentinel Medal",
            "praise": "Perfect! Keeping credentials private protects your funds!"
        },
        {
            "subject": "Physics & Chemistry",
            "topic": "States of Matter",
            "image": "assets/matter.png",
            "content": "Adding thermal heat increases molecular kinetic energy, causing liquid to vaporize.",
            "question": "What is the phase transition from liquid directly to gas called?",
            "options": ["Evaporation", "Sublimation"],
            "correct": 0,
            "reward": "Thermodynamics Medal",
            "praise": "Outstanding! Heat input drives vaporization!"
        }
    ],
    "Classes 9-10": [
        {
            "subject": "Advanced Finance",
            "topic": "The 50/30/20 Budgeting Rule",
            "image": "assets/money.png",
            "content": "The 50/30/20 Rule: 50% for Needs, 30% for Wants, and 20% for Savings & Investments.",
            "question": "Under the 50/30/20 rule, what percentage is allocated to Savings/Investments?",
            "options": ["20%", "70%"],
            "correct": 0,
            "reward": "Financial Freedom Laureate",
            "praise": "Brilliant! The 50/30/20 rule builds lifelong security!"
        },
        {
            "subject": "CBSE Physics & Biology",
            "topic": "Cellular Respiration",
            "image": "assets/physics.png",
            "content": "Mitochondria synthesize ATP energy molecules through cellular respiration.",
            "question": "Which organelle is universally termed the powerhouse of the cell?",
            "options": ["Mitochondria", "Ribosome"],
            "correct": 0,
            "reward": "Theoretical Scientist Trophy",
            "praise": "Genius! Mitochondria drive cellular respiration!"
        }
    ]
}

# --- SCREEN 1: LANGUAGE SELECTION ---
class LanguageScreen(Screen):
    def __init__(self, **kwargs):
        super(LanguageScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.04, 0.08, 0.16, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        layout = BoxLayout(orientation='vertical', padding=18, spacing=12)
        
        title = Label(
            text="[b]NovaQuest 3D[/b]\nSelect Language:",
            markup=True,
            font_size='22sp',
            halign='center',
            color=(1, 0.85, 0.2, 1),
            size_hint_y=0.2
        )
        layout.add_widget(title)

        grid = GridLayout(cols=2, spacing=10, size_hint_y=0.8)
        languages = [
            ("English", "en"), ("Hindi", "hi"),
            ("Bengali", "bn"), ("Tamil", "ta"),
            ("Telugu", "te"), ("Marathi", "mr"),
            ("Gujarati", "gu"), ("Kannada", "kn"),
            ("Malayalam", "ml"), ("Punjabi", "pa"),
            ("Urdu", "ur")
        ]
        for name, code in languages:
            btn = Button(
                text=name,
                font_size='16sp',
                bold=True,
                background_normal='',
                background_color=(0.14, 0.48, 0.78, 1)
            )
            btn.bind(on_release=lambda inst, n=name, c=code: self.select_language(n, c))
            grid.add_widget(btn)

        layout.add_widget(grid)
        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def select_language(self, name, code):
        AppState.selected_lang = name
        AppState.selected_code = code
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'grade_screen'

# --- SCREEN 2: GRADE SELECTION ---
class GradeScreen(Screen):
    def __init__(self, **kwargs):
        super(GradeScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.04, 0.08, 0.16, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        layout = BoxLayout(orientation='vertical', padding=18, spacing=12)
        
        title = Label(
            text="[b]NovaQuest 3D[/b]\nSelect Academic Stage:",
            markup=True,
            font_size='22sp',
            halign='center',
            color=(1, 0.85, 0.2, 1),
            size_hint_y=0.2
        )
        layout.add_widget(title)

        grid = GridLayout(cols=1, spacing=10, size_hint_y=0.8)
        grades = [
            "Pre-Nursery / KG",
            "Classes 1-2",
            "Classes 3-5",
            "Classes 6-8",
            "Classes 9-10"
        ]
        for grade in grades:
            btn = Button(
                text=grade,
                font_size='16sp',
                bold=True,
                background_normal='',
                background_color=(0.12, 0.45, 0.75, 1)
            )
            btn.bind(on_release=lambda inst, g=grade: self.select_grade(g))
            grid.add_widget(btn)

        layout.add_widget(grid)
        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def select_grade(self, grade):
        AppState.selected_grade = grade
        game_screen = self.manager.get_screen('game_screen')
        game_screen.start_session()
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game_screen'

# --- SCREEN 3: GAMEPLAY DASHBOARD ---
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.modules = []
        self.module_index = 0

        with self.canvas.before:
            Color(0.04, 0.08, 0.16, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.root_layout = FloatLayout()

        self.game_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.94, 0.96),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            spacing=6
        )

        self.header_label = Label(
            text="",
            markup=True,
            font_size='16sp',
            bold=True,
            size_hint_y=0.08,
            color=(1, 0.88, 0.25, 1)
        )
        self.game_container.add_widget(self.header_label)

        self.topic_image = Image(
            source="",
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.30
        )
        self.game_container.add_widget(self.topic_image)

        self.content_label = Label(
            text="",
            markup=True,
            font_size='13sp',
            halign='center',
            valign='middle',
            size_hint_y=0.26,
            color=(1, 1, 1, 1)
        )
        self.content_label.bind(width=lambda *x: self.content_label.setter('text_size')(self.content_label, (self.content_label.width - 16, None)))
        self.game_container.add_widget(self.content_label)

        self.options_layout = BoxLayout(orientation='vertical', spacing=6, size_hint_y=0.22)
        self.btn_a = Button(text="", font_size='14sp', bold=True, background_normal='', background_color=(0.18, 0.65, 0.35, 1))
        self.btn_b = Button(text="", font_size='14sp', bold=True, background_normal='', background_color=(0.18, 0.65, 0.35, 1))
        self.btn_a.bind(on_release=lambda x: self.check_answer(0))
        self.btn_b.bind(on_release=lambda x: self.check_answer(1))
        self.options_layout.add_widget(self.btn_a)
        self.options_layout.add_widget(self.btn_b)
        self.game_container.add_widget(self.options_layout)

        search_box = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=0.08)
        self.query_input = TextInput(
            hint_text="Ask AI (e.g. Savings, Planets)...",
            multiline=False,
            font_size='13sp',
            size_hint=(0.72, 1)
        )
        search_btn = Button(
            text="Explore Web",
            font_size='13sp',
            bold=True,
            size_hint=(0.28, 1),
            background_normal='',
            background_color=(0.92, 0.45, 0.15, 1)
        )
        search_btn.bind(on_release=self.fetch_web_knowledge)
        search_box.add_widget(self.query_input)
        search_box.add_widget(search_btn)
        self.game_container.add_widget(search_box)

        self.root_layout.add_widget(self.game_container)

        self.celeb_banner = BoxLayout(
            orientation='vertical',
            size_hint=(0.88, 0.40),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            padding=14,
            spacing=8,
            opacity=0,
            disabled=True
        )
        with self.celeb_banner.canvas.before:
            Color(0.08, 0.14, 0.24, 0.97)
            self.celeb_bg = Rectangle(size=self.celeb_banner.size, pos=self.celeb_banner.pos)
        self.celeb_banner.bind(size=self._update_celeb_bg, pos=self._update_celeb_bg)

        self.celeb_title = Label(text="CONCEPT MASTERED!", font_size='21sp', bold=True, color=(1, 0.85, 0.1, 1))
        self.celeb_msg = Label(text="", font_size='14sp', halign='center', color=(1, 1, 1, 1))
        self.celeb_msg.bind(width=lambda *x: self.celeb_msg.setter('text_size')(self.celeb_msg, (self.celeb_msg.width - 20, None)))
        self.celeb_reward = Label(text="", font_size='15sp', bold=True, color=(0.3, 0.95, 0.6, 1))

        self.celeb_banner.add_widget(self.celeb_title)
        self.celeb_banner.add_widget(self.celeb_msg)
        self.celeb_banner.add_widget(self.celeb_reward)
        self.root_layout.add_widget(self.celeb_banner)

        self.add_widget(self.root_layout)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_celeb_bg(self, instance, value):
        self.celeb_bg.pos = instance.pos
        self.celeb_bg.size = instance.size

    def start_session(self):
        self.modules = CBSE_DATA.get(AppState.selected_grade, CBSE_DATA["Classes 3-5"])
        self.module_index = 0
        self.load_topic()

    def load_topic(self):
        mod = self.modules[self.module_index]
        self.header_label.text = f"[b]{mod['subject']}[/b]: {mod['topic']} ({AppState.selected_lang})"

        img_path = mod.get("image", "")
        if img_path and os.path.exists(img_path):
            self.topic_image.source = img_path

        self.content_label.text = f"{mod['content']}\n\n[b]{mod['question']}[/b]"
        self.btn_a.text = mod["options"][0]
        self.btn_b.text = mod["options"][1]
        self.btn_a.disabled = False
        self.btn_b.disabled = False
        self.btn_a.background_color = (0.18, 0.65, 0.35, 1)
        self.btn_b.background_color = (0.18, 0.65, 0.35, 1)

    def check_answer(self, chosen_idx):
        mod = self.modules[self.module_index]
        app = App.get_running_app()
        if chosen_idx == mod["correct"]:
            self.btn_a.disabled = True
            self.btn_b.disabled = True

            if app.celebrate_sound:
                try:
                    app.celebrate_sound.play()
                except Exception:
                    pass

            self.celeb_msg.text = mod["praise"]
            self.celeb_reward.text = f"Unlocked: {mod['reward']}"

            self.celeb_banner.disabled = False
            Animation(opacity=1, duration=0.3).start(self.celeb_banner)
            Clock.schedule_once(self.next_topic, 3.0)
        else:
            self.content_label.text = f"{mod['content']}\n\n[color=ff7777]Try once more![/color]\n[b]{mod['question']}[/b]"

    def next_topic(self, dt):
        Animation(opacity=0, duration=0.25).start(self.celeb_banner)
        self.celeb_banner.disabled = True
        self.module_index = (self.module_index + 1) % len(self.modules)
        self.load_topic()

    def fetch_web_knowledge(self, instance):
        raw_query = self.query_input.text.strip()
        query = re.sub(r"[^\w\s-]", "", raw_query)[:50]
        if not query:
            return

        if bool(BLOCKED_KEYWORDS.search(query.lower())):
            self.header_label.text = "Safety Guard Active"
            self.content_label.text = "This topic is restricted for kids. Let's explore science, space, money, or manners!"
            self.query_input.text = ""
            return

        self.header_label.text = f"Exploring: {query.title()}"
        self.content_label.text = "Connecting to safe knowledge base..."
        threading.Thread(target=self._async_fetch, args=(query,), daemon=True).start()

    def _async_fetch(self, query):
        safe_q = urllib.parse.quote(query)
        url = f"https://{AppState.selected_code}.wikipedia.org/api/rest_v1/page/summary/{safe_q}"
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'NovaQuestKids3D/1.0 (Educational Safe Browser)'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                extract = data.get('extract', '')
                if extract:
                    summary = extract[:220] + "..." if len(extract) > 220 else extract
                    self.update_web_fact(query, summary)
                else:
                    self.update_web_fact(query, f"{query.title()} is an important concept in our universe!")
        except Exception:
            self.update_web_fact(query, f"{query.title()} is a great topic to explore in science and nature!")

    @mainthread
    def update_web_fact(self, topic, summary):
        self.header_label.text = f"Discovery: {topic.title()}"
        self.content_label.text = summary
        self.query_input.text = ""
        app = App.get_running_app()
        if app.celebrate_sound:
            try:
                app.celebrate_sound.play()
            except Exception:
                pass

# --- MAIN APPLICATION ENTRY ---
class NovaQuestApp(App):
    def build(self):
        self.bg_music = None
        self.celebrate_sound = None
        self.init_audio()

        sm = ScreenManager()
        sm.add_widget(LanguageScreen(name='language_screen'))
        sm.add_widget(GradeScreen(name='grade_screen'))
        sm.add_widget(GameScreen(name='game_screen'))
        return sm

    def init_audio(self):
        try:
            music_path = 'assets/soothing_lullaby.wav'
            if os.path.exists(music_path):
                self.bg_music = SoundLoader.load(music_path)
                if self.bg_music:
                    self.bg_music.loop = True
                    self.bg_music.volume = 0.22
                    self.bg_music.play()

            sound_path = 'assets/celebrate.wav'
            if os.path.exists(sound_path):
                self.celebrate_sound = SoundLoader.load(sound_path)
                if self.celebrate_sound:
                    self.celebrate_sound.volume = 0.85
        except Exception:
            pass

if __name__ == '__main__':
    NovaQuestApp().run()

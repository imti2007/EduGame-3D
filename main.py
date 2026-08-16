import os
import json
import threading
import urllib.request
import urllib.parse
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.clock import Clock, mainthread

BLOCKED_KEYWORDS = {
    "porn", "xxx", "sex", "nude", "naked", "erotic", "nsfw", "adult",
    "hentai", "penis", "vagina", "boobs", "breast", "intercourse", "fetish",
    "orgasm", "strip", "masturbat", "escort", "gambling", "casino"
}

CLASS_CURRICULUM = {
    "Class 1": [
        {
            "animal": "Tiger",
            "image": "assets/tiger.png",
            "fact": "Tigers have bright orange & black stripes to camouflage in tall grass!",
            "question": "What does a hungry tiger eat?",
            "options": ["Fresh Meat (Carnivore)", "Grass & Leaves"],
            "correct": 0,
            "reward": "Baby Tiger Badge",
            "praise": "Super job! You fed the tiger healthy food!"
        },
        {
            "animal": "Elephant",
            "image": "assets/elephant.png",
            "fact": "Elephants use their long trunk like a hand to pick fresh fruits!",
            "question": "What is an elephant's favorite food?",
            "options": ["Fresh Leaves & Fruit", "Fish & Meat"],
            "correct": 0,
            "reward": "Savanna Trumpet Melody",
            "praise": "Wonderful! The elephant trumpets happily!"
        }
    ],
    "Class 2": [
        {
            "animal": "Giraffe",
            "image": "assets/giraffe.png",
            "fact": "Giraffes are the tallest animals on Earth with long 6-foot legs!",
            "question": "How do giraffes reach leaves on tall trees?",
            "options": ["Long Flexible Neck", "Climbing Trees"],
            "correct": 0,
            "reward": "Acacia Master Badge",
            "praise": "Great thinking! The giraffe reaches the highest leaves!"
        },
        {
            "animal": "Zebra",
            "image": "assets/zebra.png",
            "fact": "Every zebra has a completely unique stripe pattern like a fingerprint!",
            "question": "Why do zebras stick together in large herds?",
            "options": ["Protection from Predators", "To Sing Together"],
            "correct": 0,
            "reward": "Savanna Harmony Medal",
            "praise": "Brilliant! The zebra herd stays safe and united!"
        }
    ],
    "Class 3": [
        {
            "animal": "Cheetah",
            "image": "assets/cheetah.png",
            "fact": "Cheetahs can sprint from 0 to 60 mph in just 3 seconds!",
            "question": "What helps a cheetah balance when sprinting?",
            "options": ["Long Muscular Tail", "Heavy Ears"],
            "correct": 0,
            "reward": "Golden Speedster Medal",
            "praise": "Phenomenal! Cheetah sprint mechanics mastered!"
        },
        {
            "animal": "Kangaroo",
            "image": "assets/kangaroo.png",
            "fact": "Mother kangaroos carry their baby joeys in a special front pouch.",
            "question": "What group of mammals do kangaroos belong to?",
            "options": ["Marsupials", "Reptiles"],
            "correct": 0,
            "reward": "Outback Explorer Crown",
            "praise": "Excellent! Marsupial biology unlocked!"
        }
    ],
    "Class 4-5": [
        {
            "animal": "African Elephant",
            "image": "assets/elephant.png",
            "fact": "Elephants send low-frequency vibrations through the ground over miles.",
            "question": "What is a species called that shapes its entire ecosystem?",
            "options": ["Keystone Species", "Isolated Species"],
            "correct": 0,
            "reward": "Ecosystem Architect Trophy",
            "praise": "Outstanding! Keystone ecology principle understood!"
        },
        {
            "animal": "Snow Leopard",
            "image": "assets/snow_leopard.png",
            "fact": "Snow leopards have wide paws that act as natural snowshoes in mountains.",
            "question": "What type of biological adaptation are snowshoe paws?",
            "options": ["Structural Adaptation", "Behavioral Drift"],
            "correct": 0,
            "reward": "Highland Biologist Crown",
            "praise": "Magnificent! Advanced wildlife science completed!"
        }
    ]
}

class SafariKidGame(FloatLayout):
    def __init__(self, **kwargs):
        super(SafariKidGame, self).__init__(**kwargs)

        self.selected_class = None
        self.current_levels = []
        self.level_index = 0

        # Background Canvas
        with self.canvas.before:
            Color(0.07, 0.18, 0.12, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.bg_music = None
        self.celebrate_sound = None
        self.init_audio()

        # 1. Class Selection Screen
        self.class_screen = BoxLayout(
            orientation='vertical',
            size_hint=(0.88, 0.75),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=14
        )

        title = Label(
            text="[b]WildPals AI: Jungle Quest[/b]\nSelect Your Class to Start:",
            markup=True,
            font_size='22sp',
            halign='center',
            color=(1, 0.88, 0.25, 1)
        )
        self.class_screen.add_widget(title)

        grid = GridLayout(cols=2, spacing=12, size_hint=(1, 0.6))
        for grade in ["Class 1", "Class 2", "Class 3", "Class 4-5"]:
            btn = Button(
                text=grade,
                font_size='18sp',
                bold=True,
                background_normal='',
                background_color=(0.18, 0.56, 0.88, 1)
            )
            btn.bind(on_release=lambda instance, g=grade: self.start_for_class(g))
            grid.add_widget(btn)

        self.class_screen.add_widget(grid)
        self.add_widget(self.class_screen)

        # 2. Main Gameplay Container
        self.game_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.92, 0.94),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            spacing=6,
            opacity=0
        )

        self.title_label = Label(
            text="",
            markup=True,
            font_size='18sp',
            bold=True,
            size_hint_y=0.08,
            color=(1, 0.88, 0.25, 1)
        )
        self.game_container.add_widget(self.title_label)

        # Animal Image Display Card
        self.animal_image = Image(
            source="",
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.28
        )
        self.game_container.add_widget(self.animal_image)

        # Educational Fact & Question Label
        self.fact_label = Label(
            text="",
            markup=True,
            font_size='14sp',
            halign='center',
            valign='middle',
            size_hint_y=0.22,
            color=(1, 1, 1, 1)
        )
        self.fact_label.bind(width=lambda *x: self.fact_label.setter('text_size')(self.fact_label, (self.fact_label.width - 16, None)))
        self.game_container.add_widget(self.fact_label)

        # Option Buttons
        self.options_layout = BoxLayout(orientation='vertical', spacing=6, size_hint_y=0.26)
        self.btn_a = Button(
            text="",
            font_size='15sp',
            bold=True,
            background_normal='',
            background_color=(0.18, 0.65, 0.35, 1)
        )
        self.btn_b = Button(
            text="",
            font_size='15sp',
            bold=True,
            background_normal='',
            background_color=(0.18, 0.65, 0.35, 1)
        )
        self.btn_a.bind(on_release=lambda x: self.check_answer(0))
        self.btn_b.bind(on_release=lambda x: self.check_answer(1))
        self.options_layout.add_widget(self.btn_a)
        self.options_layout.add_widget(self.btn_b)
        self.game_container.add_widget(self.options_layout)

        # Safe Web Search Bar
        search_box = BoxLayout(orientation='horizontal', spacing=6, size_hint_y=0.10)
        self.query_input = TextInput(
            hint_text="Ask WildPals AI (e.g. Lion, Sun, Mars)...",
            multiline=False,
            font_size='13sp',
            size_hint=(0.7, 1)
        )
        search_btn = Button(
            text="Explore Web",
            font_size='13sp',
            bold=True,
            size_hint=(0.3, 1),
            background_normal='',
            background_color=(0.92, 0.45, 0.15, 1)
        )
        search_btn.bind(on_release=self.fetch_web_knowledge)
        search_box.add_widget(self.query_input)
        search_box.add_widget(search_btn)
        self.game_container.add_widget(search_box)

        self.add_widget(self.game_container)

        # 3. Celebration Modal Popup
        self.celeb_banner = BoxLayout(
            orientation='vertical',
            size_hint=(0.88, 0.42),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            padding=16,
            spacing=8,
            opacity=0
        )
        with self.celeb_banner.canvas.before:
            Color(0.10, 0.15, 0.22, 0.96)
            self.celeb_bg = Rectangle(size=self.celeb_banner.size, pos=self.celeb_banner.pos)
        self.celeb_banner.bind(size=self._update_celeb_bg, pos=self._update_celeb_bg)

        self.celeb_title = Label(
            text="GREAT WORK!",
            font_size='22sp',
            bold=True,
            color=(1, 0.85, 0.1, 1)
        )
        self.celeb_msg = Label(
            text="",
            font_size='15sp',
            halign='center',
            color=(1, 1, 1, 1)
        )
        self.celeb_msg.bind(width=lambda *x: self.celeb_msg.setter('text_size')(self.celeb_msg, (self.celeb_msg.width - 20, None)))
        
        self.celeb_reward = Label(
            text="",
            font_size='15sp',
            bold=True,
            color=(0.3, 0.95, 0.6, 1)
        )

        self.celeb_banner.add_widget(self.celeb_title)
        self.celeb_banner.add_widget(self.celeb_msg)
        self.celeb_banner.add_widget(self.celeb_reward)
        self.add_widget(self.celeb_banner)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_celeb_bg(self, instance, value):
        self.celeb_bg.pos = instance.pos
        self.celeb_bg.size = instance.size

    def init_audio(self):
        music_path = 'assets/soothing_lullaby.wav'
        if os.path.exists(music_path):
            self.bg_music = SoundLoader.load(music_path)
            if self.bg_music:
                self.bg_music.loop = True
                self.bg_music.volume = 0.25
                self.bg_music.play()

        sound_path = 'assets/celebrate.wav'
        if os.path.exists(sound_path):
            self.celebrate_sound = SoundLoader.load(sound_path)
            if self.celebrate_sound:
                self.celebrate_sound.volume = 0.75

    def is_safe_query(self, text):
        clean = text.lower().strip()
        return not any(bad_word in clean for bad_word in BLOCKED_KEYWORDS)

    def fetch_web_knowledge(self, instance):
        query = self.query_input.text.strip()
        if not query:
            return

        if not self.is_safe_query(query):
            self.title_label.text = "Child Safety Guard"
            self.fact_label.text = "This search topic is not suitable for kids. Let's explore wildlife!"
            self.query_input.text = ""
            return

        self.title_label.text = f"Exploring: {query.title()}"
        self.fact_label.text = "Fetching safe nature facts from the web..."
        threading.Thread(target=self._async_fetch, args=(query,), daemon=True).start()

    def _async_fetch(self, query):
        safe_q = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_q}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'WildPalsAIApp/1.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode())
                extract = data.get('extract', '')
                if extract:
                    summary = extract[:200] + "..." if len(extract) > 200 else extract
                    self.update_web_fact(query, summary)
                else:
                    self.update_web_fact(query, "A wonderful part of our planet's wildlife ecosystem!")
        except Exception:
            self.update_web_fact(query, f"{query.title()} is a fascinating part of nature to explore!")

    @mainthread
    def update_web_fact(self, topic, summary):
        self.title_label.text = f"Nature Fact: {topic.title()}"
        self.fact_label.text = summary
        self.query_input.text = ""
        if self.celebrate_sound:
            self.celebrate_sound.play()

    def start_for_class(self, grade):
        self.selected_class = grade
        self.current_levels = CLASS_CURRICULUM[grade]
        self.level_index = 0

        self.class_screen.opacity = 0
        self.class_screen.disabled = True
        self.game_container.opacity = 1
        self.load_question()

    def load_question(self):
        lvl = self.current_levels[self.level_index]
        self.title_label.text = f"{lvl['animal']} ({self.selected_class})"
        self.animal_image.source = lvl["image"]
        self.animal_image.reload()
        self.fact_label.text = f"{lvl['fact']}\n\n[b]{lvl['question']}[/b]"
        self.btn_a.text = lvl["options"][0]
        self.btn_b.text = lvl["options"][1]
        self.btn_a.disabled = False
        self.btn_b.disabled = False

    def check_answer(self, chosen_idx):
        lvl = self.current_levels[self.level_index]
        if chosen_idx == lvl["correct"]:
            self.btn_a.disabled = True
            self.btn_b.disabled = True

            if self.celebrate_sound:
                self.celebrate_sound.play()

            self.celeb_msg.text = lvl["praise"]
            self.celeb_reward.text = f"Unlocked: {lvl['reward']}"

            Animation(opacity=1, duration=0.3).start(self.celeb_banner)
            Clock.schedule_once(self.next_level, 3.2)
        else:
            self.fact_label.text = f"{lvl['fact']}\n\n[color=ff6666]Not quite! Try again:[/color]\n[b]{lvl['question']}[/b]"

    def next_level(self, dt):
        Animation(opacity=0, duration=0.25).start(self.celeb_banner)
        self.level_index = (self.level_index + 1) % len(self.current_levels)
        self.load_question()

class WildPalsApp(App):
    def build(self):
        return SafariKidGame()

if __name__ == '__main__':
    WildPalsApp().run()

import os
import json
import threading
import urllib.request
import urllib.parse
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.animation import Animation
from kivy.clock import Clock, mainthread

# Strict Child Safety Blocklist
BLOCKED_KEYWORDS = {
    "porn", "xxx", "sex", "nude", "naked", "erotic", "nsfw", "adult",
    "hentai", "penis", "vagina", "boobs", "breast", "intercourse", "fetish",
    "orgasm", "strip", "masturbat", "escort", "gambling", "casino"
}

CLASS_CURRICULUM = {
    "Class 1": [
        {
            "animal": "Tiger",
            "fact": "Tigers have orange and black stripes to camouflage in tall grass!",
            "question": "What does a hungry tiger eat?",
            "options": ["Fresh Meat (Carnivore)", "Grass & Leaves"],
            "correct": 0,
            "reward": "Baby Tiger Badge",
            "praise": "Super job! You fed the tiger healthy food!"
        }
    ],
    "Class 2": [
        {
            "animal": "Giraffe",
            "fact": "Giraffes are the tallest mammals with 6-foot long legs!",
            "question": "How do giraffes reach leaves on high branches?",
            "options": ["Long Flexible Neck", "Climbing Trees"],
            "correct": 0,
            "reward": "Savanna Explorer Badge",
            "praise": "Great thinking! The giraffe reaches the top leaves!"
        }
    ],
    "Class 3": [
        {
            "animal": "Cheetah",
            "fact": "Cheetahs can sprint from 0 to 60 mph in just 3 seconds!",
            "question": "What gives cheetahs steering balance during sprints?",
            "options": ["Long Muscular Tail", "Heavy Ears"],
            "correct": 0,
            "reward": "Speedster Medal",
            "praise": "Phenomenal! Cheetah sprint mechanics mastered!"
        }
    ],
    "Class 4-5": [
        {
            "animal": "African Elephant",
            "fact": "Elephants communicate using low-frequency infrasound through the earth.",
            "question": "What ecological role defines an elephant shaping its habitat?",
            "options": ["Keystone Species", "Isolated Species"],
            "correct": 0,
            "reward": "Ecosystem Architect Trophy",
            "praise": "Outstanding! Keystone ecology principle understood!"
        }
    ]
}

class SafariKidGame(FloatLayout):
    def __init__(self, **kwargs):
        super(SafariKidGame, self).__init__(**kwargs)

        self.selected_class = None
        self.current_levels = []
        self.level_index = 0

        self.bg_music = None
        self.celebrate_sound = None
        self.init_audio()

        # 1. Background Video Layer
        video_path = 'assets/safari_video.mp4'
        if os.path.exists(video_path):
            self.video = Video(
                source=video_path,
                state='play',
                options={'eos': 'loop'},
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            self.add_widget(self.video)

        # 2. Class Selection Screen
        self.class_screen = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=10
        )
        title = Label(
            text="[b]Safari Explorer AI[/b]\nSelect Your Class to Start:",
            markup=True,
            font_size='20sp',
            halign='center',
            color=(1, 0.9, 0.2, 1)
        )
        self.class_screen.add_widget(title)

        grid = GridLayout(cols=2, spacing=8, size_hint=(1, 0.6))
        for grade in ["Class 1", "Class 2", "Class 3", "Class 4-5"]:
            btn = Button(text=grade, font_size='18sp', background_color=(0.2, 0.6, 0.9, 1))
            btn.bind(on_release=lambda instance, g=grade: self.start_for_class(g))
            grid.add_widget(btn)

        self.class_screen.add_widget(grid)
        self.add_widget(self.class_screen)

        # 3. Main Gameplay & Live Safari Search Container
        self.game_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.55),
            pos_hint={'center_x': 0.5, 'y': 0.03},
            spacing=6,
            opacity=0
        )

        self.fact_label = Label(
            text="",
            markup=True,
            font_size='15sp',
            halign='center',
            color=(1, 1, 1, 1)
        )
        self.game_container.add_widget(self.fact_label)

        # Action Buttons
        self.options_layout = BoxLayout(orientation='vertical', spacing=4, size_hint=(1, 0.38))
        self.btn_a = Button(text="", font_size='15sp', background_color=(0.18, 0.65, 0.35, 1))
        self.btn_b = Button(text="", font_size='15sp', background_color=(0.18, 0.65, 0.35, 1))
        self.btn_a.bind(on_release=lambda x: self.check_answer(0))
        self.btn_b.bind(on_release=lambda x: self.check_answer(1))
        self.options_layout.add_widget(self.btn_a)
        self.options_layout.add_widget(self.btn_b)
        self.game_container.add_widget(self.options_layout)

        # Safe Web Search Input Bar
        search_box = BoxLayout(orientation='horizontal', spacing=6, size_hint=(1, 0.22))
        self.query_input = TextInput(
            hint_text="Ask Safari AI (e.g. Lion, Sun, Mars)...",
            multiline=False,
            font_size='14sp',
            size_hint=(0.7, 1)
        )
        search_btn = Button(
            text="Explore Web",
            font_size='14sp',
            size_hint=(0.3, 1),
            background_color=(0.9, 0.45, 0.15, 1)
        )
        search_btn.bind(on_release=self.fetch_web_knowledge)
        search_box.add_widget(self.query_input)
        search_box.add_widget(search_btn)
        self.game_container.add_widget(search_box)

        self.add_widget(self.game_container)

        # 4. Celebration Modal Banner
        self.celeb_banner = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, 0.35),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            opacity=0,
            spacing=4
        )
        self.celeb_title = Label(text="★ LEVEL COMPLETED! ★", font_size='20sp', bold=True, color=(1, 0.85, 0.1, 1))
        self.celeb_msg = Label(text="", font_size='15sp', halign='center', color=(1, 1, 1, 1))
        self.celeb_reward = Label(text="", font_size='15sp', color=(0.3, 0.95, 0.6, 1))

        self.celeb_banner.add_widget(self.celeb_title)
        self.celeb_banner.add_widget(self.celeb_msg)
        self.celeb_banner.add_widget(self.celeb_reward)
        self.add_widget(self.celeb_banner)

        Window.bind(on_resize=self.on_window_resize)

    def init_audio(self):
        music_path = 'assets/soothing_lullaby.wav'
        if os.path.exists(music_path):
            self.bg_music = SoundLoader.load(music_path)
            if self.bg_music:
                self.bg_music.loop = True
                self.bg_music.volume = 0.3
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
            self.fact_label.text = "[b]Safari AI Safe Guard[/b]\nThis topic is not suitable for children. Let's learn about wild animals and nature!"
            self.query_input.text = ""
            return

        self.fact_label.text = f"Exploring web knowledge for [b]{query}[/b]..."
        threading.Thread(target=self._async_fetch, args=(query,), daemon=True).start()

    def _async_fetch(self, query):
        safe_q = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_q}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SafariExplorerKidsApp/1.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode())
                extract = data.get('extract', '')
                if extract:
                    summary = extract[:220] + "..." if len(extract) > 220 else extract
                    self.update_web_fact(query, summary)
                else:
                    self.update_web_fact(query, "Explore more wildlife facts by completing your safari mission!")
        except Exception:
            self.update_web_fact(query, f"Fascinating fact: {query} plays an important role in nature!")

    @mainthread
    def update_web_fact(self, topic, summary):
        self.fact_label.text = f"[b]{topic.title()}[/b]\n{summary}"
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
        self.fact_label.text = f"[b]{lvl['animal']} ({self.selected_class})[/b]\n{lvl['fact']}\n\n[b]{lvl['question']}[/b]"
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

            Animation(opacity=1, duration=0.4).start(self.celeb_banner)
            Clock.schedule_once(self.next_level, 3.0)
        else:
            self.fact_label.text = f"[b]{lvl['animal']}[/b]\nAlmost! Try again!\n\n[b]{lvl['question']}[/b]"

    def next_level(self, dt):
        Animation(opacity=0, duration=0.3).start(self.celeb_banner)
        self.level_index = (self.level_index + 1) % len(self.current_levels)
        self.load_question()

    def on_window_resize(self, instance, width, height):
        if width > height:
            self.game_container.size_hint = (0.7, 0.52)
            self.game_container.pos_hint = {'center_x': 0.5, 'y': 0.02}
        else:
            self.game_container.size_hint = (0.9, 0.55)
            self.game_container.pos_hint = {'center_x': 0.5, 'y': 0.03}

class SafariApp(App):
    def build(self):
        return SafariKidGame()

if __name__ == '__main__':
    SafariApp().run()
        

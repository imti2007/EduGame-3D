import os
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock

class SafariKidGame(FloatLayout):
    def __init__(self, **kwargs):
        super(SafariKidGame, self).__init__(**kwargs)

        self.levels = [
            {
                "animal": "Tiger (Carnivore)",
                "fact": "Protein builds strong tiger muscles!",
                "btn_text": "Feed Meat to Tiger",
                "reward": "Unlocked: Cello Instrument!",
                "praise": "Awesome! The tiger is strong and healthy!"
            },
            {
                "animal": "Elephant (Herbivore)",
                "fact": "Elephants love crisp leaves and fresh fruits!",
                "btn_text": "Feed Fresh Leaves to Elephant",
                "reward": "Unlocked: Flute Melody!",
                "praise": "Splendid! The elephant trumpets happily!"
            },
            {
                "animal": "Giraffe (Herbivore)",
                "fact": "Long necks help giraffes reach tall acacia trees!",
                "btn_text": "Pick Tall Acacia Leaves",
                "reward": "Unlocked: Safari Master Badge!",
                "praise": "Hooray! You completed all safari adventures!"
            }
        ]
        self.current_level = 0

        # Background Audio & Effects
        self.bg_music = None
        self.celebrate_sound = None
        self.init_audio()

        # Responsive Video Player
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

        # Interactive Controls Overlay
        self.ui_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, 0.35),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            spacing=8
        )

        self.fact_label = Label(
            text="",
            markup=True,
            font_size='18sp',
            halign='center',
            color=(1, 1, 1, 1)
        )

        self.action_btn = Button(
            text="",
            font_size='18sp',
            size_hint=(1, 0.45),
            background_color=(0.18, 0.65, 0.35, 1)
        )
        self.action_btn.bind(on_release=self.on_complete_level)

        self.ui_container.add_widget(self.fact_label)
        self.ui_container.add_widget(self.action_btn)
        self.add_widget(self.ui_container)

        # Celebration Modal Banner
        self.celeb_banner = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.35),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            opacity=0,
            spacing=6
        )

        self.celeb_title = Label(
            text="★ LEVEL COMPLETED! ★",
            font_size='22sp',
            bold=True,
            color=(1, 0.85, 0.1, 1)
        )
        self.celeb_msg = Label(
            text="",
            font_size='17sp',
            halign='center',
            color=(1, 1, 1, 1)
        )
        self.celeb_reward = Label(
            text="",
            font_size='16sp',
            color=(0.3, 0.95, 0.6, 1)
        )

        self.celeb_banner.add_widget(self.celeb_title)
        self.celeb_banner.add_widget(self.celeb_msg)
        self.celeb_banner.add_widget(self.celeb_reward)
        self.add_widget(self.celeb_banner)

        # Handle Orientation Changes
        Window.bind(on_resize=self.on_window_resize)
        self.load_level(self.current_level)

    def init_audio(self):
        music_path = 'assets/soothing_lullaby.mp3'
        if os.path.exists(music_path):
            self.bg_music = SoundLoader.load(music_path)
            if self.bg_music:
                self.bg_music.loop = True
                self.bg_music.volume = 0.35
                self.bg_music.play()

        sound_path = 'assets/celebrate.mp3'
        if os.path.exists(sound_path):
            self.celebrate_sound = SoundLoader.load(sound_path)
            if self.celebrate_sound:
                self.celebrate_sound.volume = 0.7

    def load_level(self, idx):
        lvl = self.levels[idx]
        self.fact_label.text = f"[b]{lvl['animal']}[/b]\n{lvl['fact']}"
        self.action_btn.text = lvl["btn_text"]
        self.action_btn.disabled = False

    def on_complete_level(self, instance):
        self.action_btn.disabled = True
        lvl = self.levels[self.current_level]

        if self.celebrate_sound:
            self.celebrate_sound.play()

        self.celeb_msg.text = lvl["praise"]
        self.celeb_reward.text = f"★ {lvl['reward']} ★"

        anim = Animation(opacity=1, duration=0.4)
        anim.start(self.celeb_banner)

        Clock.schedule_once(self.next_level_transition, 3.0)

    def next_level_transition(self, dt):
        anim_out = Animation(opacity=0, duration=0.3)
        anim_out.start(self.celeb_banner)

        self.current_level = (self.current_level + 1) % len(self.levels)
        self.load_level(self.current_level)

    def on_window_resize(self, instance, width, height):
        if width > height:
            # Landscape
            self.ui_container.size_hint = (0.6, 0.32)
            self.ui_container.pos_hint = {'center_x': 0.5, 'y': 0.04}
            self.celeb_banner.size_hint = (0.6, 0.32)
        else:
            # Portrait
            self.ui_container.size_hint = (0.85, 0.25)
            self.ui_container.pos_hint = {'center_x': 0.5, 'y': 0.08}
            self.celeb_banner.size_hint = (0.85, 0.25)

class SafariApp(App):
    def build(self):
        return SafariKidGame()

if __name__ == '__main__':
    SafariApp().run()

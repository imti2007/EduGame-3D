import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class EduGameApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.label = Label(
            text="🌿 Animal AI & Diet Safari\n[Class 4 Science & AI]",
            font_size='18sp',
            halign='center'
        )
        self.layout.add_widget(self.label)

        self.btn = Button(
            text="🦁 Tiger eats Meat (Carnivore)",
            size_hint=(1, 0.3),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.btn.bind(on_press=self.check_answer)
        self.layout.add_widget(self.btn)

        return self.layout

    def check_answer(self, instance):
        self.label.text = "✅ Correct! Protein builds tiger muscle.\n⭐ Unlocked: Cello Instrument!"

if __name__ == '__main__':
    EduGameApp().run()

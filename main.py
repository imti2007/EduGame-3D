import os
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.video import Video
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.clock import Clock, mainthread

# Localized UI Labels
LANG_CONFIG = {
    "English": {
        "code": "en",
        "select_class": "Select Grade / Academic Stage:",
        "search_hint": "Ask AI (e.g. Savings, Gravity, Solar System)...",
        "search_btn": "Explore Web",
        "great_work": "CONCEPT MASTERED!",
        "unlocked": "Unlocked",
        "safety_title": "Safety Guard Active",
        "safety_msg": "This topic is restricted for kids. Let's explore science, space, money, or manners!",
        "try_again": "Try once more!",
        "grades": [
            ("Pre-Nursery / KG (Rhymes, Piggy Banks & Manners)", "Pre-Nursery / KG"),
            ("Classes 1-2 (Needs vs Wants, Nature & Cooking)", "Classes 1-2"),
            ("Classes 3-5 (Budgeting, Universe & Science)", "Classes 3-5"),
            ("Classes 6-8 (Banking, Interest & Physics)", "Classes 6-8"),
            ("Classes 9-10 (Investing, 50/30/20 Rule & CBSE Science)", "Classes 9-10")
        ]
    },
    "हिन्दी (Hindi)": {
        "code": "hi",
        "select_class": "अपनी कक्षा / स्तर चुनें:",
        "search_hint": "पूछें (जैसे बचत, बैंक, गुरुत्वाकर्षण, ग्रह)...",
        "search_btn": "खोजें",
        "great_work": "अद्भुत सफलता!",
        "unlocked": "प्राप्त हुआ",
        "safety_title": "सुरक्षा शील्ड सक्रिय",
        "safety_msg": "यह विषय बच्चों के लिए उपयुक्त नहीं है। आइए विज्ञान, बचत और प्रकृति सीखें!",
        "try_again": "फिर से प्रयास करें!",
        "grades": [
            ("प्री-नर्सरी / केजी (गुल्लक, कविताएं व शिष्टाचार)", "Pre-Nursery / KG"),
            ("कक्षा 1-2 (ज़रूरत बनाम इच्छाएं, प्रकृति व कुकिंग)", "Classes 1-2"),
            ("कक्षा 3-5 (बजट बनाना, अंतरिक्ष व विज्ञान)", "Classes 3-5"),
            ("कक्षा 6-8 (बैंकिंग, ब्याज व भौतिकी)", "Classes 6-8"),
            ("कक्षा 9-10 (निवेश, 50/30/20 नियम व सीबीएसई विज्ञान)", "Classes 9-10")
        ]
    },
    "বাংলা (Bengali)": {
        "code": "bn",
        "select_class": "আপনার শ্রেণী নির্বাচন করুন:",
        "search_hint": "জানতে চান লিখুন (যেমন সঞ্চয়, ব্যাংক, বিজ্ঞান)...",
        "search_btn": "অনুসন্ধান",
        "great_work": "দুর্দান্ত সাফল্য!",
        "unlocked": "আনলক হয়েছে",
        "safety_title": "নিরাপত্তা ফিল্টার সক্রিয়",
        "safety_msg": "এই বিষয়টি শিশুদের জন্য নয়। আসুন আর্থিক জ্ঞান ও বিজ্ঞান শিখি!",
        "try_again": "আবার চেষ্টা করুন!",
        "grades": [
            ("প্রি-নার্সারি / কেজি (মাটির ব্যাংক, ছড়া ও শিষ্টাচার)", "Pre-Nursery / KG"),
            ("ক্লাস ১-২ (প্রয়োজন বনাম শখ, প্রকৃতি ও রান্না)", "Classes 1-2"),
            ("ক্লাস ৩-৫ (বাজেট তৈরি, মহাকাশ ও বিজ্ঞান)", "Classes 3-5"),
            ("ক্লাস ৬-৮ (ব্যাংক অ্যাকাউন্ট, সুদ ও পদার্থবিজ্ঞান)", "Classes 6-8"),
            ("ক্লাস ৯-১০ (বিনিয়োগ, ৫০/৩০/২০ নিয়ম ও বিজ্ঞান)", "Classes 9-10")
        ]
    }
}

# CBSE + Financial Literacy Curriculum
MULTILINGUAL_CURRICULUM = {
    "Pre-Nursery / KG": {
        "English": [
            {
                "subject": "Financial Literacy for Kids",
                "topic": "The Magic Piggy Bank",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "Coin by coin, save every day!\nDon't spend it all right away!\nWhen you drop coins in your little piggy bank,\nYou build smart habits you'll always thank!",
                "question": "What is the best place to keep your spare coins safe?",
                "options": ["In a Piggy Bank", "Throwing them on the floor"],
                "correct": 0,
                "reward": "Smart Saver Piggy Badge",
                "praise": "Super saver! You are building great financial habits!"
            },
            {
                "subject": "Catchy Rhymes",
                "topic": "The Solar Zoom Rhyme",
                "video": "assets/intro_universe.mp4",
                "image": "assets/sun.png",
                "content": "Zoom, zoom, zoom, we're flying to the Sun!\nBright and warm for everyone!\nMercury is fast and neat,\nJupiter is huge and sweet!",
                "question": "Which big shining star warms our Earth?",
                "options": ["The Sun", "The Moon"],
                "correct": 0,
                "reward": "Little Astronomer Badge",
                "praise": "Brilliant! You know our glowing Sun!"
            }
        ],
        "हिन्दी (Hindi)": [
            {
                "subject": "बच्चों की वित्तीय साक्षरता",
                "topic": "मेरी प्यारी गुल्लक",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "सिक्का-सिक्का रोज बचाएं,\nगुल्लक में हम डालते जाएं!\nफिजूलखर्ची कभी न करना,\nसही समय पर बचत ही अपनाना!",
                "question": "अपनी जेब खर्च के सिक्कों को सुरक्षित रखने की सबसे अच्छी जगह क्या है?",
                "options": ["गुल्लक (Piggy Bank)", "सड़क पर फेंक देना"],
                "correct": 0,
                "reward": "स्मार्ट बचतकर्ता बैज",
                "praise": "बहुत खूब! बचत करना बहुत अच्छी आदत है!"
            }
        ],
        "বাংলা (Bengali)": [
            {
                "subject": "শিশুদের আর্থিক সচেতনতা",
                "topic": "আমার মাটির ব্যাংক",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "একটি একটি কয়েন জমাই,\nমাটির ব্যাংকে তুলে রাখি ভাই!\nঅপচয় করব না কোনোমতে,\nসঞ্চয় শেখায় সমৃদ্ধির পথে!",
                "question": "জমানো কয়েন সুরক্ষিত রাখার সেরা উপায় কী?",
                "options": ["মাটির ব্যাংক / পিগি ব্যাংক", "রাস্তায় ফেলে দেওয়া"],
                "correct": 0,
                "reward": "স্মার্ট সেভার ব্যাজ",
                "praise": "দারুণ সঞ্চয়ী মনোভাব! তুমি সেরা সঞ্চয়কারী!"
            }
        ]
    },
    "Classes 1-2": {
        "English": [
            {
                "subject": "Financial Literacy",
                "topic": "Needs vs. Wants",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "A 'NEED' is essential for survival (healthy food, water, warm clothes, books).\nA 'WANT' is something nice to have but not essential (fancy video games, extra candy). Always fulfill Needs before Wants!",
                "question": "Which of these is a basic 'NEED' for every student?",
                "options": ["Healthy Nutritious Food", "Extra Toy Cars"],
                "correct": 0,
                "reward": "Smart Decision Master Badge",
                "praise": "Excellent! You understand Needs vs. Wants!"
            }
        ],
        "हिन्दी (Hindi)": [
            {
                "subject": "वित्तीय साक्षरता",
                "topic": "ज़रूरत बनाम इच्छा (Needs vs Wants)",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "'ज़रूरत' वह है जिसके बिना हम रह नहीं सकते (पौष्टिक खाना, किताबें, दवाएं)। 'इच्छा' वह है जो सिर्फ शौक के लिए है। पहले ज़रूरतों को पूरा करना चाहिए!",
                "question": "इनमें से कौन सी एक बुनियादी 'ज़रूरत' (Need) है?",
                "options": ["पौष्टिक भोजन व पढ़ाई की किताबें", "अतिरिक्त खिलौने"],
                "correct": 0,
                "reward": "समझदार उपभोक्ता पदक",
                "praise": "शानदार! आपने ज़रूरत और इच्छा का अंतर समझ लिया!"
            }
        ],
        "বাংলা (Bengali)": [
            {
                "subject": "আর্থিক শিক্ষা",
                "topic": "প্রয়োজন বনাম শখ",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "'প্রয়োজন' হলো যা ছাড়া বাঁচা যায় না (পুষ্টিকর খাবার, বই, জামাকাপড়)। 'শখ' হলো যা না থাকলেও চলে (অতিরিক্ত ভিডিও গেম)। প্রথমে প্রয়োজন পূরণ করো!",
                "question": "নিচের কোনটি একজন শিক্ষার্থীর আসল 'প্রয়োজন'?",
                "options": ["পুষ্টিকর খাবার ও পড়ার বই", "দামি ভিডিও গেম"],
                "correct": 0,
                "reward": "বিচক্ষণ শিক্ষার্থী পদক",
                "praise": "অসাধারণ! সঠিক সিদ্ধান্ত নিতে তুমি দক্ষ!"
            }
        ]
    },
    "Classes 3-5": {
        "English": [
            {
                "subject": "Financial Intelligence",
                "topic": "The Power of Budgeting",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "A Budget is a roadmap for your money: Income - Expenses = Savings. Tracking where every rupee goes ensures you have emergency savings and avoid debt!",
                "question": "If you earn ₹100 and spend ₹60 on stationery, how much is your savings?",
                "options": ["₹40", "₹160"],
                "correct": 0,
                "reward": "Junior Budget Master Trophy",
                "praise": "Outstanding math! You managed your budget perfectly!"
            }
        ],
        "हिन्दी (Hindi)": [
            {
                "subject": "वित्तीय प्रबंधन",
                "topic": "बजट का जादू",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "बजट बनाने का सरल नियम है: कमाई - खर्च = बचत। अपने हर पैसे का हिसाब रखने से भविष्य में कभी पैसों की कमी नहीं होती!",
                "question": "यदि आपको ₹100 मिले और आपने ₹60 खर्च किए, तो आपकी बचत कितनी हुई?",
                "options": ["₹40", "₹160"],
                "correct": 0,
                "reward": "बजट विशेषज्ञ ट्रॉफी",
                "praise": "उत्कृष्ट गणना! आपने अपना बजट सही संभाला!"
            }
        ],
        "বাংলা (Bengali)": [
            {
                "subject": "আর্থিক বুদ্ধিমত্তা",
                "topic": "বাজেটের নিয়ম",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "বাজেট হলো আয়ের সঠিক পরিকল্পনা: আয় - খরচ = সঞ্চয়। প্রতিটি খরচের হিসাব রাখলে ভবিষ্যৎ সুরক্ষিত থাকে!",
                "question": "যদি তোমার আয় হয় ₹১০০ এবং খরচ হয় ₹৬০, তবে তোমার সঞ্চয় কত?",
                "options": ["₹৪০", "₹১৬০"],
                "correct": 0,
                "reward": "বাজেট মাস্টার ট্রফি",
                "praise": "চমৎকার হিসাব! সঠিক আর্থিক পরিকল্পনা শিখে গেছো!"
            }
        ]
    },
    "Classes 6-8": {
        "English": [
            {
                "subject": "Modern Banking & Security",
                "topic": "Simple Interest & Safe Digital Banking",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "Banks pay Interest on your savings! Simple Interest formula: SI = (P * R * T) / 100. Cyber Safety Rule: Never share your ATM PIN, OTP, or UPI password with anyone!",
                "question": "What is the most important security rule when using digital bank accounts?",
                "options": ["Never share OTP or PIN with anyone", "Post PIN on social media"],
                "correct": 0,
                "reward": "Cyber Banking Sentinel Medal",
                "praise": "Perfect! Protecting your credentials keeps money safe!"
            }
        ],
        "हिन्दी (Hindi)": [
            {
                "subject": "बैंकिंग एवं डिजिटल सुरक्षा",
                "topic": "साधारण ब्याज व सुरक्षित बैंकिंग",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "बैंक में पैसा रखने पर ब्याज मिलता है: SI = (P * R * T) / 100। डिजिटल सुरक्षा नियम: अपना बैंक OTP या UPI पिन कभी किसी के साथ साझा न करें!",
                "question": "डिजिटल बैंकिंग इस्तेमाल करते समय सबसे जरूरी सुरक्षा नियम क्या है?",
                "options": ["अपना OTP और पिन किसी को न बताएं", "पिन सबको बता दें"],
                "correct": 0,
                "reward": "सुरक्षित बैंकिंग रक्षक मेडल",
                "praise": "एकदम सही! सुरक्षा नियमों का पालन ही समझदारी है!"
            }
        ],
        "বাংলা (Bengali)": [
            {
                "subject": "ব্যাংকিং ও সাইবার নিরাপত্তা",
                "topic": "সরল সুদ ও নিরাপদ লেনদেন",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "ব্যাংকে টাকা রাখলে সুদ পাওয়া যায়: SI = (P * R * T) / 100। নিরাপত্তা নীতি: কখনোই নিজের OTP বা পাসওয়ার্ড কাউকে শেয়ার করবে না!",
                "question": "ডিজিটাল ব্যাংকিংয়ের সবচেয়ে জরুরি নিরাপত্তা নিয়ম কোনটি?",
                "options": ["কখনোই কারো সাথে OTP বা PIN শেয়ার না করা", "সবাইকে পিন জানানো"],
                "correct": 0,
                "reward": "সাইবার ব্যাংকিং মেডেল",
                "praise": "একদম ঠিক! নিজের গোপন পিন সুরক্ষিত রাখাই বুদ্ধিমানের কাজ!"
            }
        ]
    },
    "Classes 9-10": {
        "English": [
            {
                "subject": "Advanced Personal Finance",
                "topic": "The 50/30/20 Rule & Compound Interest",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "The 50/30/20 Rule divides net income: 50% for Needs, 30% for Wants, and 20% for Investments/Savings. Compound interest A = P(1 + r/n)^(nt) turns early discipline into wealth!",
                "question": "According to the 50/30/20 budgeting rule, what percentage goes to Investments/Savings?",
                "options": ["20%", "70%"],
                "correct": 0,
                "reward": "Financial Freedom Laureate",
                "praise": "Brilliant! The 50/30/20 framework is the gold standard of money management!"
            }
        ],
        "हिन्दी (Hindi)": [
            {
                "subject": "उन्नत व्यक्तिगत वित्त",
                "topic": "50/30/20 नियम एवं चक्रवृद्धि ब्याज",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "50/30/20 नियम के अनुसार: 50% ज़रूरतें, 30% इच्छाएं, और 20% अनिवार्य बचत/निवेश। चक्रवृद्धि ब्याज (Compound Interest) समय के साथ पूंजी को कई गुना बढ़ाता है!",
                "question": "50/30/20 बजट नियम के तहत कितने प्रतिशत की बचत या निवेश करना चाहिए?",
                "options": ["20%", "70%"],
                "correct": 0,
                "reward": "वित्तीय स्वतंत्रता पुरस्कार",
                "praise": "अद्भुत! यह नियम आपको जीवनभर आर्थिक रूप से सशक्त रखेगा!"
            }
        ],
        "বাংলা (Bengali)": [
            {
                "subject": "উন্নত আর্থিক শিক্ষা",
                "topic": "৫০/৩০/২০ নিয়ম ও চক্রবৃদ্ধি সুদ",
                "video": "assets/intro_money.mp4",
                "image": "assets/money.png",
                "content": "৫০/৩০/২০ নিয়ম অনুযায়ী: ৫০% প্রয়োজন, ৩০% শখ, এবং ২০% দীর্ঘমেয়াদী বিনিয়োগ। চক্রবৃদ্ধি সুদ সময় বাড়ার সাথে সাথে সম্পদ কয়েক গুণ বৃদ্ধি করে!",
                "question": "৫০/৩০/২০ নিয়মানুযায়ী আয়ের কত শতাংশ সঞ্চয় বা বিনিয়োগ করা উচিত?",
                "options": ["২০%", "৭০%"],
                "correct": 0,
                "reward": "ফাইন্যান্সিয়াল জিনিয়াস ট্রফি",
                "praise": "চমৎকার জ্ঞান! এই নিয়ম তোমাকে ভবিষ্যৎ জীবনে অর্থনৈতিকভাবে সফল করবে!"
            }
        ]
    }
}

BLOCKED_KEYWORDS = {
    "porn", "xxx", "sex", "nude", "naked", "erotic", "nsfw", "adult",
    "hentai", "penis", "vagina", "boobs", "breast", "intercourse", "fetish",
    "orgasm", "strip", "masturbat", "escort", "gambling", "casino"
}

class EduSphereGame(FloatLayout):
    def __init__(self, **kwargs):
        super(EduSphereGame, self).__init__(**kwargs)

        self.selected_lang = "English"
        self.selected_grade = "Classes 3-5"
        self.current_modules = []
        self.module_index = 0

        with self.canvas.before:
            Color(0.04, 0.08, 0.16, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.bg_music = None
        self.celebrate_sound = None
        self.init_3d_spatial_audio()

        # 1. Screen 1: Animated Language Selection
        self.lang_screen = BoxLayout(
            orientation='vertical',
            size_hint=(0.92, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=10
        )
        lang_title = Label(
            text="[b]EduSphere 3D[/b]\nSelect Language / भाषा चुनें:",
            markup=True,
            font_size='20sp',
            halign='center',
            color=(1, 0.85, 0.2, 1),
            size_hint_y=0.18
        )
        self.lang_screen.add_widget(lang_title)

        lang_scroll = ScrollView(size_hint=(1, 0.82))
        lang_grid = GridLayout(cols=2, spacing=8, size_hint_y=None)
        lang_grid.bind(minimum_height=lang_grid.setter('height'))

        for lang_name in LANG_CONFIG.keys():
            l_btn = Button(
                text=lang_name,
                font_size='15sp',
                bold=True,
                size_hint_y=None,
                height=52,
                background_normal='',
                background_color=(0.14, 0.48, 0.78, 1)
            )
            l_btn.bind(on_release=lambda instance, l=lang_name: self.choose_language_animated(instance, l))
            lang_grid.add_widget(l_btn)

        lang_scroll.add_widget(lang_grid)
        self.lang_screen.add_widget(lang_scroll)
        self.add_widget(self.lang_screen)

        # 2. Screen 2: Animated Class Selection Screen
        self.class_screen = BoxLayout(
            orientation='vertical',
            size_hint=(0.92, 0.85),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=10,
            opacity=0,
            disabled=True
        )
        self.class_title = Label(
            text="",
            markup=True,
            font_size='21sp',
            halign='center',
            color=(1, 0.85, 0.2, 1),
            size_hint_y=0.2
        )
        self.class_screen.add_widget(self.class_title)

        self.class_grid = GridLayout(cols=1, spacing=8, size_hint=(1, 0.8))
        self.class_screen.add_widget(self.class_grid)
        self.add_widget(self.class_screen)

        # 3. Screen 3: Main Learning Canvas
        self.game_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.94, 0.96),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            spacing=6,
            opacity=0
        )

        self.header_label = Label(
            text="",
            markup=True,
            font_size='16sp',
            bold=True,
            size_hint_y=0.07,
            color=(1, 0.88, 0.25, 1)
        )
        self.game_container.add_widget(self.header_label)

        self.media_box = FloatLayout(size_hint_y=0.30)
        self.video_player = Video(
            source="",
            state='stop',
            options={'eos': 'loop'},
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            opacity=0
        )
        self.topic_image = Image(
            source="",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.media_box.add_widget(self.topic_image)
        self.media_box.add_widget(self.video_player)
        self.game_container.add_widget(self.media_box)

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
        self.btn_a.bind(on_release=lambda x: self.check_answer_animated(self.btn_a, 0))
        self.btn_b.bind(on_release=lambda x: self.check_answer_animated(self.btn_b, 1))
        self.options_layout.add_widget(self.btn_a)
        self.options_layout.add_widget(self.btn_b)
        self.game_container.add_widget(self.options_layout)

        search_box = BoxLayout(orientation='horizontal', spacing=4, size_hint_y=0.09)
        self.query_input = TextInput(
            hint_text="",
            multiline=False,
            font_size='13sp',
            size_hint=(0.72, 1)
        )
        self.search_btn = Button(
            text="",
            font_size='13sp',
            bold=True,
            size_hint=(0.28, 1),
            background_normal='',
            background_color=(0.92, 0.45, 0.15, 1)
        )
        self.search_btn.bind(on_release=self.fetch_web_knowledge)
        search_box.add_widget(self.query_input)
        search_box.add_widget(self.search_btn)
        self.game_container.add_widget(search_box)

        self.add_widget(self.game_container)

        # 4. Celebration Modal Banner
        self.celeb_banner = BoxLayout(
            orientation='vertical',
            size_hint=(0.88, 0.42),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            padding=14,
            spacing=8,
            opacity=0
        )
        with self.celeb_banner.canvas.before:
            Color(0.08, 0.14, 0.24, 0.97)
            self.celeb_bg = Rectangle(size=self.celeb_banner.size, pos=self.celeb_banner.pos)
        self.celeb_banner.bind(size=self._update_celeb_bg, pos=self._update_celeb_bg)

        self.celeb_title = Label(text="", font_size='21sp', bold=True, color=(1, 0.85, 0.1, 1))
        self.celeb_msg = Label(text="", font_size='14sp', halign='center', color=(1, 1, 1, 1))
        self.celeb_msg.bind(width=lambda *x: self.celeb_msg.setter('text_size')(self.celeb_msg, (self.celeb_msg.width - 20, None)))
        self.celeb_reward = Label(text="", font_size='15sp', bold=True, color=(0.3, 0.95, 0.6, 1))

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

    def init_3d_spatial_audio(self):
        try:
            music_path = 'assets/soothing_lullaby.wav'
            if os.path.exists(music_path):
                self.bg_music = SoundLoader.load(music_path)
                if self.bg_music:
                    self.bg_music.loop = True
                    self.bg_music.volume = 0.20
                    self.bg_music.play()

            sound_path = 'assets/celebrate.wav'
            if os.path.exists(sound_path):
                self.celebrate_sound = SoundLoader.load(sound_path)
                if self.celebrate_sound:
                    self.celebrate_sound.volume = 0.85
        except Exception:
            pass

    def choose_language_animated(self, button_instance, lang_name):
        # Bounce feedback animation
        anim = Animation(background_color=(0.3, 0.8, 1.0, 1), duration=0.1) + Animation(background_color=(0.14, 0.48, 0.78, 1), duration=0.15)
        anim.bind(on_complete=lambda *args: self._execute_lang_transition(lang_name))
        anim.start(button_instance)

    def _execute_lang_transition(self, lang_name):
        self.selected_lang = lang_name
        cfg = LANG_CONFIG.get(lang_name, LANG_CONFIG["English"])

        Animation(opacity=0, duration=0.25).start(self.lang_screen)
        Clock.schedule_once(lambda dt: self._setup_class_screen(cfg), 0.25)

    def _setup_class_screen(self, cfg):
        self.lang_screen.disabled = True
        self.class_title.text = f"[b]EduSphere 3D[/b]\n{cfg['select_class']}"
        self.query_input.hint_text = cfg["search_hint"]
        self.search_btn.text = cfg["search_btn"]
        self.celeb_title.text = cfg["great_work"]

        self.class_grid.clear_widgets()
        for label_text, g_key in cfg["grades"]:
            btn = Button(
                text=label_text,
                font_size='14sp',
                bold=True,
                background_normal='',
                background_color=(0.12, 0.45, 0.75, 1)
            )
            btn.bind(on_release=lambda instance, k=g_key: self.start_grade_animated(instance, k))
            self.class_grid.add_widget(btn)

        self.class_screen.disabled = False
        Animation(opacity=1, duration=0.3).start(self.class_screen)

    def start_grade_animated(self, button_instance, grade_key):
        anim = Animation(background_color=(0.3, 0.9, 0.5, 1), duration=0.1) + Animation(background_color=(0.12, 0.45, 0.75, 1), duration=0.15)
        anim.bind(on_complete=lambda *args: self._execute_grade_transition(grade_key))
        anim.start(button_instance)

    def _execute_grade_transition(self, grade_key):
        self.selected_grade = grade_key
        grade_dict = MULTILINGUAL_CURRICULUM.get(grade_key, MULTILINGUAL_CURRICULUM["Classes 3-5"])
        self.current_modules = grade_dict.get(self.selected_lang, grade_dict.get("English", []))
        self.module_index = 0

        Animation(opacity=0, duration=0.25).start(self.class_screen)
        Clock.schedule_once(lambda dt: self._reveal_gameplay(), 0.25)

    def _reveal_gameplay(self):
        self.class_screen.disabled = True
        self.load_topic()
        Animation(opacity=1, duration=0.35).start(self.game_container)

    def load_topic(self):
        try:
            mod = self.current_modules[self.module_index]
            self.header_label.text = f"[b]{mod['subject']}[/b]: {mod['topic']}"

            vid_path = mod.get("video", "")
            img_path = mod.get("image", "")

            if vid_path and os.path.exists(vid_path):
                self.topic_image.opacity = 0
                self.video_player.opacity = 1
                self.video_player.source = vid_path
                self.video_player.state = 'play'
            elif img_path and os.path.exists(img_path):
                self.video_player.state = 'stop'
                self.video_player.opacity = 0
                self.topic_image.opacity = 1
                self.topic_image.source = img_path
            else:
                self.video_player.state = 'stop'
                self.video_player.opacity = 0
                self.topic_image.opacity = 1
                self.topic_image.source = "assets/icon.png"

            self.content_label.text = f"{mod['content']}\n\n[b]{mod['question']}[/b]"
            self.btn_a.text = mod["options"][0]
            self.btn_b.text = mod["options"][1]
            self.btn_a.disabled = False
            self.btn_b.disabled = False
            self.btn_a.background_color = (0.18, 0.65, 0.35, 1)
            self.btn_b.background_color = (0.18, 0.65, 0.35, 1)
        except Exception:
            pass

    def check_answer_animated(self, button_instance, chosen_idx):
        mod = self.current_modules[self.module_index]
        cfg = LANG_CONFIG.get(self.selected_lang, LANG_CONFIG["English"])
        
        if chosen_idx == mod["correct"]:
            self.btn_a.disabled = True
            self.btn_b.disabled = True
            button_instance.background_color = (0.1, 0.85, 0.4, 1)

            if self.celebrate_sound:
                try:
                    self.celebrate_sound.play()
                except Exception:
                    pass

            self.celeb_msg.text = mod["praise"]
            self.celeb_reward.text = f"{cfg['unlocked']}: {mod['reward']}"

            Animation(opacity=1, duration=0.35).start(self.celeb_banner)
            Clock.schedule_once(self.next_topic_animated, 3.4)
        else:
            button_instance.background_color = (0.85, 0.2, 0.2, 1)
            self.content_label.text = f"{mod['content']}\n\n[color=ff7777]{cfg['try_again']}[/color]\n[b]{mod['question']}[/b]"

    def next_topic_animated(self, dt):
        Animation(opacity=0, duration=0.25).start(self.celeb_banner)
        self.module_index = (self.module_index + 1) % len(self.current_modules)
        self.load_topic()

    def is_safe_query(self, text):
        clean = text.lower().strip()
        return not any(bad_word in clean for bad_word in BLOCKED_KEYWORDS)

    def fetch_web_knowledge(self, instance):
        query = self.query_input.text.strip()
        if not query:
            return

        cfg = LANG_CONFIG.get(self.selected_lang, LANG_CONFIG["English"])
        if not self.is_safe_query(query):
            self.header_label.text = cfg["safety_title"]
            self.content_label.text = cfg["safety_msg"]
            self.query_input.text = ""
            return

        self.header_label.text = f"{query.title()}"
        self.content_label.text = "..."
        threading.Thread(target=self._async_fetch, args=(query,), daemon=True).start()

    def _async_fetch(self, query):
        cfg = LANG_CONFIG.get(self.selected_lang, LANG_CONFIG["English"])
        lang_code = cfg.get("code", "en")
        safe_q = urllib.parse.quote(query)
        url = f"https://{lang_code}.wikipedia.org/api/rest_v1/page/summary/{safe_q}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'EduSphereKids3D/1.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode())
                extract = data.get('extract', '')
                if extract:
                    summary = extract[:220] + "..." if len(extract) > 220 else extract
                    self.update_web_fact(query, summary)
                else:
                    self.update_web_fact(query, f"{query.title()}")
        except Exception:
            self.update_web_fact(query, f"{query.title()}")

    @mainthread
    def update_web_fact(self, topic, summary):
        self.header_label.text = f"{topic.title()}"
        self.content_label.text = summary
        self.query_input.text = ""
        if self.celebrate_sound:
            try:
                self.celebrate_sound.play()
            except Exception:
                pass

class EduSphereApp(App):
    def build(self):
        return EduSphereGame()

if __name__ == '__main__':
    EduSphereApp().run()

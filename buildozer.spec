[app]
title = WildPals AI
package.name = wildpalsai
package.domain = org.edugame
source.dir = .
source.include_exts = py,png,jpg,json,mp3,wav,ogg,mp4
version = 1.0.0
requirements = python3,kivy
orientation = all
icon.filename = %(source.dir)s/assets/icon.png

# Android target specs
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0

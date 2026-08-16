[app]
title = NovaQuest 3D
package.name = novaquest3d
package.domain = org.edugame
source.dir = .
source.include_exts = py,png,jpg,kv,json,wav
version = 1.0.0
requirements = python3,kivy
orientation = portrait

# Android Platform Configuration
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 0

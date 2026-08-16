[app]
title = Safari Explorer AI
package.name = safariexplorer
package.domain = org.edugame
source.dir = .
source.include_exts = py,png,jpg,json,mp3
version = 1.0.0
requirements = python3,kivy

# Android target specs (Updated for modern Android)
android.api = 34
android.minapi = 24
android.accept_sdk_license = True
android.archs = arm64-v8a
android.release_artifact = aab

[buildozer]
log_level = 2
warn_on_root = 0

[app]

# (str) Title of your application
title = XiaoMusic

# (str) Package name
package.name = xiaomusic

# (str) Package domain (needed for android/ios packaging)
package.domain = org.hanxi

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt,html,css,js,ico,mp3,woff2

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,sh,bat

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .git, .github, docs, __pycache__

# (str) Application versioning (method 1)
version = 0.4.5

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,aiohttp,watchdog,mutagen,yt-dlp,uvicorn,fastapi,starlette,aiofiles,ga4mp,apscheduler,opencc-python-reimplemented,pillow,python-multipart,requests,sentry-sdk,pyjwt,fake-useragent,miservice-fork,edge-tts,psutil,pycryptodome,certifi,ssl

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 19b

# (int) Android NDK API to use. This is the minimum API your app will support
# it should usually match android.minapi.
#android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (list) Android apptheme
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >= 23)
android.allow_backup = True

# (str) XML file for custom build.gradle
#android.build_gradle =

# (str) XML file for custom AndroidManifest.xml
#android.manifest =

# (list) Android additionnal libraries to copy into libs/abi
#android.add_libs_armeabi = libs/android-v7/libfolia.so
#android.add_libs_armeabi_v7a = libs/android-v7/libfolia.so
#android.add_libs_arm64_v8a = libs/android-v8/libfolia.so
#android.add_libs_x86 = libs/android-x86/libfolia.so
#android.add_libs_mips = libs/android-mips/libfolia.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
android.wakelock = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:name].
#    Examples:
#
#    [app:source.include_exts]
#    py
#    png
#    jpg
#
#    [app:source.exclude_patterns]
#    images/*
#    *.db
#

@echo off
python3 "%~dp0\..\visualizeWithMotion.py" src_dirs=20,!20/7 fullscreen=1 random_mode=1 auto_progress=1 trim_images=1 n_images=10 n_images=%1 transition_interval=30  transition_interval=%2 wallpaper_mode=1 set_wallpaper=3 wallpaper_dir=V:/


@echo off
python3 "%~dp0\..\visualizeWithMotion.py" src_dirs=17/2 fullscreen=1 random_mode=1 auto_progress=1 trim_images=0 n_images=%1 transition_interval=20  transition_interval=%2


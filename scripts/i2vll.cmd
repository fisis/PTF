@echo off
python "%~dp0\..\imgSeqToVideo.py" src_path=%1 n_frames=%2 width=%3 height=%4 fps=%5 codec=FFV1 ext=avi save_path=%6
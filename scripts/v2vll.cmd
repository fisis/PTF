@echo off
python3 "%~dp0\..\encodeVideo.py" src_path=%1 fps=%2 n_frames=%3 res=%4 start_id=%5 save_path=%6 codec=FFV1 ext=avi out_postfix=ll
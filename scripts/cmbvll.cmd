@echo off
python2 "%~dp0\..\encodeVideo.py" combine=1 src_path=%1 fps=%2 n_frames=%3 res=%4 start_id=%5 reverse=%6 codec=%7 save_path=%8 codec=FFV1 ext=avi add_headers=1
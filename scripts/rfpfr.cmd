@echo off
python2 "%~dp0\..\rename.py" include_folders=2 src_substr=__pf__ dst_substr=__rf__ recursive_search=1 exclude_src=1 convert_to_lowercase=%4 replace_existing=%5 show_names=%6 src_dir=%7 write_log=1 re_mode=0
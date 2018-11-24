import numpy as np
import keyboard
import sys
import os, time

from Misc import processArguments, sortKey, resizeAR

params = {
    'src_path': '.',
    'save_path': '',
    'img_ext': 'jpg',
    'show_img': 1,
    'del_src': 0,
    'start_id': 0,
    'n_frames': 0,
    'transition_interval': 5,
    'random_mode': 1,
    'recursive': 1,
    'width': 0,
    'height': 0,
    'fps': 30,
    'codec': 'H264',
    'ext': 'mkv',
}

processArguments(sys.argv[1:], params)
src_path = params['src_path']
save_path = params['save_path']
img_ext = params['img_ext']
show_img = params['show_img']
del_src = params['del_src']
start_id = params['start_id']
n_frames = params['n_frames']
width = params['width']
height = params['height']
fps = params['fps']
codec = params['codec']
ext = params['ext']
recursive = params['recursive']
random_mode = params['random_mode']
transition_interval = params['transition_interval']

try:
    import ctypes

    win_wallpaper_func = ctypes.windll.user32.SystemParametersInfoA
    orig_wp_fname = ctypes.create_string_buffer(500)
    SPI_GETDESKWALLPAPER = 0x0073
    SPI_SETDESKWALLPAPER = 20

    orig_wp_fname_res = win_wallpaper_func(SPI_GETDESKWALLPAPER, 500, orig_wp_fname, 0)

    orig_wp_fname = orig_wp_fname.value.decode("utf-8")
    print("orig_wp_fname: {}".format(orig_wp_fname))

    win_wallpaper_func = ctypes.windll.user32.SystemParametersInfoW

except BaseException as e:
    raise SystemError('Wallpaper functionality unavailable: {}'.format(e))

img_id = 0
if os.path.isdir(src_path):
    src_dir = src_path
    img_fname = None
elif os.path.isfile(src_path):
    src_dir = os.path.dirname(src_path)
    img_fname = src_path
else:
    raise IOError('Invalid source path: {}'.format(src_path))

print('Reading source images from: {}'.format(src_dir))

img_exts = ('.jpg', '.bmp', '.jpeg', '.png', '.tif', '.tiff', '.gif')

if recursive:
    src_file_gen = [[os.path.join(dirpath, f) for f in filenames if
                     os.path.splitext(f.lower())[1] in img_exts]
                    for (dirpath, dirnames, filenames) in os.walk(src_dir, followlinks=True)]
    src_file_list = [item for sublist in src_file_gen for item in sublist]
else:
    src_file_list = [os.path.join(src_dir, k) for k in os.listdir(src_dir) if
                     os.path.splitext(k.lower())[1] in img_exts]

total_frames = len(src_file_list)
if total_frames <= 0:
    raise SystemError('No input frames found')
print('total_frames: {}'.format(total_frames))

try:
    # nums = int(os.path.splitext(img_fname)[0].split('_')[-1])
    src_file_list.sort(key=sortKey)
except:
    src_file_list.sort()

if img_fname is None:
    img_fname = src_file_list[img_id]

img_id = src_file_list.index(img_fname)

exit_program = 0


def loadImage(diff=0):
    global img_id, src_file_list_rand
    img_id += diff
    if img_id >= total_frames:
        img_id -= total_frames
        if random_mode:
            print('Resetting randomisation')
            src_file_list_rand = list(np.random.permutation(src_file_list))
    if img_id < 0:
        img_id = total_frames - 1

    if random_mode:
        src_img_fname = src_file_list_rand[img_id]
    else:
        src_img_fname = src_file_list[img_id]

    src_img_fname = os.path.abspath(src_img_fname)

    # print('src_img_fname: {}'.format(src_img_fname))
    win_wallpaper_func(SPI_SETDESKWALLPAPER, 0, src_img_fname, 0)


def inc_callback():
    global transition_interval
    transition_interval += 1
    print('Setting transition interval to: {}'.format(transition_interval))


def dec_callback():
    global transition_interval
    transition_interval -= 1
    if transition_interval < 1:
        transition_interval = 1
    print('Setting transition interval to: {}'.format(transition_interval))


def exit_callback():
    global exit_program
    print('Exiting')
    exit_program = 1


def next_callback():
    loadImage(1)


def prev_callback():
    loadImage(-1)


def kb_callback(key_struct):
    global exit_program
    k = key_struct.name
    # print('key_struct: {}'.format(key_struct))
    print('scan_code: {}'.format(key_struct.scan_code))
    print('name: {}'.format(k))
    if k == 'esc':
        print('Exiting')
        exit_program = 1


keyboard.add_hotkey('ctrl+alt+esc', exit_callback)
keyboard.add_hotkey('ctrl+alt+right', next_callback)
keyboard.add_hotkey('ctrl+alt+left', prev_callback)
keyboard.add_hotkey('ctrl+alt+up', inc_callback)
keyboard.add_hotkey('ctrl+alt+down', dec_callback)

if random_mode:
    print('Random mode enabled')
    src_file_list_rand = list(np.random.permutation(src_file_list))

start_t = time.time()
img_id -= 1
while not exit_program:
    loadImage(1)
    while time.time() - start_t < transition_interval:
        continue
    start_t = time.time()

win_wallpaper_func(SPI_SETDESKWALLPAPER, 0, orig_wp_fname, 0)

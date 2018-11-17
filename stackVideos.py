import cv2
import sys
import os, shutil

from Misc import processArguments, sortKey, resizeAR, stackImages

params = {
    'src_paths': [],
    'root_dir': '',
    'save_path': '',
    'img_ext': 'jpg',
    'show_img': 1,
    'del_src': 0,
    'start_id': 0,
    'n_frames': 0,
    'preserve_order': 1,
    'borderless': 0,
    'width': 0,
    'height': 0,
    'fps': 30,
    'codec': 'H264',
    'ext': 'mkv',
    'grid_size': '',
}

processArguments(sys.argv[1:], params)
_src_path = params['src_paths']
root_dir = params['root_dir']
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
grid_size = params['grid_res']
borderless = params['borderless']
preserve_order = params['preserve_order']

vid_exts = ['.mkv', '.mp4', '.avi', '.mjpg', '.wmv']

if len(_src_path) == 1:
    _src_path = _src_path[0]
    print('Reading source videos from: {}'.format(_src_path))
    if os.path.isdir(_src_path):
        src_file_list = [os.path.join(_src_path, k) for k in os.listdir(_src_path) for _ext in vid_exts if
                         k.endswith(_ext)]
        n_videos = len(src_file_list)
        if n_videos <= 0:
            raise SystemError('No input videos found')
        print('n_videos: {}'.format(n_videos))
        src_file_list.sort(key=sortKey)
    else:
        src_file_list = [x.strip() for x in open(_src_path).readlines() if x.strip()]
        if root_dir:
            src_file_list = [os.path.join(root_dir, name) for name in src_file_list]
else:
    src_file_list = _src_path

if not save_path:
    dst_path = os.path.join(os.path.dirname(src_file_list[0]), 'stacked.' + ext)
else:
    dst_path = save_path

save_dir = os.path.dirname(dst_path)
if save_dir and not os.path.isdir(save_dir):
    os.makedirs(save_dir)

if not grid_size:
    grid_size = None
else:
    grid_size = [int(x) for x in grid_size.split('x')]
    if len(grid_size) != 2:
        raise IOError('Invalid grid_size: {}'.format(grid_size))

n_videos = len(src_file_list)

n_frames_list = []
cap_list = []
size_list = []

for src_file in src_file_list:
    src_file = os.path.abspath(src_file)
    seq_name = os.path.splitext(os.path.basename(src_file))[0]

    cap = cv2.VideoCapture()
    if not cap.open(src_file):
        raise StandardError('The video file ' + src_file + ' could not be opened')

    if cv2.__version__.startswith('3'):
        cv_prop = cv2.CAP_PROP_FRAME_COUNT
        h_prop = cv2.CAP_PROP_FRAME_HEIGHT
        w_prop = cv2.CAP_PROP_FRAME_WIDTH
    else:
        cv_prop = cv2.cv.CAP_PROP_FRAME_COUNT
        h_prop = cv2.cv.CAP_PROP_FRAME_HEIGHT
        w_prop = cv2.cv.CAP_PROP_FRAME_WIDTH

    total_frames = int(cap.get(cv_prop))
    _height = int(cap.get(h_prop))
    _width = int(cap.get(w_prop))

    cap_list.append(cap)
    n_frames_list.append(total_frames)
    size_list.append((_width, _height))

frame_id = start_id
pause_after_frame = 0
video_out = None

while True:

    images = []
    for cap in cap_list:
        ret, image = cap.read()
        if not ret:
            print('\nFrame {:d} could not be read'.format(frame_id + 1))
            break
        images.append(image)

    if len(images) != n_videos:
        break

    out_img = stackImages(images, grid_size, borderless=borderless, preserve_order=preserve_order)

    if video_out is None:
        dst_height, dst_width = out_img.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*codec)
        video_out = cv2.VideoWriter(dst_path, fourcc, fps, (dst_width, dst_height))

        if video_out is None:
            raise IOError('Output video file could not be opened: {}'.format(dst_path))

        print('Saving {}x{} output video to {}'.format(dst_width, dst_height, dst_path))

    video_out.write(out_img)
    if show_img:
        cv2.imshow('stacked', out_img)
        k = cv2.waitKey(1 - pause_after_frame) & 0xFF
        if k == ord('q') or k == 27:
            break
        elif k == 32:
            pause_after_frame = 1 - pause_after_frame

    frame_id += 1
    sys.stdout.write('\rDone {:d} frames '.format(frame_id - start_id))
    sys.stdout.flush()

sys.stdout.write('\n')
sys.stdout.flush()

video_out.release()

if show_img:
    cv2.destroyWindow('stacked')

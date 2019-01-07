import cv2
import sys
import os, shutil

from Misc import processArguments, sortKey, resizeAR

params = {
    'src_path': '.',
    'save_path': '',
    'img_ext': 'jpg',
    'show_img': 1,
    'del_src': 0,
    'start_id': 0,
    'n_frames': 0,
    'reverse': 0,
    'res': '',
    'fps': 30,
    'codec': 'H264',
    'ext': 'mkv',
    'out_postfix': '',
}

processArguments(sys.argv[1:], params)
_src_path = params['src_path']
save_path = params['save_path']
img_ext = params['img_ext']
show_img = params['show_img']
del_src = params['del_src']
start_id = params['start_id']
n_frames = params['n_frames']
res = params['res']
fps = params['fps']
codec = params['codec']
ext = params['ext']
reverse = params['reverse']
out_postfix = params['out_postfix']


height = width = 0
if res:
    width, height = [int(x) for x in res.split('x')]

print('Reading source videos from: {}'.format(_src_path))
vid_exts = ['.mkv', '.mp4', '.avi', '.mjpg', '.wmv']

if os.path.isdir(_src_path):
    src_file_list = [os.path.join(_src_path, k) for k in os.listdir(_src_path) for _ext in vid_exts if k.endswith(_ext)]
    n_videos = len(src_file_list)
    if n_videos <= 0:
        raise SystemError('No input videos found')
    print('n_videos: {}'.format(n_videos))
    src_file_list.sort(key=sortKey)
else:
    src_file_list = [_src_path]

if reverse:
    print('Reversing video')

for src_path in src_file_list:
    src_path = os.path.abspath(src_path)
    seq_name = os.path.splitext(os.path.basename(src_path))[0]

    if not save_path:
        dst_seq_name = seq_name
        if start_id > 0:
            dst_seq_name = '{}_{}'.format(dst_seq_name, start_id)
        if n_frames > 0:
            dst_seq_name = '{}_{}'.format(dst_seq_name, start_id + n_frames)
        dst_path = os.path.join(os.path.dirname(src_path), dst_seq_name + '.' + ext)
    else:
        dst_path = save_path

    if dst_path == src_path:
        print('Skipping {:s} as having the save name as its target'.format(src_path))

    save_dir = os.path.dirname(dst_path)
    if save_dir and not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    cap = cv2.VideoCapture()
    if not cap.open(src_path):
        raise IOError('The video file ' + src_path + ' could not be opened')

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

    if n_frames <= 0:
        dst_n_frames = total_frames
    else:
        if total_frames > 0 and n_frames > total_frames:
            raise AssertionError('Invalid n_frames {} for video with {} frames'.format(n_frames, total_frames))
        dst_n_frames = n_frames

    if height <= 0 or width <= 0:
        dst_height, dst_width = _height, _width
        enable_resize = 0
    else:
        enable_resize = 1
        dst_height, dst_width = height, width

    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_out = cv2.VideoWriter(dst_path, fourcc, fps, (dst_width, dst_height))

    if video_out is None:
        raise IOError('Output video file could not be opened: {}'.format(dst_path))

    print('Saving {}x{} output video to {}'.format(dst_width, dst_height, dst_path))

    if start_id > 0:
        print('Starting from frame_id {}'.format(start_id))

    frame_id = 0
    pause_after_frame = 0
    frames = []
    while True:

        ret, image = cap.read()
        if not ret:
            print('\nFrame {:d} could not be read'.format(frame_id + 1))
            break

        frame_id += 1

        if frame_id <= start_id:
            continue

        if enable_resize:
            image = resizeAR(image, dst_width, dst_height)

        if show_img:
            cv2.imshow(seq_name, image)
            k = cv2.waitKey(1 - pause_after_frame) & 0xFF
            if k == ord('q') or k == 27:
                break
            elif k == 32:
                pause_after_frame = 1 - pause_after_frame

        if reverse:
            frames.append(image)
        else:
            video_out.write(image)

        sys.stdout.write('\rDone {:d} frames '.format(frame_id - start_id))
        sys.stdout.flush()

        if dst_n_frames > 0 and (frame_id - start_id) >= dst_n_frames:
            break

        if frame_id >= total_frames:
            break

    sys.stdout.write('\n')
    sys.stdout.flush()

    if reverse:
        for frame in frames[::-1]:
            video_out.write(frame)

    video_out.release()

    if show_img:
        cv2.destroyWindow(seq_name)
    if del_src:
        print('Removing source video {}'.format(src_path))
        shutil.rmtree(src_path)

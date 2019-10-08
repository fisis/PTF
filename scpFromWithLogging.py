from pywinauto import application
import os, sys
# from dragonfly import Window

import ctypes
import win32gui

from Misc import processArguments

if __name__ == '__main__':
    params = {
        'win_title': 'The Journal 8',
        'config': 0,
        'wait_t': 10,
        'scp_dst': 'abhineet@greyshark.cs.ualberta.ca',
    }
    processArguments(sys.argv[1:], params)
    win_title = params['win_title']
    config = params['config']
    wait_t = params['wait_t']
    scp_dst = params['scp_dst']

    # Window.get_all_windows()

    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    titles = []


    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append((hwnd, buff.value))
        return True


    # EnumWindows(EnumWindowsProc(foreach_window), 0)

    win32gui.EnumWindows(foreach_window, None)

    for i in range(len(titles)):
        print(titles[i])

    target_title = [k[1] for k in titles if k[1].startswith(win_title)]
    print('target_title: {}'.format(target_title))

    if not target_title:
        raise IOError('Window with win_title: {} not found'.format(win_title))

    target_title = target_title[0]
    print('target_title: {}'.format(target_title))

    app = application.Application().connect(title=target_title)
    Form1 = app.Window_(title=target_title)
    Form1.SetFocus()
    Form1.TypeKeys("^t~")
    Form1.TypeKeys("nazio~")

    while True:
        k = input('Enter filename')
        scp_cmd = 'scp {}:~/{} ~/{}'.format(scp_dst, k, k)
        print('Running {}'.format(scp_dst))
        os.system(scp_cmd)
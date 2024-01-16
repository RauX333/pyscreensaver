
from pathlib import Path
import array
import psutil
import datetime
import time
import mss.tools
import ctypes
from ctypes import wintypes as w, create_unicode_buffer
import win32process as wproc
from log import log


picDir = Path.cwd() / 'tempPic'
picDir.mkdir(parents=True, exist_ok=True)
windowsOcrPath = Path.cwd() / "ocr_bins/Windows.Media.Ocr.Cli.exe"
goodOcrPath = Path.cwd() / "ocr_bins/ocr.exe"
db_ext_path = Path.cwd() / "libsimple/x64/simple"
db_path = Path.cwd() / 'test.db'
wordninja_path = Path.cwd() / 'ocr_bins\wordninja_words.txt.gz'
ffmpeg_path = Path.cwd() / 'ffmpeg/ffmpeg.exe'

MAX_PATH = 260
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

def errcheck(result, func, args):
    if result is None or result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return result


def current_milli_time():
    return round(time.time() * 1000)


# def slugify(value, allow_unicode=False):
#     """
#     Taken from https://github.com/django/django/blob/master/django/utils/text.py
#     Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#     dashes to single dashes. Remove characters that aren't alphanumerics,
#     underscores, or hyphens. Convert to lowercase. Also strip leading and
#     trailing whitespace, dashes, and underscores.
#     """
#     value = str(value)
#     if allow_unicode:
#         value = unicodedata.normalize('NFKC', value)
#     else:
#         value = unicodedata.normalize('NFKD', value).encode(
#             'ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '-', value).strip('-_')


class Rect(w.RECT):
    def __repr__(self):
        return f'Rect(left={self.left},top={self.top},right={self.right},bottom={self.bottom})'

    def __eq__(self, other):
        return self.left == other.left and self.top == other.top and self.right == other.right and self.bottom == other.bottom


def screenshot(rect: Rect):
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {"top": rect.top, "left": rect.left,
                   "width": rect.right-rect.left, "height": rect.bottom-rect.top}
        log.logger.debug("screenshot window rect: %s", monitor)
        now = current_milli_time()

        filename = str(now) + ".png"
        output = picDir / filename
        

        start = datetime.datetime.now()
        # Grab the data
        sct_img = sct.grab(monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)

        log.logger.debug(output)
        log.logger.debug('png time: %s', datetime.datetime.now()-start)
        return filename


user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('Psapi.dll')
ver = ctypes.WinDLL('version', use_last_error=True)


def getActiveWindowHandle():
    # TODO:check scroll behavior and screenshot
    hWnd = user32.GetForegroundWindow()
    return hWnd


def getWindowRect(hWnd):
    rect = Rect()
    user32.GetWindowRect(hWnd, ctypes.byref(rect))
    # TODO:get rid of taskbar
    return rect


def getWindowTitle(hWnd):
    length = user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hWnd, buf, length + 1)
    if buf.value:
        return buf.value
    else:
        log.logger.warning("hWnd no window title")
        return None


def getWindowPID(hWnd):
    PID = w.DWORD()
    user32.GetWindowThreadProcessId(hWnd, ctypes.byref(PID))
    return PID


def getThreadFullpathByPID(PID):
    if PID.value == 0:
        log.logger.warning("PID.value = 0")
        return None
    p = psutil.Process(PID.value)
    fullpath = p.exe()
    print(fullpath)
    print(windowsPath(fullpath))
    return windowsPath(fullpath)


def getThreadNameByPID(PID):
    if PID.value == 0:
        log.logger.warning("PID.value = 0")
        return None
    p = psutil.Process(PID.value)
    name = p.name()
    return name


GetFileVersionInfoSizeW = ver.GetFileVersionInfoSizeW
GetFileVersionInfoSizeW.argtypes = w.LPCWSTR, w.LPDWORD
GetFileVersionInfoSizeW.restype = w.DWORD

GetFileVersionInfoW = ver.GetFileVersionInfoW
GetFileVersionInfoW.argtypes = w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID
GetFileVersionInfoW.restype = w.BOOL

VerQueryValueW = ver.VerQueryValueW
VerQueryValueW.argtypes = w.LPCVOID, w.LPCWSTR, ctypes.POINTER(
    w.LPVOID), w.PUINT
VerQueryValueW.restype = w.BOOL


def getAppNameFromPath(fullpath):
    if fullpath is None:
        return None
    path = fullpath
    size = GetFileVersionInfoSizeW(path, None)
    if not size:
        log.logger.warning('app name not found')
        return path.rsplit('\\', 1)[-1]
    res = ctypes.create_string_buffer(size)
    if not GetFileVersionInfoW(path, 0, size, res):
        log.logger.warning('GetFileVersionInfoW failed')
        return path.rsplit('\\', 1)[-1]
    buf = w.LPVOID()
    length = w.UINT()
    # Look for codepages
    if not VerQueryValueW(res, r'\VarFileInfo\Translation', ctypes.byref(buf), ctypes.byref(length)):
        log.logger.warning('VerQueryValueW failed to find translation')
        return path.rsplit('\\', 1)[-1]
    if length.value == 0:
        log.logger.warning('no code pages')
        return path.rsplit('\\', 1)[-1]
    codepages = array.array('H', ctypes.string_at(buf.value, length.value))
    codepage = tuple(codepages[:2])

    # Extract information
    if not VerQueryValueW(res, rf'\StringFileInfo\{codepage[0]:04x}{codepage[1]:04x}\FileDescription', ctypes.byref(buf), ctypes.byref(length)):
        # fallback to the exe name directly
        return path.rsplit('\\', 1)[-1]
        # raise RuntimeError('VerQueryValueW failed to find file description')
    return ctypes.wstring_at(buf.value, length.value)


WNDENUMPROC = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, ctypes.py_object)
EnumChildWindows = user32.EnumChildWindows
EnumChildWindows.argtypes = w.HWND, WNDENUMPROC, ctypes.py_object
EnumChildWindows.restype = w.BOOL


@WNDENUMPROC
def getFromUWPCallback(hWnd, obj):
    PID = getWindowPID(hWnd)
    if PID:
        path = getThreadFullpathByPID(PID)
        if path != "C:\\Windows\\System32\\ApplicationFrameHost.exe":
            obj.append(path)
            return False
    return True


def getAppPathForUWP(hWnd):
    obj = []
    if EnumChildWindows(hWnd, getFromUWPCallback, obj) == False:
        return windowsPath(obj[0])
    return None


IsWindowVisible = user32.IsWindowVisible
IsIconic = user32.IsIconic
SetProcessDPIAware = user32.SetProcessDPIAware


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", w.DWORD),
        ("flags", w.DWORD),
        ("hwndActive", w.HWND),
        ("hwndFocus", w.HWND),
        ("hwndCapture", w.HWND),
        ("hwndMenuOwner", w.HWND),
        ("hwndMoveSize", w.HWND),
        ("hwndCaret", w.HWND),
        ("rcCaret", w.RECT),

    ]

    def __str__(self):
        ret = "\n" + self.__repr__()
        start_format = "\n  {0:s}: "
        for field_name, _ in self. _fields_[:-1]:
            field_value = getattr(self, field_name)
            field_format = start_format + \
                ("0x{1:016X}" if field_value else "{1:}")
            ret += field_format.format(field_name, field_value)
        rc_caret = getattr(self, self. _fields_[-1][0])
        ret += (start_format + "({1:d}, {2:d}, {3:d}, {4:d})").format(
            self. _fields_[-1][0], rc_caret.top, rc_caret.left, rc_caret.right, rc_caret.bottom)
        return ret


def getWindowThreadInfo(hWnd):
    tid, pid = wproc.GetWindowThreadProcessId(hWnd)
    log.logger.debug("PId: {0:d}, TId: {1:d}".format(pid, tid))
    GetGUIThreadInfo = user32.GetGUIThreadInfo
    GetGUIThreadInfo.argtypes = [w.DWORD, ctypes.POINTER(GUITHREADINFO)]
    GetGUIThreadInfo.restype = w.BOOL
    gti = GUITHREADINFO()
    gti.cbSize = ctypes.sizeof(GUITHREADINFO)
    res = GetGUIThreadInfo(tid, ctypes.byref(gti))
    log.logger.debug("{0:s} returned: {1:d}".format(
        GetGUIThreadInfo.__name__, res))
    if res:
        return gti
    return


def isWindowMoving(hWnd):
    gti = getWindowThreadInfo(hWnd)
    if gti:
        if gti.hwndMoveSize:
            log.logger.debug("window moving")
            return True
    return False


def windowsPath(path):
    return str(Path(path))


# def Lower_resolution(file_path, percentage):  # 降低分辨率（360*360）
#     # 修改之后的图片大小
#     img = cv2.imdecode(np.fromfile(
#         file_path, dtype=np.uint8), -1)  # 路径不能为中文解决方法
#     sp = img.shape
#     print(sp)
#     if sp[1] < 500 or sp[0] < 500:
#         size_ = (sp[1], sp[0])
#     else:
#         size_ = (int(sp[1]*percentage), int(sp[0]*percentage))
#     print(size_)
#     im2 = cv2.resize(img, size_, interpolation=cv2.INTER_AREA)
#     # saved_path = r'D:\Python\python3\picture processing\哈哈\kjfhkj_5453.JPG'
#     # cv2.imwrite(saved_path, im2)  #保存
#     # cv2.imencode('.png', im2)[1].tofile(file_path) # #路径不能为中文解决方法
#     return im2


# def increaseContrast(file_path, alpha, beta):
#     print("contrast!!!!!!!!!!!!!!!!!!!!!!!")
#     img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
#     new_image = np.zeros(img.shape, img.dtype)

#     for y in range(img.shape[0]):
#         for x in range(img.shape[1]):
#             for c in range(img.shape[2]):
#                 new_image[y, x, c] = np.clip(alpha*img[y, x, c] + beta, 0, 255)
#     cv2.imencode('.png', new_image)[1].tofile(file_path)
#     print("contrast end")

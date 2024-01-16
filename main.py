from multiprocessing import Process
import multiprocessing
import threading
from time import sleep
from WindowChangeObserver import IWindowChangeObserver, ObservableWindowChange
from data import database
from exThread import thread_with_exception
from ffmpeg import videoMain
from log import log
from ocr import ocrMain
from utils import getActiveWindowHandle
# pid = os.getpid()
# python_process = psutil.Process(pid)
# print("cpu:  ", psutil.cpu_percent(), "%")
# print("mem:  ",   python_process.memory_info()[0]/2.**30*1024, "mb")



process_list = []


class WindowObserver(IWindowChangeObserver):
    def notify(self, hWnd):
        log.logger.debug("notify")
        # stop previous process
        for i in process_list:
            print("close")
            i.raise_exception()
        process_list.clear()
        # multiprocessing.freeze_support()
        # start a new process
        p = thread_with_exception(hWnd)
        p.start()
        process_list.append(p)


def main():
    db = database()
    db.initTable()
    # before listener
    hWnd = getActiveWindowHandle()
    # multiprocessing.freeze_support()
    pp = thread_with_exception(hWnd)
    pp.start()
    process_list.append(pp)

    # listen window change
    subject = ObservableWindowChange()
    observer = WindowObserver(subject)
    subject.start_event_listener()
    


# def console_handler(signal):
#     print(f"Console handler (signal {signal})!")
#     global keep_running
#     keep_running = False
#     # Sleep until process either finishes or is killed by the OS
#     time.sleep(20)
#     return True
# start
if __name__ == "__main__":
    # yappi.start()
    multiprocessing.freeze_support()
    log.logger.info(
        "=======================================start======================================")
    # log.logger.info("config %s",confDict)
    keep_running = True
    # win32api.SetConsoleCtrlHandler(console_handler, 1)
    t = threading.Thread(target=main)
    t.daemon = True
    t.start()
    ocr_process = Process(target = ocrMain)
    ocr_process.start()

    video_process = Process(target=videoMain)
    video_process.start()
    # Keep the main thread running in a sleep loop until ctrl+c (SIGINT) is caught.
    # Once the main thread terminates, all daemon threads will automatically
    # terminate.
    # main()
    while keep_running:
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            ocr_process.terminate()
            video_process.terminate()
            # yappi.get_func_stats().strip_dirs().print_all()
            # yappi.get_thread_stats().print_all()
            break

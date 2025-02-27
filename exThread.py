import threading
import ctypes
from log import log
from Screenshot import getInfoAndScreenshot
  
class thread_with_exception(threading.Thread):
    def __init__(self, hWnd):
        threading.Thread.__init__(self)
        self.hWnd = hWnd
             
    def run(self):
        # target function of the thread class
        try:
           getInfoAndScreenshot(self.hWnd)
        finally:
            log.logger.debug('thread ended')
          
    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            log.logger.debug('Exception raise failure')
import datetime
from time import sleep
from GetUrl import BrowserWindow
from data import database

from log import log
from conf import conf

from utils import current_milli_time, SetProcessDPIAware, IsIconic, IsWindowVisible, getAppPathForUWP, getWindowPID, getThreadFullpathByPID, getAppNameFromPath, getWindowRect, getWindowTitle, screenshot, isWindowMoving, windowsPath


# main screenshot method

SUPPORTED_BROWSERS = ['Google Chrome', 'Firefox', 'Microsoft Edge', 'Opera']


def getInfoAndScreenshot(hWnd):
    db = database()
    oldWindowTitle = None
    PID = None
    fullpath = None
    name = None
    SetProcessDPIAware(2)
    first = True
    rowId = None
    while True:
        if (not IsWindowVisible(hWnd)) or IsIconic(hWnd):
            log.logger.debug("visible %s", IsWindowVisible(hWnd))
            log.logger.debug("Iconic %s", IsIconic(hWnd))
            sleep(0.2)
            continue
        if first:
            PID = getWindowPID(hWnd)
            if PID.value == 0:
                log.logger.warning("PID.value = 0")
                break
            fullpath = getThreadFullpathByPID(PID)
            if fullpath == windowsPath("C:\Windows\System32\ApplicationFrameHost.exe"):
                log.logger.debug('UWP')
                fullpath = getAppPathForUWP(hWnd)
            if not fullpath in conf['screen']['white_list']:
                log.logger.debug("not in whitelist %s", fullpath)
                break
            name = getAppNameFromPath(fullpath).rstrip('\x00')
            log.logger.debug(name)

        start = datetime.datetime.now()
        if name:
            url = ""
            if name in SUPPORTED_BROWSERS:
                # TODO:url time too long
                start = datetime.datetime.now()
                browser = BrowserWindow(name)
                # TODO: sometimes url is None because find step is always slower than timeout
                url = browser.current_tab_url
                log.logger.debug("url time: %s  %s",
                                 datetime.datetime.now()-start, url)
            # TODO:check if incognito window

            # check title
            title = getWindowTitle(hWnd)
            # if not a new window, sleep accroding to the config
            if (not title) or (oldWindowTitle and oldWindowTitle == title):
                sleep(int(conf['screen']['shot_interval']))
             # check if the window is on the move
            if isWindowMoving(hWnd):
                timer = 0
                while isWindowMoving(hWnd):
                    if timer > 10:
                        break
                    sleep(0.1)
                    timer = timer + 1
                continue
            rect = getWindowRect(hWnd)
            now = current_milli_time()

            imageFilename = screenshot(rect)
            # save to database for an existed segment(update endtime)

            info = (name, now, now, title, url, fullpath)
            if first:
                rowId = db.addSegment(*info)
            elif rowId:
                if oldWindowTitle != title:
                    # add new
                    rowId = db.addSegment(*info)
                else:
                    # update
                    db.updateSegment(rowId, now)
            # add new frame record

            # ocrResult = ocr(imageFilename)
            frameInfo = (now, imageFilename, rowId, 0, 0, title, "")
            db.addFrame(*frameInfo)
            # db.addOcr(ocrResult,"")
            # db.findOcr('Object')
            log.logger.info(info)
            log.logger.debug(frameInfo)
            oldWindowTitle = title

            first = False
            end = datetime.datetime.now()
            log.logger.debug("Screenshot Full Time: %s", end-start)

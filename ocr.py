from utils import windowsOcrPath, picDir,goodOcrPath
from log import log
import datetime
import os
import re
import subprocess
from time import sleep
import psutil
# from rapidocr_onnxruntime import RapidOCR
from data import database
from conf import conf
from wordNinja import ninjaSplit
# rapid_ocr = RapidOCR()

# wordninja.DEFAULT_LANGUAGE_MODEL = wordninja.LanguageModel(str(wordninja_path))

def ocr(path):
    result = ""
    if conf['screen']['ocr_type'] == 'fast':
        result = fastOcr(path)
    elif conf['screen']['ocr_type'] == 'precise':
        result = preciseOcr(path)
    log.logger.debug(result)
    return result


def preciseOcr(path):
    start = datetime.datetime.now()
    result = subprocess.Popen([goodOcrPath,"--src", path], shell=True,
                              stdout=subprocess.PIPE).stdout.read()
    line = " ".join(result.decode("gbk").splitlines())
    end = datetime.datetime.now()
    # log.logger.debug(lines)
    log.logger.info("++++++++++++++++++++++++++++OCR Time: %s", end-start)
    return line

# def preciseOcr(path):
#     start = datetime.datetime.now()
#     # imag = Lower_resolution(path,0.8)
#     result = rapid_ocr(path)
#     end = datetime.datetime.now()
#     log.logger.info("++++++++++++++++++++++++++++OCR Time: %s", end-start)
#     stringResult = []
#     for a in result[0]:
#         stringResult.append(a[1])
#     return " ".join(stringResult)


def only_letters(tested_string):
    match = re.match("^[a-zA-Z]*$", tested_string)
    return match is not None


def fastOcr(path):
    start = datetime.datetime.now()
    # increaseContrast(path,1.2,0)
    result = subprocess.Popen([windowsOcrPath, path], shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
    lines = " ".join(result.decode('gbk').splitlines())
    a = re.split(r'([a-zA-Z]+)', lines)
    r = []
    for aa in a:
        if only_letters(aa):
            aa = " ".join(ninjaSplit(aa))
        r.append(aa)

    end = datetime.datetime.now()
    log.logger.info("++++++++++++++++++++++++++++OCR Time: %s", end-start)
    return " ".join(r)


def ocrMain():
    log.logger.info("ocrmain process start, %s", os.getpid())
    p = psutil.Process(os.getpid())
    # p.nice(psutil.HIGH_PRIORITY_CLASS)
    # find un-ocr-ed frame
    db = database()
    while True:
        sleep(2)

        rows = db.findUnocredFrame()
        for row in rows:
            start = datetime.datetime.now()
            id = row[0]
            imageName = row[1]
            if imageName:
                imagePath = picDir / imageName
                if imagePath.exists():
                    content = ocr(imagePath)
                    db.addOcr(id, content)
                else:
                    log.logger.debug("imagepath does not exists %s",imagePath)
                    db.failOcr(id)
            else:
                log.logger.debug("no image name")
            end = datetime.datetime.now()
            log.logger.info(
                "++++++++++++++++++++++++++++OCR Time: %s", end-start)

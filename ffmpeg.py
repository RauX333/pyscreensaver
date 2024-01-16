import datetime
import os
import subprocess
from time import sleep

import psutil
from utils import current_milli_time, picDir,ffmpeg_path
from log import log
from data import database

# p = picDir.glob('**/*')
# files = [x for x in p if x.is_file()]

ffmpegPath =str(ffmpeg_path)

# put -r before -i, or ffmpeg will miss some frames


def genVideo(files):
    videoName = str(current_milli_time()) + '.mp4'
    print(videoName)
    print(files)
    # flag order matters in ffmpeg
    cmd_ffmpeg = [ffmpegPath,'-y','-r','2','-i','-','-s','1920x1080','-vcodec','libx264',videoName]
    process = subprocess.Popen(cmd_ffmpeg, shell=True,stdin=subprocess.PIPE)
    for in_file in files:
        if not in_file.is_file():
           log.logger.error('file does not exists %s',in_file)
           continue
        with open(in_file, 'rb') as f:
            # Read the JPEG file content to jpeg_data (bytes array)
            png_data=f.read()
            # Write JPEG data to stdin pipe of FFmpeg process
            process.stdin.write(png_data)

    # Close stdin pipe - FFmpeg fininsh encoding the output file.
    process.stdin.close()
    process.wait()
    # process.communicate()
    if process.returncode !=0: raise subprocess.CalledProcessError(process.returncode,cmd_ffmpeg)
    return 

# genVideo(files)

def videoMain():
    log.logger.info("ocrmain process start, %s", os.getpid())
    p = psutil.Process(os.getpid())

    db = database()
    while True:
        #TODO: save energy mode
        sleep(30)
        start = datetime.datetime.now()
        frames = db.findUnEncodedFrames()
        files = []
        ids = []
        if not len(frames):
           continue
        print(frames)
        for f in frames:
           files.append(picDir / f[1])
           ids.append(f[0])
        try:
          videoName = genVideo(files)
        except:
          # TODOif error
          log.logger.error('Something went wrong')
        finally:
            for id in ids:
               if id:
                  db.updateEncodedFrame(id)
            print('The try except is finished')
        end = datetime.datetime.now()
        log.logger.info(
                "++++++++++++++++++++++++++++gen video Time: %s", end-start)

          # mark frame encode status as 1
          # delete files
        
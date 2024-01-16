Inspired by [Rewind](https://www.rewind.ai/), an application to remember anyting ever happened on your mac. this [blog](https://kevinchen.co/blog/rewind-ai-app-teardown/) explained how it's done. So I wonder if I can write one for windows.

## introductions


## installation
1. clone the codes.
2. download [ffmpeg.exe](https://ffmpeg.org/download.html) and put it in `ffmpeg/ffmpeg.exe`

## config
change configurations in `conif.ini`.
shot_interval: time interval to take screenshots
white_list: only take screenshots of the applications in the whitelist 
ocr_type: precise or fast
##  test run
```python main.py```

## build
you can build it into an exe using pyinstaller by ```pyinstaller --clean .\screen_saver.spec```

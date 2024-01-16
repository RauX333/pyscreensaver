Inspired by [Rewind](https://www.rewind.ai/), an application that remembers everything that happened on your Mac. This [blog](https://kevinchen.co/blog/rewind-ai-app-teardown/) explains how it's done. So, I wondered if I could create a similar application for Windows.

## Introduction
This application captures screenshots of your screen and performs OCR (Optical Character Recognition) on them. The results are saved in a SQLite database for further use. It also generates videos using the captured images. You can use a database browser to view all the results.

In my tests, the OCR performance on Windows using third-party utilities was not as satisfying as what Rewind showed on Mac.

## Installation
1. Clone the repository.
2. Download [ffmpeg.exe](https://ffmpeg.org/download.html) and place it in the `ffmpeg/` folder as `ffmpeg.exe`.

## Configuration
Modify the settings in the `config.ini` file.
- `shot_interval`: Time interval between screenshots.
- `white_list`: Only capture screenshots of applications in the whitelist.
- `ocr_type`: Choose between precise or fast OCR.

## Test Run
Run the following command to execute the application:
``` python main.py ```

## Build
To build the application into an executable using PyInstaller, run the following command:
```pyinstaller --clean .\screen_saver.spec```

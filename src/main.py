import sys
import os

import pyocr
import pyocr.builders
import pyautogui
import cv2
import numpy as np

from PIL import Image, ImageEnhance, ImageOps

PATH_TO_IMG = '/Users/tena/Desktop/cap.png'
PATH_TO_MODELS = "/usr/local/Cellar/tesseract/5.2.0/share/tessdata"

def setup():
    # Path to a directory of Tesseract-OCR models
    path = PATH_TO_MODELS
    path_list = os.environ["PATH"].split(os.pathsep)
    if path not in path_list:
        os.environ["PATH"] += os.pathsep + path

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    # Ex: Will use tool 'libtesseract'
    print("Will use tool '%s'" % (tool.get_name()))

    langs = tool.get_available_languages()
    print("Available languages: %s" % ", ".join(langs))
    lang = langs[0]
    print("Will use lang '%s'" % (lang))
    # Ex: Will use lang 'fra'
    # Note that languages are NOT sorted in any way. Please refer
    # to the system locale settings for the default language
    # to use.

    return tool, lang

def image2text(tool, lang="jpn", style=3):
    image = Image.open(PATH_TO_IMG)
    gray = image.convert('L') # グレースケールに変換
    cont = ImageEnhance.Contrast(gray).enhance(3) # コントラストを強調

    border = 200
    arr = np.array(cont)
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            arr[i][j] = (arr[i][j] < border) * 255
            # pix = arr[i][j]
            # if pix[0] >= border or pix[1] >= border or pix[2] >= border: # 白文字は黒に
            #     arr[i][j] = [0, 0, 0, 255]
            # elif pix[0] < border or pix[1] < border or pix[2] < border: # 暗めの色は白に
            #     arr[i][j] = [255, 255, 255, 255]

    result = Image.fromarray(arr)
    result.show()
    text = tool.image_to_string(
        result,
        lang=lang,
        builder=pyocr.builders.TextBuilder(style))

    print(text)

def ScreenShot(x1, y1, x2, y2):
    sc = pyautogui.screenshot(region=(x1, y1, x2, y2))
    sc.save('TransActor.jpg')
    img = cv2.imread('TransActor.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tmp = cv2.resize(gray, (gray.shape[1]*2, gray.shape[0]*2), interpolation=cv2.INTER_LINEAR)
    cv2.imwrite('TransActor.jpg', tmp)

if __name__ == '__main__':
    tool, _ = setup()
    # styleについて
    # 0 = Orientation and script detection (OSD) only.
    # 1 = Automatic page segmentation with OSD.
    # 2 = Automatic page segmentation, but no OSD, or OCR. (not implemented)
    # 3 = Fully automatic page segmentation, but no OSD. (Default)
    # 4 = Assume a single column of text of variable sizes.
    # 5 = Assume a single uniform block of vertically aligned text.
    # 6 = Assume a single uniform block of text.
    # 7 = Treat the image as a single text line.
    # 8 = Treat the image as a single word.
    # 9 = Treat the image as a single word in a circle.
    # 10 = Treat the image as a single character.
    # 11 = Sparse text. Find as much text as possible in no particular order.
    # 12 = Sparse text with OSD.
    # 13 = Raw line. Treat the image as a single text line,
    #     bypassing hacks that are Tesseract-specific.
    image2text(tool, style=4)

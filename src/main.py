import sys
import os

import pyocr
import pyocr.builders
import numpy as np

from PIL import Image, ImageEnhance, ImageOps, ImageDraw


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


def image2text(image, tool, lang="jpn", style=3):
    border = 200

    gray = image.convert('L') # グレースケールに変換
    cont = ImageEnhance.Contrast(gray).enhance(3) # コントラストを強調

    arr = np.array(cont)
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            arr[i][j] = (arr[i][j] < border) * 255 # 明度で二値化

    result = Image.fromarray(arr)
    result.show()

    text = tool.image_to_string(
        result,
        lang=lang,
        builder=pyocr.builders.TextBuilder(style))

    print(text)


def splitImage(image: Image.Image, rects):
    segments = []
    draw = ImageDraw.Draw(image)

    for rect in rects:
        segments.append(image.crop(rect))
        draw.rectangle(rect, outline=(255, 0, 0))

    # image.save("split.png")
    return segments


if __name__ == '__main__':
    tool, _ = setup()
    image = Image.open(PATH_TO_IMG)
    rects = [
        # 左上x, 左上y, 右下x, 右下y
        (1280, 200, 2000, 1200),# 概要
        (2000, 200, 2500, 1200),# 詳細
    ]
    segments = splitImage(image, rects)
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
    for segment in segments:
        image2text(image=segment, tool=tool, style=4)

from json import tool
import sys
import os
import time
from tracemalloc import start

import pyocr
import pyocr.builders
import tesserocr
import unicodedata
import numpy as np

from PIL import Image, ImageEnhance, ImageOps, ImageDraw

from multiprocessing import Pool
import multiprocessing as multi

from item import Extension, Element, Segment, normalize_text


PATH_TO_IMG_1 = '/Users/tena/Desktop/cap.png'
PATH_TO_IMG_2 = '/Users/tena/Desktop/capture2.png'
PATH_TO_MODELS = '/usr/local/Cellar/tesseract/5.2.0/share/tessdata'


def print_time(start: float, message: str):
    elapsed_time = time.time() - start
    # print(message + ": {0}".format(elapsed_time) + "[sec]")
    print(message + ": {0}".format(elapsed_time))


def available_tools():
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print('No OCR tool found')
        sys.exit(1)
    print('Available tool:')
    for tool in tools:
        print(tool.get_name())
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    # Ex: Will use tool 'libtesseract'
    print('Will use tool "%s"' % (tool.get_name()))

    langs = tool.get_available_languages()
    print('Available languages: %s' % ', '.join(langs))
    # lang = langs[0]
    # print('Will use lang "%s"' % (lang))
    # Ex: Will use lang 'fra'
    # Note that languages are NOT sorted in any way. Please refer
    # to the system locale settings for the default language
    # to use.


def recommended_tool():
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print('No OCR tool found')
        sys.exit(1)
    return tools[0]


def image_to_string(inputs: tuple[Image.Image, Element]):
    tool = recommended_tool()
    image = inputs[0]
    elem = inputs[1]
    lang, builder = Element.EXTENSION_PROP[elem.extension]

    start = time.time()
    text = tool.image_to_string(image, lang, builder)
    print_time(start, elem.extension.name)

    text = normalize_text(text, elem.extension)
    # if elem.extension == Extension.IMG:
    #     image.show()
    return text


def split_image(image: Image.Image, rect: tuple[int, int, int, int]):
    # draw = ImageDraw.Draw(image)

    segment = image.crop(rect)

    # r = 1
    # segment = crop.resize((round(segment.width*r), round(segment.height*r)))

    # 切り抜き範囲
    # draw.rectangle(rect, outline=(255, 0, 0))

    # 横線
    # start = (0, 100)
    # end = (2560, 100)
    # for i in range(14):
    #     r = 50 * ((i % 5) + 1)
    #     draw.line((start, end), fill=(r, 0, 0), width=2)
    #     start = (start[0], start[1] + 100)
    #     end = (end[0], end[1] + 100)

    # 縦線
    # start = (100, 0)
    # end = (100, 1440)
    # for i in range(25):
    #     g = 50 * ((i % 5) + 1)
    #     draw.line((start, end), fill=(0, g, 0), width=2)
    #     start = (start[0] + 100, start[1])
    #     end = (end[0] + 100, end[1])

    gray = segment.convert('L') # グレースケールに変換
    cont = ImageEnhance.Contrast(gray).enhance(3) # コントラストを強調

    arr = np.array(cont)
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            arr[i][j] = (arr[i][j] < 200) * 255 # 明度で二値化

    segment = Image.fromarray(arr)
    # segment.show()

    return segment


if __name__ == '__main__':
    start = time.time()

    # スレッド数
    njobs = 1
    if multi.cpu_count() > 2:
        njobs = multi.cpu_count() - 1

    # Path to a directory of Tesseract-OCR models
    path = PATH_TO_MODELS
    path_list = os.environ['PATH'].split(os.pathsep)
    if path not in path_list:
        os.environ['PATH'] += os.pathsep + path
    available_tools()

    # 画面構成の定義(TODO: GUI実装)
    items = Segment('Item')
    items.append(Segment('防具', ((0, 0), (2560, 1440))))
    armors = items['防具']
    if type(armors) is Segment:

        armors.append(Segment('詳細', (2000, 200, 2500, 1200)))
        details = armors['詳細']
        if type(details) is Segment:

            details.append(Segment('1'))
            page1 = details['1']
            if type(page1) is Segment:
                page1.append(Element('名称', (2100, 300, 2500, 350), Extension.LBL))
                page1.append(Element('RARE', (2475, 350, 2500, 400), Extension.VAL))
                page1.append(Element('Lv', (2470, 400, 2500, 450), Extension.VAL))
                page1.append(Element('防御力', (2440, 450, 2500, 500), Extension.VAL))
                page1.append(Element('スロット1', (2330, 495, 2390, 555), Extension.IMG))
                page1.append(Element('スロット2', (2390, 495, 2447, 555), Extension.IMG))
                page1.append(Element('スロット3', (2448, 495, 2500, 555), Extension.IMG))
                page1.append(Element('火', (2450, 550, 2500, 600), Extension.VAL))
                page1.append(Element('水', (2450, 600, 2500, 650), Extension.VAL))
                page1.append(Element('雷', (2450, 650, 2500, 700), Extension.VAL))
                page1.append(Element('氷', (2450, 700, 2500, 750), Extension.VAL))
                page1.append(Element('龍', (2450, 750, 2500, 800), Extension.VAL))

            details.append(Segment('2'))
            page2 = details['2']
            if type(page2) is Segment:
                page2.append(Element('説明', (2040, 400, 2500, 510), Extension.TXT))
                page2.append(Element('スキル1', (2070, 620, 2300, 670), Extension.LBL))
                page2.append(Element('スキル1Lv', (2470, 670, 2500, 720), Extension.VAL))
                page2.append(Element('スキル2', (2070, 720, 2300, 770), Extension.LBL))
                page2.append(Element('スキル2Lv', (2470, 770, 2500, 830), Extension.VAL))
                page2.append(Element('スキル3', (2070, 820, 2300, 870), Extension.LBL))
                page2.append(Element('スキル3Lv', (2470, 870, 2500, 920), Extension.VAL))

            # テキストの取得
            # 画像は本当はページ番号で判別するが一旦強制
            segments: list[tuple[Image.Image, Element]] = []
            capture1 = Image.open(PATH_TO_IMG_1)
            capture2 = Image.open(PATH_TO_IMG_2)
            for elem in page1.values():
                segments.append((split_image(capture1, elem.pos), elem))
            for elem in page2.values():
                segments.append((split_image(capture2, elem.pos), elem))
            print_time(start, 'セグメンテーション')

            # 並列化
            process = Pool(njobs)
            texts = process.map(image_to_string, segments)
            process.close()

            for i, elem in enumerate(page1.values()):
                elem.value = texts[i]
            for i, elem in enumerate(page2.values()):
                elem.value = texts[len(page1)+i]

            # capture1.save("split1.png")
            # capture2.save("split2.png")
            print(page1)
            print(page2)

    print_time(start, '実行時間')
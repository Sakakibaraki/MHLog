import sys
import os

import pyocr
import pyocr.builders
import unicodedata
import numpy as np

from PIL import Image, ImageEnhance, ImageOps, ImageDraw

from item import Element, Segment


PATH_TO_IMG_1 = '/Users/tena/Desktop/cap.png'
PATH_TO_IMG_2 = '/Users/tena/Desktop/capture2.png'
PATH_TO_MODELS = '/usr/local/Cellar/tesseract/5.2.0/share/tessdata'


def setup():
    # Path to a directory of Tesseract-OCR models
    path = PATH_TO_MODELS
    path_list = os.environ['PATH'].split(os.pathsep)
    if path not in path_list:
        os.environ['PATH'] += os.pathsep + path

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print('No OCR tool found')
        sys.exit(1)
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    # Ex: Will use tool 'libtesseract'
    print('Will use tool "%s"' % (tool.get_name()))

    langs = tool.get_available_languages()
    print('Available languages: %s' % ', '.join(langs))
    lang = langs[0]
    print('Will use lang "%s"' % (lang))
    # Ex: Will use lang 'fra'
    # Note that languages are NOT sorted in any way. Please refer
    # to the system locale settings for the default language
    # to use.

    return tool, lang


def image2text(image: Image.Image, tool, lang='jpn', style=3):
    border = 200

    gray = image.convert('L') # グレースケールに変換
    cont = ImageEnhance.Contrast(gray).enhance(3) # コントラストを強調

    arr = np.array(cont)
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            arr[i][j] = (arr[i][j] < border) * 255 # 明度で二値化

    result = Image.fromarray(arr)
    # result.show()

    # OCRで画像からテキストを読み出す
    text = tool.image_to_string(
        result,
        lang=lang,
        builder=pyocr.builders.TextBuilder(style))

    # 改行含めてひとつのstrとして返されるので分割する
    if type(text) is str:
        lines = text.split('\n')
    # print(lines)

    normals = []
    for line in lines:
        # 数字が丸文字として検出されることがある
        normal = ''
        for chara in line:
            # 一文字ずつ対応する
            if chara is ' ':
                continue
            normal += str(unicodedata.normalize('NFKC', chara)) # NOTE: 正直どれくらい直してくれるかわからない
        normals.append(normal)

    return normals


def splitImage(image: Image.Image, rect):
    draw = ImageDraw.Draw(image)

    r = 1
    # for rect in rects:
    crop = image.crop(rect)
    segment = crop.resize((round(crop.width*r), round(crop.height*r)))

    # draw.rectangle(rect, outline=(255, 0, 0))

    # start = (0, 100)
    # end = (2560, 100)
    # for i in range(14):
    #     r = 50 * ((i % 5) + 1)
    #     draw.line((start, end), fill=(r, 0, 0), width=2)
    #     start = (start[0], start[1] + 100)
    #     end = (end[0], end[1] + 100)

    # start = (100, 0)
    # end = (100, 1440)
    # for i in range(25):
    #     g = 50 * ((i % 5) + 1)
    #     draw.line((start, end), fill=(0, g, 0), width=2)
    #     start = (start[0] + 100, start[1])
    #     end = (end[0] + 100, end[1])

    image.save("split.png")
    return segment


if __name__ == '__main__':
    tool, _ = setup()
    size = (2560, 1440)
    # styleについて
    # 0 = Orientation and script detection (OSD) only.(不使用)
    # 1 = Automatic page segmentation with OSD.(離れた部分が削除される)
    # 2 = Automatic page segmentation, but no OSD, or OCR. (not implemented)(不使用)
    # 3 = Fully automatic page segmentation, but no OSD. (Default)(離れた部分が削除される)
    # 4 = Assume a single column of text of variable sizes.(そこそこ使いやすい)
    # 5 = Assume a single uniform block of vertically aligned text.(縦向きに読まれて変になる)
    # 6 = Assume a single uniform block of text.(いい感じかもしれない)
    # 7 = 画像を1行のテキストとして扱います
    # 8 = 画像を一単語として扱います
    # 9 = 画像を円の中の一単語として扱います
    # 10 = 画像を一つの文字として扱います
    # 11 = Sparse text. Find as much text as possible in no particular order.(離れた部分が削除される; 0がなくなる)
    # 12 = Sparse text with OSD.(同上)
    # 13 = Raw line. Treat the image as a single text line,
    #     bypassing hacks that are Tesseract-specific.(ダメダメ)

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
                page1.append(Element('名称', (2100, 280, 2500, 360)))
                page1.append(Element('RARE', (2470, 350, 2500, 400)))
                page1.append(Element('Lv', (2400, 400, 2500, 450)))
                page1.append(Element('防御力', (2400, 450, 2500, 500)))
                page1.append(Element('スロット', (2300, 495, 2500, 555)))
                page1.append(Element('火', (2400, 550, 2500, 600)))
                page1.append(Element('水', (2400, 600, 2500, 650)))
                page1.append(Element('雷', (2400, 650, 2500, 700)))
                page1.append(Element('氷', (2400, 700, 2500, 750)))
                page1.append(Element('龍', (2400, 750, 2500, 800)))

            details.append(Segment('2'))
            page2 = details['2']
            if type(page2) is Segment:
                page2.append(Element('説明', (2040, 400, 2500, 510)))
                page2.append(Element('スキル1', (2070, 610, 2400, 670)))
                page2.append(Element('スキル1Lv', (2450, 650, 2500, 720)))
                page2.append(Element('スキル2', (2070, 710, 2400, 770)))
                page2.append(Element('スキル2Lv', (2450, 750, 2500, 820)))
                page2.append(Element('スキル3', (2070, 810, 2400, 870)))
                page2.append(Element('スキル3Lv', (2450, 850, 2500, 920)))

            # テキストの取得
            # 画像は本当はページ番号で判別するが一旦強制
            for elem in page1.values():
                capture = Image.open(PATH_TO_IMG_1)
                segment = splitImage(capture, elem.pos)
                elem.value.append(image2text(image=segment, tool=tool, style=6))
                print(elem.name, elem.value)

            for elem in page2.values():
                capture = Image.open(PATH_TO_IMG_2)
                segment = splitImage(capture, elem.pos)
                elem.value.append(image2text(image=segment, tool=tool, style=6))
                print(elem.name, elem.value)

from enum import Enum, auto
from collections import UserDict
from typing import Any
import unicodedata

from pyocr import builders, tesseract


class Extension(Enum):
    """
    Element型の拡張子
    """
    # Element
    TXT = auto() # 複数行・複数列の可能性のある日本語
    IMG = auto() # 画像・アイコン
    VAL = auto() # 数値
    LBL = auto() # ラベル

    # Segment
    SEG = auto() # 範囲


def normalize_text(text: str, extension: Extension):
        # 改行含めてひとつのstrとして返されるので分割する
        if type(text) is str:
            lines = text.split('\n')

        # 一文として返す(NOTE: list化が必要な場合もある？)
        normalized: str = ''
        for line in lines:
            for chara in line:
                # 空白は削除(NOTE: 必要な空白が消える可能性もある？)
                if chara == ' ':
                    continue
                # 数字が丸文字として検出されることがある
                normalized += str(unicodedata.normalize('NFKC', chara)) # NOTE: 正直どれくらい直してくれるかわからない

        return normalized


class Element:
    """
    具体的なプロパティに対応する
    """

    def __init__(self, name: str, pos: tuple[tuple[float, float], tuple[float, float]] = None, extension: Extension = Extension.TXT):
        """
        @input name 自分の名前
        @input pos 枠を取った時の(絶対)座標(左上xy, 右下xy)
        """

        self.name = name
        self.pos = pos
        self.extension = extension
        self.value: str = None

        self.parent: Segment = None
        """
        Elementクラスのparentは自身がSegmentに追加された時に決定される
        (Elementには必ず親がいる)
        """

    """
    Builderの引数メモ
    @param tesseract_layout
        0 (非対応) テキストの傾斜角度や言語の種類を検知（OSD）して出力
        1 OSDありでOCR（回転した画像にも対応してOCR可）
        2 (非対応) OSDなしでテキストの傾斜角度情報を標準出力（OCRなし）
        3 OSDなしでOCR（デフォルトの設定はこれ）
        4 単一列にさまざまなテキストサイズが入り混じったものと想定してOCR
        5 縦書きのまとまった文章と想定してOCR
        6 横書きのまとまった文章と想定してOCR
        7 一行の文章と想定してOCR
        8 一単語と想定してOCR
        9 円の中に一単語がある想定でOCR（①、➁など）
        10 一文字と想定してOCR
        11 順序を気にせずできるだけ画像内に含まれる文章をOCRで取得
        12 OSDありでできるだけ画像内に含まれる文章をOCRで取得
        13 Tesseract固有の処理を飛ばして一行の文章としてOCR処理
    """
    EXTENSION_PROP: dict[Extension, tuple[str, Any]] = {
        Extension.TXT: ('jpn', builders.TextBuilder(6)), # 文章
        Extension.IMG: ('eng', builders.TextBuilder(8)), # 画像(TODO)
        Extension.VAL: ('eng', builders.DigitBuilder(10)), # 数字
        Extension.LBL: ('jpn', builders.TextBuilder()), # スキル名などの単文
        Extension.SEG: ('jpn', builders.TextBuilder(6)), # 範囲
    }


class Segment(Element, UserDict[str, Element]):
    """
    グループや一つのアイテムの本体などに対応する
    """

    def __init__(self, name: str, pos: tuple[tuple[float, float], tuple[float, float]] = None, children: list[Element] = None, style = 6):
        super(Segment, self).__init__(name, pos, style)

        self.data = {}
        if children is not None:
            for elem in children:
                self.data[elem.name] = elem
                elem.parent = self

    def update(self, **kwargs: Element):
        self.update(kwargs) # これで追加できている？新しいキーの場合はその処理も書いた方がいい？
        # NOTE: とりあえずの実装。なんかいちいちparent設定してそう
        for elem in kwargs.values():
            if elem.parent is not self:
                elem.parent = self

    def append(self, elem: Element):
        self.data[elem.name] = elem
        elem.parent = self
        if elem.pos is None:
            elem.pos = self.pos

    def __str__(self):
        dictionary = {}
        for elem in self.data.values():
            dictionary[elem.name] = elem.value
        return dictionary.__str__()

from collections import UserDict


class Element:
    """
    具体的なプロパティに対応する
    """

    def __init__(self, name: str, pos: tuple[tuple[float, float], tuple[float, float]] = None):
        """
        @input name 自分の名前
        @input pos 枠を取った時の(絶対)座標(左上xy, 右下xy)
        """

        self.name = name
        self.pos = pos
        self.value: list[str] = []

        self.parent: Segment = None
        """
        Elementクラスのparentは自身がSegmentに追加された時に決定される
        (Elementには必ず親がいる)
        """


class Segment(Element, UserDict[str, Element]):
    """
    グループや一つのアイテムの本体などに対応する
    """

    def __init__(self, name: str, pos: tuple[tuple[float, float], tuple[float, float]] = None, children: list[Element] = None):
        super(Segment, self).__init__(name, pos)

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

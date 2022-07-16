class Item:
    def __init__(self, *args):
        """
        コンストラクタ
        """
        # publicメンバ
        self.name = 'name'
        self.defined_value = {}
        # privateメンバ
        self.__misdefined_values = {
            'LV': self.DATA_NAME[1],
            '防御カ': self.DATA_NAME[2],
        }

    # クラス定数
    DATA_NAME = [
        'RARE',
        'Lv',
        '防御力',
        'スロット',
        '火耐性',
        '水耐性',
        '雷耐性',
        '龍耐性',
    ]

    # public関数
    def register(self, text: str):
        # 空白を除去する
        text = text.replace(' ', '')

        # データ名のいずれかを含むか探索する
        for name in self.DATA_NAME:
            index = text.find(name)
            if index != -1:
                # データ名を含む場合

                # 続く数値を登録する
                self.defined_value[name] = text[index+len(name):]

                # TODO: 登録済みだった場合の処理

                # TODO: 数値が続かない場合、特殊な項目については履歴を残す
                # self.defined_value[value] = self.defined_value[name]

                # TODO: 他のnameも含まれている場合の処理
                return

        # データ名を含まない場合
        # 誤検出リストにあるか調べる
        for name_mis, name in self.__misdefined_values.items():
            index = text.find(name_mis)
            if index != -1:
                # 誤検出リストにある場合
                self.defined_value[name] = text[index+len(name_mis):]
                return

    # private関数

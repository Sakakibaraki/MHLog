from multiprocessing import Event
import os
import tkinter as tk
from tkinter import filedialog, EventType

# pillow
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageTk

import item


def e2s(event: EventType, num: int = None):
    """
    EventTypeのEnumからイベント名を入力できる
    tkinterの仕様よく知らないのにすごく適当に追加した関数
    """
    if num is None:
        return '<' + event.name + '>'
    else:
        return '<' + event.name + '-' + str(num) + '>'


class MainWindow:
    def __init__(self):
        #==============================
        # プライベートメンバ
        #==============================
        self.root = tk.Tk('Main Window')
        self.display_width = self.root.winfo_screenwidth()
        self.display_height = self.root.winfo_screenheight()
        self.item = item.Segment('Top')
        self.drawing = False

        #==============================
        # UI
        #==============================
        self.root.geometry('400x300')

        # ファイルピッカ
        fileButton = tk.Button(self.root, text='Open Image File', width=20)
        fileButton.bind(e2s(EventType.ButtonPress), self.file_dialog)
        fileButton.pack()

        # 選択したファイル
        self.file_name = tk.StringVar()
        self.file_name.set('Not Selected')
        label = tk.Label(textvariable=self.file_name, font=('', 12))
        label.pack()

        # セグメントの定義
        settingButton = tk.Button(self.root, text='Setting', width=10)
        settingButton.bind(e2s(EventType.ButtonPress), self.__on_setting_button_pressed)
        settingButton.pack()

        # セグメンテーション
        inputButton = tk.Button(self.root, text='Start Input', width=10)
        inputButton.bind(e2s(EventType.ButtonPress), self.__on_input_button_pressed)
        inputButton.pack()

        # OCRとデータベースの出力
        outputButton = tk.Button(self.root, text='Start Output', width=10)
        outputButton.bind(e2s(EventType.ButtonPress), self.__on_output_button_pressed)
        outputButton.pack()

    def start(self):
        self.root.mainloop()

    def file_dialog(self, event):
        fTyp = [('image', ['png', 'jpg', 'jpeg']), ('all', '*')]
        iDir = os.path.abspath(os.path.dirname(__file__))
        file_name = filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
        if len(file_name) == 0:
            self.file_name.set('canceled')
        else:
            self.file_name.set(file_name)


    #==================================================
    # ジェネレータ
    #==================================================
    def __create_setting_dialog(self):
        img = Image.open(self.file_name.get())

        # 画面の半分に画像をリサイズする
        dialog_width = self.display_width / 2
        change_rate = dialog_width / img.width
        img.thumbnail((img.width * change_rate, img.height * change_rate), Image.ANTIALIAS)

        img = ImageTk.PhotoImage(img) # imgが保持されないと表示されない
        width = img.width()
        height = img.height()
        geometry = str(width) + 'x' + str(height)

        dlg = tk.Toplevel(self.root)     # モーダルなウィンドウ
        dlg.title("Setting Dialog") # ウィンドウタイトル
        dlg.geometry(geometry)      # ウィンドウサイズ(幅x高さ)

        # モーダルにする設定
        dlg.grab_set()        # モーダルにする
        dlg.focus_set()       # フォーカスを新しいウィンドウをへ移す
        dlg.transient(self.root.master) # タスクバーに表示しない

        dlg.bind(e2s(EventType.Destroy), self.__on_canvas_destroyed)

        self.setting_canvas = tk.Canvas(dlg, width=width, height=height)
        self.setting_canvas.place(x=0, y=0)  # メインウィンドウ上に配置
        self.setting_canvas.bind(e2s(EventType.ButtonPress, 1), self.__on_left_clicked)
        self.setting_canvas.bind(e2s(EventType.Motion), self.__on_mouth_moved)
        self.setting_canvas.bind(e2s(EventType.ButtonRelease, 1), self.__on_left_released)

        self.setting_canvas.create_image(  # キャンバス上にイメージを配置
            0,  # x座標
            0,  # y座標
            image=img,  # 配置するイメージオブジェクトを指定
            tag="illust",  # タグで引数を追加する。
            anchor=tk.NW  # 配置の起点となる位置を左上隅に指定
        )

        return dlg, img


    #==================================================
    # イベント関数
    #==================================================
    def __on_setting_button_pressed(self, e):
        if self.file_name.get() != 'canceled':
            # 画像ファイルをキャンバスとして開く
            # クリック&ドラッグで選択範囲の枠を作成する
            dlg, _ = self.__create_setting_dialog()
            # ダイアログが閉じられるまで待つ
            self.root.wait_window(dlg)
        else:
            print('ファイルを選択してください')

    def __on_input_button_pressed(self, e):
        # 画像ファイルをセグメントに従って切り分ける
        pass

    def __on_output_button_pressed(self, e):
        # OCRしてCSV化する
        pass

    def __on_canvas_destroyed(self, e):
        print(self.item)

    def __on_left_clicked(self, e):
        self.drawing = True

    def __on_mouth_moved(self, e):
        if self.drawing:
            # クリック中、枠を描画する
            self.end_pos = (e.x, e.y)
            self.setting_canvas.delete('drawing') # 以前描画していた枠を削除
            self.setting_canvas.create_rectangle(self.start_pos[0], self.start_pos[1], self.end_pos[0], self.end_pos[1], tags='drawing') # 新しい枠を描画する
        else:
            # クリックしていない場合は開始地点を更新
            self.start_pos = (e.x, e.y)

    def __on_left_released(self, e):
        self.drawing = False
        # 指定した枠を追加する
        count = len(self.item.data)
        start = (min(self.start_pos[0], self.end_pos[0]), min(self.start_pos[1], self.end_pos[1])) # 左上の点
        end = (max(self.start_pos[0], self.end_pos[0]), max(self.start_pos[1], self.end_pos[1]))   # 右下の点
        self.item.append(item.Element(str(count), (start, end)))

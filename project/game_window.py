from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
import random
import sqlite3
from data_colours import COLOURS
from data import SaveData
# from load_words import load_words


class GameWindow(QWidget):
    def __init__(self, stacked_widget):
        self.stacked_widget = stacked_widget
        #load_words()
        self.words = {}
        self.cur_row = 0
        self.cur_word = ''
        self.word_info = ''
        self.word_category = ''
        self.bd = SaveData()
        self.closei = False
        self.hard_mode = 0
        super().__init__()
        self.init_ui()
        with open("words_alpha.txt", "r") as f:
            self.eng_words = set(i.strip().lower() for i in f)

    def load_words2(self):
        con = sqlite3.connect("words.db")
        cur = con.cursor()
        cur.execute("SELECT category, word, translation, sentence FROM words")
        data = cur.fetchall()
        words = {}
        for cat, word, trans, sent in data:
            if cat not in words:
                words[cat] = {}
            words[cat][word] = {"translation": trans, "sentence": sent}
        con.close()
        return words


    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        # !!! добавить спейсинг
        main_layout.setSpacing(10)
        main_layout.addStretch(1)
        self.cat_label = QLabel('')
        self.cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWindowTitle("Wordle")
        self.setStyleSheet("background-color:#white;")
        self.cat_label.setStyleSheet("font-size:18px;color:#555;")
        main_layout.addWidget(self.cat_label)
        try:
            pnt = self.bd.get_points()
        except:
            pnt = 0
        self.score = QLabel('Очки: ' + str(pnt))
        self.score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score.setStyleSheet("font-size:20px;color:#222;font-weight:bold;")
        main_layout.addWidget(self.score)
        main_layout.addSpacing(30)
        self.rows = []
        for i in range(5):
            row_lay = QHBoxLayout()
            boxes = []
            for j in range(5):
                box = QLineEdit()
                box.setFixedSize(60, 60)
                box.setAlignment(Qt.AlignmentFlag.AlignCenter)
                box.setMaxLength(1)
                box.setEnabled(False)
                box.setStyleSheet(
                    "font-size:24px;background-color:white;"
                    "border:2px solid #aaa;border-radius:10px;"
                )
                box.textChanged.connect(self.next_choose)
                boxes.append(box)
                row_lay.addWidget(box)
            self.rows.append(boxes)
            main_layout.addLayout(row_lay)
    #проверка
        main_layout.addSpacing(40)
        self.check = QPushButton('Проверить')
        self.check.setFixedSize(250, 70)
        self.check.setStyleSheet(
            "font-size:26px;font-weight:bold;background-color:#4CAF50;color:white;"
            "border-radius:12px;padding:10px 30px;"
        )
        self.check.clicked.connect(self.check_cur_word)
        main_layout.addWidget(self.check, alignment=Qt.AlignmentFlag.AlignCenter)
        self.info = QLabel('')
        self.info.setStyleSheet("font-size:18px;color:#333;font-weight:bold;")
        main_layout.addWidget(self.info)
        main_layout.addStretch(2)
        # !!! форматирование
        self.back_btn = QPushButton("Назад")
        self.back_btn.setFixedSize(200, 55)
        self.back_btn.setStyleSheet(
            "font-size:22px;font-weight:bold;background-color:#787c7e;color:white;"
            "border-radius:12px;padding:10px 20px;"
        )
        self.back_btn.clicked.connect(self.go_back)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.back_btn)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.genering_new_word()

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)

    def genering_new_word(self):
        self.hard_mode = self.bd.hard_mode()
        self.words = self.load_words2()
        categorys = list(self.words.keys())
        self.word_category = random.choice(categorys)
        try:
            done = self.bd.get_done()
        except:
            done = set()
        lft_words = [(i, j) for i, j in self.words[self.word_category].items() if i not in done]
        if not lft_words:
            try:
                self.bd.reset_words()
            except:
                pass
            lft_words = list(self.words[self.word_category].items())
        tmp = random.choice(lft_words)
        self.cur_word = tmp[0]
        self.word_info = tmp[1]
        self.cur_row = 0

        # очистка
        for row in self.rows:
            for box in row:
                box.setText('')
                box.setEnabled(False)
                box.setStyleSheet(
                    "font-size:24px;background-color:white;border:2px solid #aaa;border-radius:10px;"
                )

        for box in self.rows[0]:
            box.setEnabled(True)
        try:
            self.rows[0][0].setFocus()
        except:
            pass
        #подсказка
        self.cat_label.setText('Категория: ' + self.word_category)
        self.cat_label.setStyleSheet("font-size:24px;font-weight:bold;")
        self.info.setText("")
        try:
            self.check.clicked.disconnect()
        except:
            pass
        self.check.setText('Проверить')
        self.check.clicked.connect(self.check_cur_word)

    def next_choose(self):
        if self.closei:
            return
        box = self.sender()
        if box is None:
            return
        cur_txt = box.text().lower()
        if cur_txt == "":
            for r in self.rows:
                if box in r:
                    ind = r.index(box)
                    if ind > 0:
                        r[ind - 1].setFocus()
                    return

        if len(cur_txt) == 1:
            for r in self.rows:
                if box in r:
                    ind = r.index(box)
                    if ind < 4:
                        r[ind + 1].setFocus()
                    return


    def check_cur_word(self):
        guessed = [b.text().lower() for b in self.rows[self.cur_row]]
        if '' in guessed:
            self.info.setText('Введите все буквы')
            return
        guess = "".join(guessed)
        allLetters = True
        for i, ch in enumerate(guess):
            if not ("a" <= ch <= "z"):
                self.rows[self.cur_row][i].setStyleSheet(
                    "background-color:#FF4C4C;color:white;font-size:24px;border-radius:10px;"
                )
                allLetters = False
        if not allLetters:
            self.info.setText('Используйте только английские буквы')
            return
        # наличие атрибута
        if guess not in self.eng_words:
            self.info.setText('Такого слова не существует')
            for box in self.rows[self.cur_row]:
                box.setStyleSheet(
                    "background-color:#FF4C4C;color:white;font-size:24px;border-radius:10px;"
                )
            return
        try:
            hard = bool(self.bd.hard_mode())
        except:
            hard = False
        targ = self.cur_word
        n = len(targ)
        from collections import Counter
        targ_cnt = Counter(targ)
        result_colors = [None] * n
        for i in range(n):
            if guess[i] == targ[i]:
                result_colors[i] = COLOURS['green']
                targ_cnt[guess[i]] -= 1

        for i in range(n):
            if result_colors[i] is not None:
                continue
            ch = guess[i]
            if hard:
                result_colors[i] = COLOURS['gray']
            else:
                if targ_cnt.get(ch, 0) > 0:
                    result_colors[i] = COLOURS['yellow']
                    targ_cnt[ch] -= 1
                else:
                    result_colors[i] = COLOURS['gray']
        self.closei = True
        for i, color in enumerate(result_colors):
            self.rows[self.cur_row][i].setEnabled(False)
            self.rows[self.cur_row][i].setStyleSheet(
                f"background-color:{color};color:black;font-size:24px;border-radius:10px;"
            )
        # снижение очков
        self.closei = False
        if guess == targ:
            try1 = self.cur_row
            dif = [5, 4, 3, 2, 1][try1]
            try:
                self.bd.add_points(dif)
                self.bd.mark(self.cur_word)
                pnt = self.bd.get_points()
            except:
                pnt = 0
            self.score.setText("Очки: " + str(pnt))
            self.info.setText(
                f"Так держать! {self.cur_word} - {self.word_info['translation']}\nОчки: +{dif}\nПример: {self.word_info['sentence']}"
            )
            try:
                self.check.clicked.disconnect()
            except:
                pass
            self.check.setText("Далее")
            self.check.clicked.connect(self.genering_new_word)
            return
    #неудача
        self.cur_row += 1
        if self.cur_row >= 5:
            try:
                self.bd.add_points(-2)
                pnt = self.bd.get_points()
            except:
                pnt = 0
            self.score.setText("Очки: " + str(pnt))
            self.info.setText(
                f"Неверно. Словом было: {self.cur_word} - {self.word_info['translation']}\nОчки: -2\nПример: {self.word_info['sentence']}"
            )
            try:
                self.check.clicked.disconnect()
            except:
                pass
            self.check.setText('Далее')
            self.check.clicked.connect(self.genering_new_word)
            return
        for b in self.rows[self.cur_row]:
            b.setEnabled(True)
        try:
            self.rows[self.cur_row][0].setFocus()
        except:
            pass



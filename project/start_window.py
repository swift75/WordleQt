from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from data import SaveData
import sqlite3


class StartWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.bd = SaveData()
        self.cur_score = self.bd.get_points()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Wordle')
        self.setStyleSheet("background-color:#white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)
        self.logo = QLabel()
        pic = QPixmap('!!!ДОБАВИТЬ')
        self.logo.setPixmap(pic)
        # !!! отформатировать
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(self.logo)
        self.title = QLabel("Wordle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 54px;
            font-weight: 900;
            color: #333;
            letter-spacing: 2px;
        """)
        layout.addWidget(self.title)
        self.sub = QLabel('Угадайте английское слово начального уровня.\nУ вас есть 5 попыток.')
        self.sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub.setStyleSheet("""
            font-size: 25px;
            color: #666;
            margin-top: 10px;
            margin-bottom: 5px;
        """)
        layout.addWidget(self.sub)
        self.play = QPushButton('Играть')
        self.play.setFixedSize(300, 80)
        self.play.setStyleSheet("""
            QPushButton {
                font-size: 30px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        layout.addWidget(self.play, alignment=Qt.AlignmentFlag.AlignCenter)
        self.play.clicked.connect(self.start_game)
        self.points = QPushButton('Очки')
        self.points.setFixedSize(275, 80)
        self.points.setStyleSheet("""
            QPushButton {
                font-size: 26px;
                font-weight: bold;
                background-color: #2196F3;
                color: white;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #1e86d8;
            }
        """)
        layout.addWidget(self.points, alignment=Qt.AlignmentFlag.AlignCenter)
        self.points.clicked.connect(self.open_points)
        self.setLayout(layout)

    def start_game(self):
        self.stacked_widget.setCurrentIndex(1)

    def open_points(self):
        dialog = PointsWindow(self)
        dialog.exec()

    def update_score(self, sc):
        self.cur_score = sc


class PointsWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.bd = parent.bd
        self.cur_score = self.bd.get_points()
        self.setWindowTitle("Очки")
        self.setFixedSize(475, 500)
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout()
        # очки
        title = QLabel("Система очков")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('''
            font-size: 32px;
            font-weight: 900;
            color: #222;
            margin-top: 10px;
            letter-spacing: 1px;
        ''')
        # очки-подсказка
        layout.addWidget(title)
        des = QLabel(
            "     1 попытка      +5 очков\n"
            "   2 попытки      +4 очка\n"
            "   3 попытки      +3 очка\n"
            "   4 попытки      +2 очка\n"
            "   5 попыток      +1 очко\n"
            "  Ошибка          -2 очка\n"
            "  Усложнение - только верно угаданные буквы"
        )
        des.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #333;
                background-color: #f3f3f3;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        # счет
        des.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(des)
        self.setFixedSize(500, 600)
        self.score = QLabel(f"Ваши очки: {self.cur_score}")
        self.score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #444;
            margin-top: 10px;
        """)
        # !!! словарь добавить
        layout.addWidget(self.score)
        bonus = self.bd.is_unlocked()
        if bonus or self.cur_score >= 50:
            self.download = QPushButton("Скачать словарь")
            self.download.setFixedSize(310, 75)
            self.download.setStyleSheet("""
                QPushButton {
                    font-size: 24px;
                    background-color: #673AB7;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5c32a3;
                }
            """)
            self.download.clicked.connect(self.download_dict)
            layout.addWidget(self.download, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            locked = QLabel("Словарь: требуется 50 очков")
            locked.setAlignment(Qt.AlignmentFlag.AlignCenter)
            locked.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                padding: 14px;
                background-color: #f0f0f0;
                color: #999;
                border-radius: 18px;
                margin-top: 10px;
            """)
            layout.addWidget(locked)
        layout.addSpacing(10)
# !!! хард добавить
        if self.cur_score >= 75:
            self.hard_btn = QPushButton()
            self.hard_btn.setFixedSize(310, 75)
            self.update_hard_button_ui()
            self.hard_btn.clicked.connect(self.act_hard_mode)
            layout.addWidget(self.hard_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            locked2 = QLabel("Усложнение: требуется 75 очков")
            locked2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            locked2.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                padding: 14px;
                background-color: #f0f0f0;
                color: #999;
                border-radius: 18px;
                margin-top: 10px;
            """)
            layout.addWidget(locked2)
        self.setLayout(layout)


    def download_dict(self):
        i, j = QFileDialog.getSaveFileName(
            self, "Сохранить словарь", "wordle_dictionary.txt", "Text Files (*.txt)"
        )
        if not i:
            return
        con = sqlite3.connect("words.db")
        cur = con.cursor()
        cur.execute("SELECT category, word, translation, sentence FROM words")
        data = cur.fetchall()
        con.close()
        with open(i, "w", encoding="utf-8") as f:
            cur_cat = None
            for cat, word, tr, sent in data:
                if cat != cur_cat:
                    f.write(f"\n--- {cat} ---\n")
                    cur_cat = cat
                f.write(f"{word} – {tr}\nПример: {sent}\n\n")
        self.bd.unlock_bonus()
        self.close()

    def update_hard_button_ui(self):
        if self.bd.hard_mode():
            self.hard_btn.setText("Усложнение: Включено")
            self.hard_btn.setStyleSheet("""
                QPushButton {
                    font-size: 24px;
                    background-color: #e53935;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c62828;
                }
            """)
        else:
            self.hard_btn.setText("Усложнение: Выключено")
            self.hard_btn.setStyleSheet("""
                QPushButton {
                    font-size: 24px;
                    background-color: #9E9E9E;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #757575;
                }
            """)


    def act_hard_mode(self):
        current = self.bd.hard_mode()
        self.bd.Ishard_mode(not current)
        self.update_hard_button_ui()



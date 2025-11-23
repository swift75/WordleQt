from PyQt6.QtWidgets import QApplication, QStackedWidget
from start_window import StartWindow
from game_window import GameWindow
# временно from result_window import ResultWindow
import sys
# import nltk


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked = QStackedWidget()
    start = StartWindow(stacked)
    game = GameWindow(stacked)
    # временно result = ResultWindow(stacked)
    stacked.addWidget(start)
    stacked.addWidget(game)
    # временно stacked.addWidget(result)
    stacked.setCurrentIndex(0)
    stacked.resize(600, 700)
    stacked.show()
    sys.exit(app.exec())

# ---------------------------------------------------
# |                    CHESS                        |
# ---------------------------------------------------

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

WIDTH = 800
HEIGHT = 800


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.pawn_im = QPixmap("img/pawntest.png")
        self.pawn = QLabel()
        self.pawn.setPixmap(self.pawn_im)

        self.pawn2 = QLabel()
        self.pawn2.setPixmap(self.pawn_im)

        self.layout = QGridLayout()
        self.layout.addWidget(self.pawn)
        self.setLayout(self.layout)

        self.setGeometry(300, 200, WIDTH, HEIGHT)
        self.setWindowTitle("Chess")
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_board(qp)
        qp.end()

    def draw_board(self, qp):
        col1 = QColor(0, 0, 0)
        col1.setNamedColor("#61a055")  # green
        col2 = QColor(0, 0, 0)
        col2.setNamedColor("#ebf2d2")  # white

        qp.setPen(col1)
        qp.setBrush(QColor(col1))

        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:  # to make checkered pattern
                    qp.setPen(col1)
                    qp.setBrush(QColor(col1))
                else:
                    qp.setPen(col2)
                    qp.setBrush(QColor(col2))
                qp.drawRect(x * WIDTH // 8, y * WIDTH // 8, WIDTH // 8, WIDTH // 8)


def window():  # create window
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()

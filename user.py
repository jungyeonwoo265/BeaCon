import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("user.ui")[0]


class User(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.name = str

    def set_information(self, name):
        self.name = name
        print(self.name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = User()
    myWindow.show()
    app.exec_()

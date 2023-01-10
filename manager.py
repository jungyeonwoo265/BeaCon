import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pymysql as p
from datetime import datetime

form_class = uic.loadUiType("manager.ui")[0]


class Manager(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # DB 연결
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()
        self.conn.close()

        # self.변수 초기화 및 선언
        self.now = datetime.now()
        self.name = str

        # 시그널 - 메서드
        self.cb_menu.currentIndexChanged.connect(self.page_move)
        self.pb_home_page2.clicked.connect(self.go_home)
        self.pb_home_page3.clicked.connect(self.go_home)
        self.pb_home_page4.clicked.connect(self.go_home)
        # self.open_event()

    def page_move(self):
        page = self.cb_menu.currentText()
        self.cb_menu.setCurrentIndex(0)
        if page == '...':
            self.stackedWidget.setCurrentIndex(0)
        elif page == '전체 공지':
            self.stackedWidget.setCurrentIndex(1)
        elif page == '학생 일정':
            self.stackedWidget.setCurrentIndex(2)
        elif page == '메신저':
            self.stackedWidget.setCurrentIndex(3)

    def go_home(self):
        self.stackedWidget.setCurrentIndex(0)

    def set_information(self, name):
        self.name = name


    def open_db(self):
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()

    # def open_event(self):
    #     self.open_db()
    #     # self.c.execute(f'select * from calendar where training = curdate()')
    #     self.c.execute(f'select * from calendar where training = subdate(curdate(),1)')
    #     check = self.c.fetchone()
    #     print(check, 'manager')
    #     self.conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Manager()
    myWindow.show()
    app.exec_()

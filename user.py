import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pymysql as p
import datetime

form_class = uic.loadUiType("user.ui")[0]


class User(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # DB 연결
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()
        self.conn.close()

        # self.변수 초기화 및 선언
        self.time = 'curtime()'
        self.date = 'curdate()'
        self.name = str
        self.set_information('김연수')
        self.lb_notice.setText('')
        self.lb_state.setText('입실전')
        self.state = tuple
        self.reset()

        # 시그널 - 메서드
        self.cb_menu.currentIndexChanged.connect(self.page_move)
        self.pb_home_page2.clicked.connect(self.go_home)
        self.pb_home_page3.clicked.connect(self.go_home)
        self.pb_home_page4.clicked.connect(self.go_home)
        self.pb_home_page5.clicked.connect(self.go_home)
        self.pb_check.clicked.connect(self.check)
        self.pb_check.clicked.connect(self.push_chang)
        self.pb_outing.clicked.connect(self.outing)
        self.pb_outing.clicked.connect(self.push_chang)

    def reset(self):
        self.early()
        self.push_chang()
        self.time_set()

    def outing(self):
        self.open_db()
        if self.lb_comeback.text() != '':
            self.c.execute(f'update attendance set 복귀 = "" where 이름 = "{self.name}" and 날짜 = {self.date};')
        self.c.execute(f'update attendance set 외출 = {self.time} where 이름 = "{self.name}" and 날짜 = {self.date};')
        self.conn.commit()
        self.conn.close()

    def check(self):
        state = self.pb_check.text()
        self.open_db()
        if state == '입실':
            self.c.execute(f'update attendance set 입실 = {self.time} where 이름 = "{self.name}" and 날짜 = {self.date};')
        elif state == '복귀':
            self.c.execute(f'update attendance set 복귀 = {self.time} where 이름 = "{self.name}" and 날짜 = {self.date};')
        elif state == '퇴실':
            self.c.execute(f'update attendance set 퇴실 = {self.time} where 이름 = "{self.name}" and 날짜 = {self.date};')
        self.conn.commit()
        self.conn.close()

    def early(self):
        self.open_db()
        self.c.execute('select 내용 from notice where 상태 = "y";')
        self.lb_notice.setText(self.c.fetchone()[0])
        self.conn.close()

    def push_chang(self):
        self.open_db()
        self.c.execute(f'select 입실, 외출, 복귀, 퇴실 from attendance where 날짜 = {self.date} and 이름 = "{self.name}";')
        self.state = self.c.fetchone()
        if self.state == 'none':
            print('됬음')
            self.state = ([], [], [], [])
        self.lb_entrance.setText(self.state[0])
        self.lb_outing.setText(self.state[1])
        self.lb_comeback.setText(self.state[2])
        self.lb_leave.setText(self.state[3])
        if self.state[0] == '':
            self.lb_state.setText('입실전')
            self.pb_outing.hide()
        elif self.state[3] != '':
            self.lb_state.setText('퇴실')
            self.pb_outing.hide()
            self.pb_check.hide()
        elif self.state[1] != '' and self.state[2] == '':
            self.lb_state.setText('외출')
            self.pb_check.setText('복귀')
            self.pb_outing.hide()
        elif self.state[1] != '' and self.state[2] != '':
            self.lb_state.setText('입실')
            self.pb_check.setText('퇴실')
            self.pb_outing.show()
            self.conn.commit()
        elif self.state[0] != '':
            self.lb_state.setText('입실')
            self.pb_check.setText('퇴실')
            self.pb_outing.show()
        self.conn.close()

    def time_set(self):
        self.open_db()
        self.c.execute(f'select min(시간), max(시간) from schedule where 날짜 = {self.date};')
        date = self.c.fetchone()
        mindate = date[0]
        maxdate = date[1]
        self.c.execute(f'select {self.date};')
        today = self.c.fetchone()
        self.lb_training.setText(f'{today[0]} {mindate.split("~")[0]} ~ {maxdate.split("~")[1]}')
        self.conn.close()

    def page_move(self):
        page = self.cb_menu.currentText()
        self.cb_menu.setCurrentIndex(0)
        if page == '...':
            self.stackedWidget.setCurrentIndex(0)
        elif page == '나의 출결 및 진도 현황':
            self.stackedWidget.setCurrentIndex(1)
        elif page == '나의출석보기':
            self.stackedWidget.setCurrentIndex(2)
        elif page == '개인 일정':
            self.stackedWidget.setCurrentIndex(3)
        elif page == '메신저':
            self.stackedWidget.setCurrentIndex(4)

    def go_home(self):
        self.stackedWidget.setCurrentIndex(0)

    def set_information(self, name):
        self.name = name

    def open_db(self):
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = User()
    myWindow.show()
    app.exec_()

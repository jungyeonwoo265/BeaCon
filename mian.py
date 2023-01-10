import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtWidgets
import pymysql as p
from datetime import datetime, timedelta
from user import User
from manager import Manager

form_class = uic.loadUiType("main.ui")[0]


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # DB 연결
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()
        self.conn.close()

        # self.변수 선언 및 초기화
        self.lb_id.setText('')
        self.name = str
        self.login_state = False
        self.login_manager = False
        self.yesterday = datetime.now() - timedelta(1)

        # 시그널-메서드
        self.pb_loginpage.clicked.connect(self.go_login)
        self.pb_login_2.clicked.connect(self.login)
        self.pb_beacon.clicked.connect(self.program)
        # self.open_event()

    # def open_event(self):
    #     training = list()
    #     self.open_db()
    #     self.c.execute('select * from calendar where training = subdate(curdate(),1);')
    #     check = self.c.fetchone()
    #     for i in check:
    #         if i == self.yesterday.strftime("%Y-%m-%d"):
    #             training.append(i)
    #         elif i == '퇴실' or i == '출석':
    #             training.append('출석')
    #         else:
    #             training.append('결석')
    #     print(training)
    #     self.conn.close()

    def open_db(self):
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()

    def program(self):
        if self.login_manager and self.login_state:
            user_page.set_information(self.name)
            widget.setCurrentIndex(2)
        elif self.login_state:
            manager_page.set_information(self.name)
            widget.setCurrentIndex(1)
        else:
            QMessageBox.information(self, '안내창', '로그인 하세요')

    def go_login(self):
        if self.login_state:
            self.name = str
            self.lb_id.setText(f'')
            self.login_state = False
            self.login_manager = False
            self.pb_loginpage.setText('로그인')
        else:
            self.stackedWidget.setCurrentIndex(1)

    def go_home(self):
        self.stackedWidget.setCurrentIndex(0)

    def login(self):
        self.open_db()
        userid = self.le_id.text()
        password = self.le_pw.text()
        if userid and password:
            self.c.execute(f'select name from user where id ="{userid}" and password = {password}')
            check = self.c.fetchone()
            self.c.execute(f'select name from manager where id ="{userid}" and password = {password}')
            manager = self.c.fetchone()
            if check and not manager:
                self.le_id.clear()
                self.le_pw.clear()
                self.name = check[0]
                self.lb_id.setText(f'{self.name}님 안녕 하세요.')
                self.login_state = True
                self.pb_loginpage.setText('로그 아웃')
                self.go_home()
            elif manager and not check:
                self.le_id.clear()
                self.le_pw.clear()
                self.name = manager[0]
                self.lb_id.setText(f'{self.name}님 안녕 하세요.')
                self.login_state = True
                self.login_manager = True
                self.pb_loginpage.setText('로그 아웃')
                self.go_home()
            else:
                QMessageBox.information(self, '안내창', 'login 실패')
        elif userid:
            QMessageBox.information(self, '안내창', 'password 누락')
        elif password:
            QMessageBox.information(self, '안내창', 'id 누락')
        else:
            self.conn.close()
            return
        self.conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    main_page = WindowClass()
    user_page = User()
    manager_page = Manager()

    widget.addWidget(main_page)
    widget.addWidget(user_page)
    widget.addWidget(manager_page)

    # myWindow = WindowClass()
    # myWindow.show()
    widget.setFixedHeight(800)
    widget.setFixedWidth(800)
    widget.show()
    app.exec_()

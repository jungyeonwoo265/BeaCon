import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pymysql as p

form_class = uic.loadUiType("schedule.ui")[0]


class Schedule(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()
        self.c.execute(f'select 날짜, 시간, 과목 from schedule where 날짜 = curdate();')
        schedule = self.c.fetchall()
        if schedule:
            self.tableWidget.setRowCount(len(schedule))
            self.tableWidget.setColumnCount(len(schedule[0]))
            for i, le in enumerate(schedule):
                for j, v in enumerate(le):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(v))
        self.conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Schedule()
    myWindow.show()
    app.exec_()
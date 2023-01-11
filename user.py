import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pymysql as p

form_class = uic.loadUiType("user.ui")[0]


class User(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # DB 연결
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()
        self.conn.close()

        # page1 self.변수 초기화 및 선언
        self.check_class = False
        self.time = 'curtime()'
        self.date = 'curdate()'
        self.name = str
        self.state = tuple
        # main.py 연결시 주석 처리
        self.set_information('고연재')

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

    # 페이지3 이동시 초기화 및 이벤트 핸들러로 self.page3_month() 호출
    def reset_page3(self):
        self.open_db()
        # 출석일 구하기
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}" and 출석="y";')
        attendance = self.c.fetchone()[0]
        self.c.execute(f'select count(*) from (select 날짜 from schedule group by 날짜) as t;')
        total = self.c.fetchone()[0]
        self.lb_attendance_rate_page3.setText(f'{attendance}/{total}')
        # 나의 출석 정보 콤보 박스 년,월 셋팅
        self.cb_year_page3.clear()
        self.c.execute(f'select year(min(날짜)),year(max(날짜)) from attendance where 이름 = "{self.name}";')
        year = self.c.fetchone()
        for idx, y in enumerate(year):
            self.cb_year_page3.insertItem(idx, str(y))
        self.conn.close()
        self.page3_month()
        self.cb_year_page3.currentIndexChanged.connect(self.page3_month)
        # self.page3_calender()

    # page3 년도 콤보 박스 변경시 월 콤보 박스 셋팅
    def page3_month(self):
        self.cb_month_page3.clear()
        year = self.cb_year_page3.currentText()
        self.open_db()
        self.c.execute(f'select month(min(날짜)),month(max(날짜)) from attendance where 날짜 like "{year}%" and 이름 = "{self.name}";')
        month = self.c.fetchone()
        for i, m in enumerate(range(month[0], month[1]+1)):
            self.cb_month_page3.insertItem(i, str(m))
        self.conn.close()
        self.cb_year_page3.currentIndexChanged.connect(self.page3_calender)
        self.cb_month_page3.currentIndexChanged.connect(self.page3_calender)

    def page3_calender(self):
        year = self.cb_year_page3.currentText()
        month = self.cb_month_page3.currentText()
        self.calendar_page3.setCurrentPage(int(year), int(month))

    # 페이지2 이동시 초기화
    def reset_page2(self):
        self.open_db()
        # 출석, 지각, 조퇴, 외출, 결석 수 구하기
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}" and 출석="y";')
        attendance = self.c.fetchone()[0]
        self.lb_attendance_page2.setText(f'{attendance}')
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}" and "17:00:00"-입실 < 8;')
        self.lb_tardy_num.setText(str(self.c.fetchone()[0]))
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}" and 조퇴="y";')
        self.lb_leave_early_page2.setText(str(self.c.fetchone()[0]))
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}" and 외출!="";')
        self.lb_outing_page2.setText(str(self.c.fetchone()[0]))
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}" and 결석="y";')
        absent =self.c.fetchone()[0]
        self.lb_absent_page2.setText(f'{absent}')
        self.lb_total_absent_num.setText(f'{absent}')
        # 나의 출석률, 과정 진행률 구하기
        self.c.execute(f'select count(*) from (select 날짜 from schedule group by 날짜) as t;')
        total = self.c.fetchone()[0]
        self.c.execute(f'select count(*) from attendance where 이름 = "{self.name}";')
        num = self.c.fetchone()[0]
        self.lb_attendance_rate_page2.setText('%0.1f%%(%d/%d)'%((attendance/total*100), attendance, total))
        self.lb_progress.setText('%0.1f%%(%d/%d)'%((num/total*100), num, total))
        self.bar_attendance.setValue(int(attendance/total*100))
        self.bar_progress.setValue(int(num/total*100))
        self.conn.close()

    # 오늘 수업이 있는지 확인
    def check_schecule(self):
        self.open_db()
        self.c.execute(f'select count(*) from schedule where 날짜 = {self.date};')
        check = self.c.fetchone()
        self.check_class = check[0]
        self.conn.close()

    # 날짜를 기준 으로 수업이 있고 출석부 명단이 없는 경우 출석부 명단 추가
    def roster(self):
        if self.check_class:
            self.open_db()
            self.c.execute(f'select count(*) from attendance where 날짜 = {self.date};')
            today = self.c.fetchone()
            self.c.execute(f'select count(*) from user;')
            user = self.c.fetchone()
            self.c.execute(f'select name from user;')
            user_name = self.c.fetchall()
            if today < user:
                self.c.execute(f'delete from attendance where 날짜 ={self.date} and 퇴실 = "" and 결석 ="n";')
                for i in user_name:
                    self.c.execute(f"insert into attendance values "
                                   f"({self.date}, '{i[0]}', '', '', '', '', 'n','n','n')")
            self.conn.commit()
            self.conn.close()

    # 전날의 출결 결과를 DB에 저장
    def result(self):
        self.open_db()
        self.c.execute(f'select count(*) from attendance where 날짜 = subdate({self.date},1)')
        count = self.c.fetchone()
        if count[0]:
            self.c.execute(f'select name from user;')
            user_name = self.c.fetchall()
            for i in user_name:
                self.c.execute(f'select 퇴실, "16:00:00"-입실, "17:00:00"- 퇴실 '
                               f'from attendance where 날짜 = subdate({self.date},1) and 이름 = "{i[0]}";')
                data = self.c.fetchone()
                # 수업 4시간 이상, 일찍 퇴실한 경우
                if data[1] >= 4 and data[2] > 0:
                    self.c.execute(f'update attendance set 조퇴="y" where 날짜 = subdate({self.date},1) and 이름 = "{i[0]}";')
                # 정상 퇴실, 수업 4시간 이상
                elif data[0] >= '17:01:00' and data[1] >= 4:
                    self.c.execute(f'update attendance set 출석="y" where 날짜 = subdate({self.date},1) and 이름 = "{i[0]}";')
                # 나머진 결석 처리
                else:
                    self.c.execute(f'update attendance set 결석="y" where 날짜 = subdate({self.date},1) and 이름 = "{i[0]}";')
            self.conn.commit()
        self.conn.close()

    # page1 의 초기 셋팅
    def reset(self):
        self.lb_notice.setText('')
        self.lb_state.setText('입실전')
        self.check_schecule()
        self.roster()
        self.result()
        self.early()
        self.push_chang()
        self.time_set()

    # 외출 버튼 클릭시 DB에 시간 저장
    def outing(self):
        self.open_db()
        if self.lb_comeback.text() == '':
            self.c.execute(f'update attendance set 외출 = {self.time} where 이름 = "{self.name}" and 날짜 = {self.date};')
        self.conn.commit()
        self.conn.close()

    # 출석 체크버튼 클릭시 DB에 시간 저장
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

    # 전체 공지를 띄우는 기능
    def early(self):
        self.open_db()
        self.c.execute('select count(*) from notice where 상태 = "y";')
        count = self.c.fetchone()
        if count[0]:
            self.c.execute('select 내용 from notice where 상태 = "y";')
            self.lb_notice.setText(self.c.fetchone()[0])
        else:
            self.lb_notice.setText('')
        self.conn.close()

    # 출석 체크를 위해 시간및 버튼의 텍스트 변경
    def push_chang(self):
        if self.check_class:
            self.open_db()
            self.c.execute(f'select 입실, 외출, 복귀, 퇴실 from attendance where 날짜 = {self.date} and 이름 = "{self.name}";')
            self.state = self.c.fetchone()
            self.lb_entrance.setText(self.state[0])
            self.lb_outing.setText(self.state[1])
            self.lb_comeback.setText(self.state[2])
            self.lb_leave.setText(self.state[3])
            # 입실 체크 전인 경우
            if self.state[0] == '':
                self.lb_state.setText('입실전')
                self.pb_outing.hide()
                self.pb_check.show()
            # 퇴실한 경우
            elif self.state[3] != '':
                self.lb_state.setText('퇴실')
                self.pb_outing.hide()
                self.pb_check.hide()
            # 외출 중인 경우
            elif self.state[1] != '' and self.state[2] == '':
                self.lb_state.setText('외출')
                self.pb_check.setText('복귀')
                self.pb_outing.hide()
            # 외출후 복귀 한 경우
            elif self.state[1] != '' and self.state[2] != '':
                self.lb_state.setText('입실')
                self.pb_check.setText('퇴실')
                self.pb_outing.hide()
                self.conn.commit()
            # 입실한 경우
            elif self.state[0] != '':
                self.lb_state.setText('입실')
                self.pb_check.setText('퇴실')
                self.pb_outing.show()
            self.conn.close()
        else:
            self.lb_state.setText('수업 없음')
            self.pb_outing.hide()
            self.pb_check.show()
            self.lb_entrance.setText('')
            self.lb_outing.setText('')
            self.lb_comeback.setText('')
            self.lb_leave.setText('')

    # 금일 수업 시간 라벨에 넣기
    def time_set(self):
        if self.check_class:
            self.open_db()
            self.c.execute(f'select min(시간), max(시간) from schedule where 날짜 = {self.date};')
            date = self.c.fetchone()
            mindate = date[0]
            maxdate = date[1]
            self.c.execute(f'select {self.date};')
            today = self.c.fetchone()
            self.lb_training.setText(f'{today[0]} {mindate.split("~")[0]} ~ {maxdate.split("~")[1]}')
            self.conn.close()
        else:
            self.lb_training.setText(f'')

    # 홈 에서 다른 스텍 으로 이동 하기
    def page_move(self):
        page = self.cb_menu.currentText()
        self.cb_menu.setCurrentIndex(0)
        if page == '...':
            self.stackedWidget.setCurrentIndex(0)
        elif page == '나의 출결 및 진도 현황':
            self.reset_page2()
            self.stackedWidget.setCurrentIndex(1)
        elif page == '나의출석보기':
            self.reset_page3()
            self.stackedWidget.setCurrentIndex(2)
        elif page == '개인 일정':
            self.stackedWidget.setCurrentIndex(3)
        elif page == '메신저':
            self.stackedWidget.setCurrentIndex(4)

    # 홈 이외의 창에서 홈 버튼을 누르면 홈 으로 이동
    def go_home(self):
        self.stackedWidget.setCurrentIndex(0)

    # mani.py 에서 사용자 이름 가져 오기
    def set_information(self, name):
        self.name = name

    # DB 연결 하기
    def open_db(self):
        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='0000', db='step6', charset='utf8')
        self.c = self.conn.cursor()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = User()
    myWindow.show()
    app.exec_()

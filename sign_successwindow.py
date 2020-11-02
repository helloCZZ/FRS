import sqlite3
import time
#import xlwt
import xlwt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox

from sign_success import Ui_Dialog


class sign_sussesswindow(Ui_Dialog,QDialog):
    def __init__(self,group,parent=None):
        super(sign_sussesswindow,self).__init__(parent)
        self.setupUi(self)
        self.group = group
        # 设置窗口内容不能被修改
        self.tableWidget.setEditTriggers((QAbstractItemView.NoEditTriggers))
        #显示签到学生
        self.search_tosqlite3()
        #显示未签到学生
        self.search_tosqlite3_2()
        # 显示打卡签到成功的学生信息,从sqlite3中进行查找操作！！！
        #self.pushButton_3.clicked.connect(self.del_data)

    #显示已经签到的学生信息
    def search_tosqlite3(self):
        # 关于两个按钮的功能，都是关闭，但是关闭之前完成什么工作
        self.pushButton.clicked.connect(self.save_data)
        self.pushButton_2.clicked.connect(self.close_window)
        # 导出数据

        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        print("Opened database successfully")
        self.table = self.group+'_student_sign'
        self.table_2 = self.group+'_student'
        try:
            cursor = c.execute("SELECT *  FROM '"+self.table+"'")
        except Exception as e:
            print("Unexpected error:", e)
            return
        print("查询成功")
        for row in cursor:
            id = str(row[0])
            user = row[1]
            date_time = row[2]
            #insertRow()添加第几行的数据，可以通过for循环的执行次数来判断
            rowcount = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowcount)
            # 插入数据
            self.tableWidget.setItem(rowcount, 0, QTableWidgetItem(id))
            self.tableWidget.setItem(rowcount, 1, QTableWidgetItem(user))
            self.tableWidget.setItem(rowcount, 2, QTableWidgetItem(self.group))
            self.tableWidget.setItem(rowcount, 3, QTableWidgetItem(date_time))



    #显示未签到的学生信息
    def search_tosqlite3_2(self):
        try:
            conn = sqlite3.connect('my.db')
            c = conn.cursor()
            cursor=c.execute("select * from '"+self.table_2+"' where id not in(select id from '"+self.table+"')")
        except Exception as e:
            print("Unexpected error:", e)
            return
        for row in cursor:
            id = str(row[0])
            user = row[1]
            department = row[2]
            #insertRow()添加第几行的数据，可以通过for循环的执行次数来判断
            rowcount = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(rowcount)
            # 插入数据
            self.tableWidget_2.setItem(rowcount, 0, QTableWidgetItem(id))
            self.tableWidget_2.setItem(rowcount, 1, QTableWidgetItem(user))
            self.tableWidget_2.setItem(rowcount, 2, QTableWidgetItem(department))


    def save_data(self):
        # 打开对话框，获取要导出的数据的文件名和格式
        filename, rel = QFileDialog.getSaveFileName(self, "导出数据", ".", "EXCEL(*.xls)")
        if filename:
            conn = sqlite3.connect('my.db')
            c = conn.cursor()
            cursor = c.execute("select * from '" + self.table_2 + "' where id not in(select id from '" + self.table + "')")
            print("查询成功")
            workbook = xlwt.Workbook()  # 新建一个工作簿
            sheet = workbook.add_sheet("data")  # 在工作簿中新建一个表格
            print("Ok1")
            # rowcount = cursor.rowcount
            i = 2
            str = self.group+'未签到人员名单'
            print(str)
            sheet.write(0,0,str)
            sheet.write(1, 0, "卡号")
            sheet.write(1, 1, "姓名")
            sheet.write(1, 2, "班级")
            for row in cursor:
                for line in range(3):
                    sheet.write(i, line, row[line])
                i = i + 1
            #print(filename)
            workbook.save(filename)  # 保存工作簿
            self.accept()
        else:
            return
        # 取消按钮
    def close_window(self):
        self.reject()

    #删除签到成功的全部数据
    def del_data(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        if c.execute("delete from '"+self.table+"'"):
            QMessageBox.about(self, "签到信息表删除", "删除成功")
            print("删除成功")
            conn.commit()
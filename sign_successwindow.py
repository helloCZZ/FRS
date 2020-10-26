import sqlite3
import time
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
        self.pushButton_3.clicked.connect(self.del_data)

    #显示已经签到的学生信息
    def search_tosqlite3(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        print("Opened database successfully")
        self.table = self.group+'_student_sign'
        self.table_2 = self.group+'_student'
        cursor = c.execute("SELECT *  FROM '"+self.table+"'")
        print("查询成功")
        for row in cursor:
            id = str(row[0])
            user = row[1]
            department = row[2]
            date_time = row[3]
            #insertRow()添加第几行的数据，可以通过for循环的执行次数来判断
            rowcount = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowcount)
            # 插入数据
            self.tableWidget.setItem(rowcount, 0, QTableWidgetItem(id))
            self.tableWidget.setItem(rowcount, 1, QTableWidgetItem(user))
            self.tableWidget.setItem(rowcount, 2, QTableWidgetItem(department))
            self.tableWidget.setItem(rowcount, 3, QTableWidgetItem(date_time))

        # 关于两个按钮的功能，都是关闭，但是关闭之前完成什么工作
        self.pushButton.clicked.connect(self.save_data)
        self.pushButton_2.clicked.connect(self.close_window)
        # 导出数据

    #显示未签到的学生信息
    def search_tosqlite3_2(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        cursor=c.execute("select * from '"+self.table_2+"' where id not in(select id from '"+self.table+"')")
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
        # 打开对话框，获取要导出的数据的文件名
        filename, rel = QFileDialog.getSaveFileName(self, "导出数据", ".", "EXCEL(*.excel)")
        self.accept()
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
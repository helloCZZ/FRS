import sqlite3
import time
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox

from sign_success import Ui_Dialog


class sign_sussesswindow(Ui_Dialog,QDialog):
    def __init__(self,parent=None):
        super(sign_sussesswindow,self).__init__(parent)
        self.setupUi(self)
        # 设置窗口内容不能被修改
        self.tableWidget.setEditTriggers((QAbstractItemView.NoEditTriggers))
        self.search_tosqlite3()
        # 显示打卡签到成功的学生信息,从sqlite3中进行查找操作！！！
        self.pushButton_3.clicked.connect(self.del_data)

    def search_tosqlite3(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        print("Opened database successfully")
        # 查询操作
        #c.execute("INSERT INTO STUDENT_2(ID,NAME,DEPARTMENT,DATE) VALUES (1,'f','s','2020-10-8')")
        print("添加成功")
        cursor = c.execute("SELECT ID,NAME,DEPARTMENT,DATE FROM STUDENT_2")
        print("查询成功")
        for row in cursor:
            print("ok1")
            print("ID = ", row[0])
            print("NAME = ", row[1])
            print("ADDRESS = ", row[2])
            print("DATETIME = ", row[3])
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
        if c.execute("delete from student_2"):
            QMessageBox.about(self, "签到信息表删除", "删除成功")
            print("删除成功")
            conn.commit()
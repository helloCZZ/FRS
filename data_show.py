import sqlite3
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView, QFileDialog
from sign_indata import Ui_Dialog


class sign_data(Ui_Dialog,QDialog):
    def __init__(self,signdata,parent=None):
        super(sign_data,self).__init__(parent)
        self.setupUi(self)
        #设置窗口内容不能被修改
        self.tableWidget.setEditTriggers((QAbstractItemView.NoEditTriggers))
        #将接受到的数据进行展开，键值对，键为了区别不同对象，值在这里才有用
        for i in signdata.values():
            #将usr_info中的信息进行分割,通过反斜杠分割，因为之前存储了两个反斜杠
            info = i['user_info'].split('\n\n')
            #得到姓名和部门的两个列表，利用列表的输出方法进行输出

            #insertRow()添加第几行的数据，可以通过for循环的执行次数来判断
            rowcount = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowcount)

            # 插入数据
            self.tableWidget.setItem(rowcount, 0, QTableWidgetItem(i['user_id']))
            self.tableWidget.setItem(rowcount, 1, QTableWidgetItem(info[0][3:]))
            #self.tableWidget.setItem(rowcount, 2, QTableWidgetItem(info[1][3:]))
            self.tableWidget.setItem(rowcount, 3, QTableWidgetItem(i['datetime']))

        #关于两个按钮的功能，都是关闭，但是关闭之前完成什么工作

        self.pushButton_2.clicked.connect(self.close_window)

    #导出数据
    def save_data(self):
        #打开对话框，获取要导出的数据的文件名
        filename,rel = QFileDialog.getSaveFileName(self,"导出数据",".","EXCEL(*.excel)")
        self.accept()

    #取消按钮
    def close_window(self):
        self.reject()

    # #将签到成功的数据写入sqlite3中
    # def save_tosqlite3(self,id,name,department,datetime):
    #     self.id = id
    #     self.name = name
    #     self.department = department
    #     self.datetime = str(datetime)
    #     print(self.datetime)
    #     conn = sqlite3.connect('my.db')
    #     c = conn.cursor()
    #     #c.execute('CREATE TABLE STUDENT_2(ID INT PRIMARY KEY NOT NULL,NAME TEXT NOT NULL,DEPARTMENT TEXT NOT NULL,DATE TXET NOT NULL)')
    #     c.execute("INSERT INTO STUDENT_2(ID,NAME,DEPARTMENT,DATE) VALUES (?,?,?,?)",(self.id,self.name,self.department,self.datetime))
    #     conn.commit()
    #     print("test3")

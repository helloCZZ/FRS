#从user窗口中导入Ui_Dialog这个类
import base64
import sqlite3

import cv2
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5 import QtGui
from adduser import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QComboBox, QVBoxLayout, QFileDialog, QCompleter
from cameravideo import camera
import pandas as pd

#新创建一个类,继承adduserwindow窗口中的Ui_Dialog这个类
#from test5 import items_list
#from PyQt5 import QtCore

class adduserwindow(Ui_Dialog,QDialog):
    def __init__(self,list,parent=None):
        super(adduserwindow,self).__init__(parent)
        self.setupUi(self)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle('添加学生')
        # 把组信息显示在列表框中
        self.show_list(list)
        # 选择照片按钮
        self.pushButton.clicked.connect(self.get_cameradata)
        #确定按钮
        self.pushButton_2.clicked.connect(self.get_data_close)
        #取消按钮
        self.pushButton_3.clicked.connect(self.close_window)
        #导入数据按钮
        self.pushButton_4.clicked.connect(self.import_data)
        #导入图片按钮
        self.pushButton_5.clicked.connect(self.get_picture)
        #调用显示数据的函数（从数据库中获取得到）
        self.show_data()
        # 选择启动摄像头按钮
        self.pushButton_6.clicked.connect(self.open_camera)


    #启动摄像头
    def open_camera(self):
        # 创建摄像头对象，不能少
        self.cameravideo = camera()
        # 让摄像头自适应
        self.label.setScaledContents(True)
        # 用到定时器 0ms启动一次
        self.time = QTimer()
        self.time.timeout.connect(self.show_cameradata)
        self.time.start(50)


    #将摄像头的画面显示到界面中
    def show_cameradata(self):
        # 获取摄像头数据，转换数据
        pic = self.cameravideo.camera_to_pic()  # 将摄像头获取到的数据转换成界面能显示的数据，返回值为qpmaxip
        # 显示数据，显示画面
        self.label.setPixmap(pic)  # 将获取到的数据拿到界面中进行显示

    #得到当前摄像头画面并关闭摄像头
    def get_cameradata(self):
        #camera_data得到图片
        camera_data = self.cameravideo.read_camera()
        # 把摄像头画面转换成图片，然后设置为base64编码
        _, enc = cv2.imencode('.jpg', camera_data)  # 返回两个元组
        #转换格式后保存到base64_image变量中
        self.base64_image = base64.b64encode(enc.tobytes())
        # 关闭定时器
        self.time.stop()
        #将摄像头关闭的操作
        self.cameravideo.close_camera()

    #通过打开文件来选择照片
    def get_picture(self):
        # 首先得到图片的路径,path
        img_path, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        #以只读的方式打开图片
        f = open(img_path,'rb')
        #将图片显示到界面上
        jpg = QtGui.QPixmap(img_path).scaled(self.label_5.width(), self.label_5.height())
        self.label_5.setPixmap(jpg)
        #将图片转换为base64格式
        self.base64_image = base64.b64encode(f.read()).decode()

    # 把组信息显示在列表框中
    def show_list(self,list):
        for l in list:
             self.listWidget.addItem(l)
        self.listWidget.setCurrentRow(0)
    #确定按钮功能
    def get_data_close(self):

        #选择的哪个用户组,注意currentItem()有括号！！！
        self.group_id = self.listWidget.currentItem().text()
        self.user_id = self.lineEdit.text()
        self.msg_name = self.lineEdit_2.text()
        self.msg_department = self.lineEdit_3.text()
        #点确定后应该关闭对话框
        self.accept()


    #取消按钮功能
    def close_window(self):
        #取消调用reject()函数，直接关闭对话框
        # 关闭定时器
        self.time.stop()
        # 将摄像头关闭的操作
        self.cameravideo.close_camera()
        self.reject()


    def import_data(self):
        # 打开对话框，获取要导出的数据的文件名
        # 获取excel表中的数据
        # "./test.xls"也行
        filename, rel = QFileDialog.getOpenFileName(self, "导入数据", ".", "EXCEL(*.*)")
        print(filename)
        path = filename
        data = pd.read_excel(path, None)

        print(data.keys())
        for sh_name in data.keys():
            print('sheet_name的名字是：', sh_name)
            sh_data = pd.DataFrame(pd.read_excel(path, sh_name))
            print(type(sh_data))
            #将pand.DataFrame类型转换为字典类型
            #id_name = sh_data.to_dict()
            self.id_name = sh_data.set_index('姓名').T.to_dict(orient='records')
            #print(self.id_name)

            # 将导入的数据存入到数据库my.db的student中
            conn = sqlite3.connect('my.db')
            # 创建游标方便执行命令
            c = conn.cursor()
            #c.execute('CREATE TABLE STUDENT_1(ID int PRIMARY KEY NOT NULL,NAME TEXT NOT NULL)')
            #print("ok1")
            #将值取出来并放入表中
            for i in self.id_name[0].items():
                print(i[0])
                print(i[1])
                c.execute("INSERT INTO STUDENT_1(ID,NAME) VALUES (?,?)",(i[1], i[0]))
                conn.commit()
            print("导入数据到数据库成功！")

    #写一个函数从数据库中获取信息并显示到表单中
    def show_data(self):
            #从数据库中取出数据
            conn = sqlite3.connect('my.db')
            c = conn.cursor()
            cursor = c.execute('select name from student_1')
            data = []
            for l in cursor:
                #print(l[0])
                #添加数据到列表中
                data.append(l[0])
                self.comboBox.addItem(l[0])
            self.comboBox.setCurrentIndex(-1)
            # 增加自动补全
            self.completer = QCompleter(data)
            self.completer.setFilterMode(Qt.MatchContains)
            self.completer.setCompletionMode(QCompleter.PopupCompletion)
            self.comboBox.setCompleter(self.completer)
            self.comboBox.currentIndexChanged.connect(self.selchange)


    #函数用来将鼠标选中的信息显示到文本框中
    def selchange(self):
        name = self.comboBox.currentText()
        self.lineEdit_2.setText(name)
        #根据姓名来查找学号
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        #从数据库中查找
        cursor = c.execute("select id from student_1 where name = '"+name+"'")
        for l in cursor:
            id = str(l[0])
        self.lineEdit.setText(id)
        #默认部门是信息科学与工程学院
        self.lineEdit_3.setText("信息科学与工程学院")

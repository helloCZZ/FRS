#从user窗口中导入Ui_Dialog这个类
import base64
import sqlite3

import cv2
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5 import QtGui
from adduser import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QComboBox, QVBoxLayout, QFileDialog, QCompleter, QInputDialog, QLineEdit, \
    QApplication, QMessageBox, QGroupBox
from cameravideo import camera
import pandas as pd
class adduserwindow(Ui_Dialog,QDialog):
    def __init__(self,group,parent=None):
        super(adduserwindow,self).__init__(parent)
        self.setupUi(self)
        # 定义一个布尔变量，用来互斥抓拍照片和打开摄像头
        self.status = True
        self.group = group
        #抓拍按钮变成灰色
        self.pushButton.setEnabled(False)
        # 选择启动摄像头按钮
        self.pushButton_6.clicked.connect(self.open_camera)
        # 抓拍照片按钮
        self.pushButton.clicked.connect(self.get_cameradata)
        # 导入图片按钮
        self.pushButton_5.clicked.connect(self.get_picture)
        #确定按钮
        self.pushButton_2.clicked.connect(self.get_data_close)
        #取消按钮
        self.pushButton_3.clicked.connect(self.close_window)
        self.groupBox.setStyleSheet('QGroupBox{border:2px,clolor:green}')

    #启动摄像头
    def open_camera(self):
        # 创建摄像头对象，不能少
        self.cameravideo = camera()
        # 让摄像头自适应
        self.label.setScaledContents(True)
        #用到定时器 0ms启动一次
        self.time = QTimer()
        self.time.timeout.connect(self.show_cameradata)
        self.time.start(50)
        #让按钮变成灰色
        #self.pushButton_6.setEnabled(False)
        #让抓拍按钮恢复使用
        self.pushButton.setEnabled(True)
        self.pushButton_6.setEnabled(False)
        self.status = True
    #将摄像头的画面显示到界面中
    def show_cameradata(self):
        # 获取摄像头数据，转换数据
        pic = self.cameravideo.camera_to_pic()  # 将摄像头获取到的数据转换成界面能显示的数据，返回值为qpmaxip
        # 显示数据，显示画面
        self.label.setPixmap(pic)  # 将获取到的数据拿到界面中进行显示

    #抓拍人脸，关闭摄像头
    def get_cameradata(self):
        if self.status:
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
            self.pushButton.setEnabled(False)
            self.pushButton_6.setEnabled(True)
            QMessageBox.about(self,"温馨提示","人脸抓拍成功，请填写下面的编号和姓名\n")
            self.status=False
        else:
            QMessageBox.about(self, "温馨提示", "您已选择从照片中添加人脸")
            return

    #通过打开文件来选择照片
    def get_picture(self):
        if self.status:
            # 首先得到图片的路径,path
            img_path, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
            #以只读的方式打开图片
            if img_path:
                f = open(img_path,'rb')
                #将图片显示到界面上
                jpg = QtGui.QPixmap(img_path).scaled(self.label_5.width(), self.label_5.height())
                self.label_5.setPixmap(jpg)
                #将图片转换为base64格式
                self.base64_image = base64.b64encode(f.read()).decode()
                QMessageBox.about(self, "温馨提示", "人脸选择成功，请填写下面的编号和姓名\n")
                self.pushButton_6.setEnabled(False)
                self.status =False
            else:
                return
        else:
            QMessageBox.about(self, "信息提示", "您已选择从摄像头获取人脸")
            return
    #确定按钮功能
    def get_data_close(self):
        #如果status为真，说明用户至少选择了一项进行添加人脸
        if self.status==False:
            if self.lineEdit.text() and self.lineEdit_2.text():
                #选择的哪个用户组,注意currentItem()有括号！！！
                self.group_id = self.group
                self.user_id = self.lineEdit.text()
                self.msg_name = self.lineEdit_2.text()

                #如果是自己手动添加信息，也需要写入数据库
                conn = sqlite3.connect('my.db')
                c = conn.cursor()
                table = self.group+'_student'
                cursor = c.execute("select * from '"+table+"'where id = '"+self.user_id+"'")
                print("ok1")
                if len(list(cursor)):
                    QMessageBox.about(self, "温馨提示", "编号已经存在，请重新输入！\n")
                    return
                else:
                    c.execute("INSERT INTO '" + table + "'(ID,NAME,CLASS) VALUES (?,?,?)", (self.user_id,self.msg_name,self.group))
                    conn.commit()
            else:
                QMessageBox.about(self,"温馨提示","姓名或编号还没有输入")
                return
        else:
            QMessageBox.about(self,"温馨提示","还未选择人脸")
            return
        self.accept()

    #取消按钮功能
    def close_window(self):
        self.reject()

    #设置按钮为灰色
    def btnsetdisabled(self, btn):
        if btn.isEnabled():
            btn.setEnabled(False)
        else:
            btn.setEnabled(True)

import cv2#opencv的一个关于摄像头的库
import numpy as np #as np 简写成np
from PyQt5.QtGui import  QPixmap,QImage
'''
摄像头操作：创建类对象完成摄像头操作，所以可以把打开摄像头与创建类对象操作合并
    __init__
    open()函数完成摄像头的配置打开

'''
class camera():
    def __init__(self):#创建并打开摄像头
        #类VideoCapture对视频或调用摄像头进行读取操作
        #参数 filename（视频的存储位置）;device(摄像头设备号，0表示电脑自带的摄像头)
        #0表示默认的摄像头，进行打开,创建视频/摄像头操作类对象：capture
        #创建摄像头操作对象，打开摄像头
        #self. capture表示打开的摄像头对象
        self. capture= cv2.VideoCapture(0)
        #isOpened()函数返回一个布尔值，来判断摄像头是否初始化成功
        if self.capture.isOpened():
            print("isOpened")
        #定义一个多维数组，用来存储获取的画面数据
        self.currentframe = np.array([])

    #读取摄像头的数据，返回获取到的数据data
    def read_camera(self):
        ret,data = self.capture.read()#ret是否成功，data是数据
        if not ret:
            print("获取摄像头数据失败!!!")
            return None
        return data

    #将获取到的摄像头数据转换成界面能显示的数据格式
    #pic保存的是摄像头获取到的数据
    def camera_to_pic(self):
        pic = self.read_camera()
        #镜像显示
        pic = cv2.flip(pic, 1)
        #摄像头是以BGR方式存储，首先需要转换为RGB(将pic转换成RGB存储方式)
        #调用cvtColor完成后才是RGB格式格式的画面数据
        self.currentframe = cv2.cvtColor(pic,cv2.COLOR_BGR2RGB)
        #设置宽和高
        #self.currentframe = cv2.cvtColor(self.currentframe,(640,480))
        #转换格式（界面能够显示的格式）lable显示Qpixmap
        #获取画面的宽度和高度
        height,width = self.currentframe.shape[:2]
        #先转换成QImage类型的图片（画面），创建QImage对象，使用摄像头的画面数据进行创建
        #QImage(data,width,height,format)创建：数据，宽度，高度，格式
        qimg = QImage(self.currentframe,width,height,QImage.Format_RGB888)
        #由于上面的形式不适合图像显示，故还需要转换格式
        qpixmap =  QPixmap.fromImage(qimg)
        return qpixmap

    #退出签到（关闭摄像头）
    def close_camera(self):
        self.capture.release()
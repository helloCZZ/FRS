'''
#QThread就是Pyqt5提供的线程类
#由于是一个已经完成了的类，功能已经写好，线程类的功能需要自己完成
#需要自己完成需要的线程类，创建一个新的线程类（功能自己定义），继承QThread
#新写的类具有线程的功能
'''
import base64
import cgitb
import datetime
import os

import cv2
from PyQt5.QtCore import QThread, QSettings


#线程进行执行，只会执行线程类中的run函数，如果有新的功能需要实现，需要重新写一个run函数完成
class recordVideo(QThread):#新的线程类，并继承QThread
    cgitb.enable(format='text')
    #ok(布尔值)用于判断退出while循环
    ok = True
    userID = ""
    emotion = ""
    def __init__(self,capture):#进行初始化,需要传递一个token(访问令牌)参数

        super(recordVideo, self).__init__()#初始化父类 后面括号不需要self
        #cam = cv2.VideoCapture(0)
        self.recordCapture = capture
        #user_ID = userID
        self.fps = 25
        # wid = int(self.recordCapture.get(3))
        # hei = int(self.recordCapture.get(4))
        # self.size = (wid, hei)
        self.size = (0, 0)
        #用来切换路径
        self.reMakePath = True
        self.fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.out = cv2.VideoWriter()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        #录制视频最长时间，达到后就重新生成一个文件
        self.timeToCreateNewVideo = QSettings('config.ini', QSettings.IniFormat).value("timeToCreateNewVideo", 5000,
                                                                                       int)
        #已记录的帧数
        self.num = 0


    def run(self):
        #启动系统时一直录像

        while 1:
            while self.ok:
                if self.reMakePath:
                    # 保存的文件名称
                    # 判断是否存在文件夹
                    folder = os.path.exists("video/" + self.userID + "_recordVideo")
                    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
                        os.makedirs("video/" + self.userID + "_recordVideo")  # makedirs 创建文件时如果路径不存在会创建这个路径
                    path = "video/" + self.userID + "_recordVideo/" + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".avi"
                    self.out.open(path,self.fourcc, self.fps, self.size)
                    self.reMakePath = False
                ret, frame = self.recordCapture.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    cv2.putText(frame,self.emotion,(400,50),self.font, 1.5, ( 0, 0,255), 2)
                    self.out.write(frame)
                    self.num += 1
                    if self.num > self.timeToCreateNewVideo:
                        self.reMakePath = True
                        self.num = 0
                    cv2.waitKey(30)


        # if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        #     os.makedirs("video/" + self.userID + "_recordVideo")  # makedirs 创建文件时如果路径不存在会创建这个路径
        # path = "video/" + self.userID + "_recordVideo/" + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')+".avi"
        # self.out.open(path,
        #          self.fourcc, self.fps, self.size)
        # while self.ok:
        #     ret, frame = self.recordCapture.read()
        #     if ret:
        #         frame = cv2.flip(frame, 1)
        #         self.out.write(frame)
        #         cv2.waitKey(30)

    def stop(self):
        self.ok = False
        cv2.waitKey(30)
        #self.wait()
        self.out.release()
        print("record线程已停止")


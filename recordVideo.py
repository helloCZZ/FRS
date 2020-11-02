'''
#QThread就是Pyqt5提供的线程类
#由于是一个已经完成了的类，功能已经写好，线程类的功能需要自己完成
#需要自己完成需要的线程类，创建一个新的线程类（功能自己定义），继承QThread
#新写的类具有线程的功能
'''
import base64
import datetime

import cv2
from PyQt5.QtCore import QThread

#线程进行执行，只会执行线程类中的run函数，如果有新的功能需要实现，需要重新写一个run函数完成
class recordVideo(QThread):#新的线程类，并继承QThread

    #ok(布尔值)用于判断退出while循环
    ok = True
    userID = ""
    def __init__(self,capture):#进行初始化,需要传递一个token(访问令牌)参数
        super(recordVideo, self).__init__()#初始化父类 后面括号不需要self
        #cam = cv2.VideoCapture(0)
        self.recordCapture = capture
        #user_ID = userID
        self.fps = 20
        wid = int(self.recordCapture.get(3))
        hei = int(self.recordCapture.get(4))
        self.size = (wid, hei)
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.out = cv2.VideoWriter()



    def run(self):
        #启动系统时一直录像
        # 保存的文件名称
        path = "video/" + self.userID + "/" + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')+".mp4"
        self.out.open(path,
                 self.fourcc, self.fps, self.size)
        while self.ok:
            ret, frame = self.recordCapture.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.out.write(frame)
                cv2.waitKey(30)

    def stop(self):
        self.ok = False
        cv2.waitKey(30)
        self.out.release()
        print("record线程已停止")


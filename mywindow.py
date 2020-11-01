import base64
import sqlite3
import sys
import cv2
import requests

import os

from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist

from mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QInputDialog, QLineEdit
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, pyqtSignal, QDir, QUrl, QSettings  # 引入定时器库
from cameravideo import camera
from detect import detect_thread#导入自己写的线程
from adduserwindow import adduserwindow#将用户窗口导入主窗口
from delfacewindow import delfacewindow#将删除用户窗口导入主窗口
from data_show import sign_data
from sign_successwindow import sign_sussesswindow
from playsound import playsound
import time
from PyQt5.QtCore import Qt
'''
子类、继承Ui_MainWindow与QMainWindow
Ui_MainWindow：
    包含是界面的设计，窗口中的窗口部件
QMainWindow：
    包含是整个界面窗口，窗口操作（界面外面的框框）
mywindow:
    完整的窗口类，窗口框框+窗口部件
'''
class mywindow(Ui_MainWindow,QMainWindow):
    #自己设计信号,因为需要传递的参数是bytes类型，所以括号里面写入bytes
    detect_data_signal = pyqtSignal(bytes)
    #定义一个布尔变量，用于充当点击签到和添加用户两个操作的互斥信号（摄像头不能充当，为什么）
    camera_status = False


    # 初始化函数
    def __init__(self):#初始化
        super(mywindow,self).__init__()
        self.setupUi(self)#创建界面内容

        self.systemIsOpen = False
        # 设置一个初始值，后续用来实现：30秒无人脸就进行广告播放
        self.noFaceNum = 0
        #设置时间，用来，当未检测到人脸时，实现配置文件中的定时时间到了后，自动切换到广告播放
        self.timeToChangeVideo = QSettings('config.ini', QSettings.IniFormat).value("timeToChangeVideo")
        print(self.timeToChangeVideo)
        # 标志位，是否在播放广告
        #self.isPlayAdvertising

        self.get_accesstoken()
        #cz 获取公共视频播放列表
        videoList = os.listdir("video/ID0000")
        url = QUrl()
        #将视频列表加载到playList中
        self.playList = QMediaPlaylist()

        # 将个人视频列表加载到playList中
        self.playList2 = QMediaPlaylist()

        #3为列表循环
        self.playList.setPlaybackMode(3)
        self.playList2.setPlaybackMode(3)

        for videoPath in videoList:
            #sys.path[0]获取的绝对路径为反斜杠，需要替换为正的
            url.setUrl("./video/ID0000/" + videoPath)
            print(url)
            self.playList.addMedia(QMediaContent(url))

        #cz
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.videoWidget)

        #添加背景图片


        palette = self.videoWidget.palette()
        print("cccc")
        pixmap = QPixmap("./init.jpg")
        print(pixmap)
        palette.setBrush(palette.Window,QBrush(pixmap))
        self.videoWidget.setPalette(palette)
        self.videoWidget.setAutoFillBackground(True)
        #self.videoWidget.setWindowFlags(Qt.FramelessWindowHint)

        #player2用来播放每个人的视频
        self.player2 = QMediaPlayer()
        #self.player2.setVideoOutput(self.videoWidget)

        #如果图片过大显示不完整，下面这条语句会让图片显示完整
        self.label.setScaledContents(True)
        #在label中插入一张图片
        #self.label.setPixmap(QPixmap("./init.jpg"))
        #创建一个时间定时器
        self.datetime = QTimer(self)
        #启动时间定时器,定时时间为500ms，500ms产生一次信号
        self.datetime.start(500)
        #关联槽函数
        self.datetime.timeout.connect(self.date_time)
        # 创建窗口就应该完成完成访问令牌的申请操作
        #self.get_accesstoken()

        #设计启动关联信号槽
        #信号与槽的关联
        #self.actionopen：指定对象
        #triggered:信号
        #connect:关联（槽函数）
        #self.on_actionopen：关联的函数是on_actionopen这个函数
        self.actionopen.triggered.connect(self.on_actionopen)#actionopen对应界面中的“启动签到”

        #cz 签到按钮开始播放广告
        self.actionopen.triggered.connect(self.openVideoFile)  # actionopen对应界面中的“启动签到”

        #退出签到
        self.actionclose.triggered.connect(self.on_actionclose)
        #添加用户组（班级）信号槽
        self.actionaddgroup.triggered.connect(self.add_group)
        #删除用户组（班级）信号槽
        self.actiondelgroup.triggered.connect(self.delgroup)
        #获取组列表信号槽
        self.actiongetlist.triggered.connect(self.getgrouplist)
        #添加用户
        self.actionadduser.triggered.connect(self.adduser)
        #删除用户
        self.actiondeluser.triggered.connect(self.deluser)
        #签到成功信息查看
        self.actionsave.triggered.connect(self.on_actionsave)

        # #播放视频信息
        # video = 'mlxtj.mp4'  # 加载视频文件
        # self.cap = cv2.VideoCapture(video)

    #创建线程函数完成检测,参数有:令牌,列表（用来存放签到成功的数据）
    def create_thread(self,group):
        self.detectThread = detect_thread(self.access_token,group)
        self.detectThread.start()

    # #函数功能：获取系统时间与日期，添加到界面对应的编辑器中。
    # def date_time(self):
    #     # 获取日期
    #     date = QDate.currentDate()
    #     # 设置日期
    #     self.dateEdit.setDate(date)
    #     # 获取时间
    #     time = QTime.currentTime()
    #     # 设置时间
    #     self.timeEdit.setTime(time)
    #     # 获取日期时间
    #     #datatime = QDateTime.currentDateTime()

    #函数功能：获取系统时间与日期，添加到界面对应的编辑器中。
    def date_time(self):
        qdatetime = QDateTime.currentDateTime()
        self.label_4.setText(qdatetime.toString("ddd  yyyy/MM/dd  hh:mm:ss"))

    #点击签到函数，里面包含打开摄像头，关联一个线程（用于发送人脸检测的图片）
    def on_actionopen(self):
        # 选择签到的班级,先通过函数获取到已经存在的班级
        list = self.getlist()
        # 返回值是一个元组，只需要第一个值,设置输入框的默认值是"class1"

        group, ret = QInputDialog.getItem(self, "选择签到班级", "请选择如下班级进行签到：\n" ,list['result']['group_id_list'],0)
        #group, ret = QInputDialog.getText(self, "选择签到班级", "请选择如下班级进行签到：\n" + str(list['result']['group_id_list']),QLineEdit.Normal, "class1")
        if ret:
            # 启动摄像头
            self.cameravideo = camera()  # 创建摄像头这个类
            # 互斥信号量
            self.camera_status = True

            # 启动检测线程,解决卡顿问题
            self.create_thread(group)
            # 启动定时器，进行定时，每隔10ms进行一次获取摄像头数据进行显示
            # timeshow定时器用作显示画面
            self.timeshow = QTimer(self)
            self.timeshow.start(30)
            # 10ms后定时器启动，产生一个timeout信号，.connect()关联槽函数
            self.timeshow.timeout.connect(self.show_cameradata)

            # facedetecttime定时器设置检测画面获取
            # 当打开摄像头时，创建定时器500ms，用于获取检测的画面
            self.facedetecttime = QTimer(self)
            self.facedetecttime.start(500)
            self.facedetecttime.timeout.connect(self.get_cameradata)  # 关联检测人脸信息函数
            # 通过信号将画面传给线程,每500ms传一次信号，调用线程的get_base64函数，将画面传给线程
            self.detect_data_signal.connect(self.detectThread.get_base64)

            # 线程关联槽函数，从线程中获取到检测的结果，并关联槽函数get_cetectdata用于在界面上显示画面
            self.detectThread.transmit_data.connect(self.get_detectdata)
            # 线程里面人脸搜索返回的结果关联槽函数
            self.detectThread.search_data.connect(self.get_search_data)
            self.systemIsOpen = True

    #退出签到，槽函数
    def on_actionclose(self):
        if self.systemIsOpen:
            print("关闭定时器2")
            #关闭定时器2
            self.facedetecttime.stop()
            #下面三条语句老师讲可写可不写，但如果我这里写上点击退出签到时会有问题，故不写
            #self.facedetecttime.timeout().disconnect(self.get_cameradata)
            #self.detect_data_signal.disconnect(self.detectThread.get_base64)
            #self.detectThread.transmit_data.connect(self.get_detectdata)
            #关闭检测线程
            #退出线程的run函数
            self.detectThread.ok = False
            #线程结束 返回Fslse
            self.detectThread.quit()
            self.detectThread.wait()

            #关闭定时器1，不再去获取摄像头进行数据显示
            self.timeshow.stop()
            # 关闭摄像头
            self.cameravideo.close_camera()

            #设置互斥信号量
            self.camera_status = False
            # 显示本次签到情况,签到数据从线程的字典中拿出来
            # 创建一个类,并将线程传过来的数据交个窗口
            print(self.detectThread.sign_list)

            self.player.pause()
            self.player2.pause()

            signdata = sign_data(self.detectThread.sign_list)
            signdata.exec_()
            # 关初始化状态
            # 摄像头的一个定时器和检测画面的一个定时器同时关闭时才清空
            if self.timeshow.isActive() == False and self.facedetecttime.isActive() == False:
                print("关闭成功")
                #self.label.setPixmap(QPixmap("./init.jpg"))
                self.plainTextEdit.clear()
                self.plainTextEdit_2.clear()
            else:
                print("关闭失败，存在部分窗口没有关闭")


    '''
    信号槽功能：
        当某个组件设计了信号槽功能（关联信号槽）时，当信号产生，会主动调用槽函数去完成对应的功能。
        信号：当以某种特定的操作，操作这个组件时，就会主动产生对应的信号。
    '''

    def get_cameradata(self):
        camera_data = self.cameravideo.read_camera()
        # 把摄像头画面转换成图片，然后设置为base64编码
        _, enc = cv2.imencode('.jpg', camera_data)  # 返回两个元组
        base64_image = base64.b64encode(enc.tobytes())
        #产生信号（自己创的信号），传递数据，默认数据是bytes类型
        #每500ms传一次数据
        self.detect_data_signal.emit(bytes(base64_image))
        #return self.camera_data

    #在界面中显示，只能获取到一次数据，需要设置时间，每隔50ms获取一次

    def show_cameradata(self):

        #30秒无人脸，就会切回广告播放
        if self.noFaceNum == self.timeToChangeVideo:
            self.player.setVideoOutput(self.videoWidget)
            self.player.setPlaylist(self.playList)
            self.player.play()
            self.player2.pause()
            self.noFaceNum = 0
            self.detectThread.isLastFace = False

        #获取摄像头数据，转换数据
        #判断是否检测到了人脸
        if self.detectThread.faceMark:
            self.noFaceNum = 0

            #判断此次检测到的人脸和上一张人脸是否为同一人
            if not self.detectThread.isLastFace:
                # 获取当前人脸对应的视频文件夹
                user_id = self.detectThread.lastFace
                #判断是否存在此用户的视频文件夹
                if os.path.exists("video/"+user_id):
                    url = QUrl()

                    user_id = self.detectThread.lastFace
                    videoList = os.listdir("video/" + user_id)
                    #清空上一个人的播放列表
                    self.playList2.clear()
                    for videoPath in videoList:
                        url.setUrl("./video/" + user_id + "/" + videoPath)
                        self.playList2.addMedia(QMediaContent(url))

                    self.player2.setVideoOutput(self.videoWidget)
                    self.player2.setPlaylist(self.playList2)
                    self.player2.play()
                    self.player.pause()

                self.detectThread.isLastFace = True
                print(self.player.state())
        #判断播放广告的播放器是否运行
        elif self.player.state()==0 or self.player.state()==2 :
            self.noFaceNum = self.noFaceNum + 1
            print(self.noFaceNum)
            #pic = self.cameravideo.camera_to_pic()#将摄像头获取到的数据转换成界面能显示的数据，返回值为qpmaxip
            #print(self.detectThread.isLastFace)
        # else:
        #     pic = self.playVideo()
        # #显示数据，显示画面
        # self.label.setPixmap(pic)  # 将获取到的数据拿到界面中进行显示

    #获取accesstoken（访问令牌）的槽函数
    def get_accesstoken(self):
        #host是字符串对象，存储的是授权服务地址----获取accesstoken的地址
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=HtoZ9pM4HsG7GGEldsbwjOCq&client_secret=3H7vVG5uXklMPRaMeWIA2RwmG30jqk9G'
        #发送网络请求 requests 网络库
        #使用get函数发送网络请求，参数为网络请求地址，执行时会返回执行结果，
        response = requests.get(host)
        if response:
            response= response.json()
            self.access_token = response['access_token']
            #print(self.access_token)

    #槽函数，获取检测数据
    def get_detectdata(self,data):
        # 如果传过来的数据是空的（即没检测到人脸），先将上一次数据清空
        if data['error_code'] != 0:
            self.plainTextEdit_2.setPlainText(data['error_msg'])  #将对话框里面的内容设置为错误代码
        elif data['error_msg'] != 'SUCCESS':
            print("获取数据失败")
        else:
            # 在data字典中，键为'result'对应的值才是返回的检测结果
            self.plainTextEdit_2.clear()  # 将上一次信息清空
            face_num = data['result']['face_num']
            # 判断有无人脸信息
            if face_num == 0:
                self.plainTextEdit_2.appendPlainText("当前没有人以及人脸信息出现")
                return
            else:

                self.plainTextEdit_2.appendPlainText("检测到学生人脸信息\n")
            # 人脸信息：data['result']['face_list']，是列表，每个数据是一个字典
            # 取每个人脸信息 data['result']['face_list'][0-i]
            # 循环取出所有人脸信息
            for i in range(face_num):
                data['result']['face_list'][i]
                age = data['result']['face_list'][i]['age']
                beauty = data['result']['face_list'][i]['beauty']
                gender = data['result']['face_list'][i]['gender']['type']
                expression = data['result']['face_list'][i]['expression']['type']
                face_shape = data['result']['face_list'][i]['face_shape']['type']
                glasses = data['result']['face_list'][i]['glasses']['type']
                emotion = data['result']['face_list'][i]['emotion']['type']
                mask = data['result']['face_list'][i]['mask']['type']
                #人脸库
                left = data['result']['face_list'][i]['location']['left']
                top = data['result']['face_list'][i]['location']['top']
                width = data['result']['face_list'][i]['location']['width']
                height = data['result']['face_list'][i]['location']['height']
                #print("location"+str(left))

                #往窗口中添加文本，参数就是需要的文本信息，年龄需要转换成字符串
                self.plainTextEdit_2.appendPlainText("\n"+"第" + str(i + 1) + "个学生人脸信息\n")
                self.plainTextEdit_2.appendPlainText("年龄是：" + str(age)+"\n")
                #性别
                if gender == 'male':
                    gender = "男"
                else:
                    gender = "女"
                self.plainTextEdit_2.appendPlainText("性别是：" + str(gender)+"\n")
                self.plainTextEdit_2.appendPlainText("颜值分数：" + str(beauty)+"\n")
                #表情
                if expression == 'none':
                    expression = "不笑"
                else:
                    if expression == 'smile':
                         expression = '微笑'
                    else:
                         expression = "大笑"
                self.plainTextEdit_2.appendPlainText("表情：" + str(expression)+"\n")
                #脸型
                if face_shape == 'square':
                    face_shape = "国字脸"
                else:
                    if face_shape == 'triangle':
                        face_shape = "瓜子脸"
                    else:
                        if face_shape == 'voal':
                            face_shape = "椭圆脸"
                        else:
                            if face_shape == 'heart':
                                face_shape = "心形脸"
                            else:
                                face_shape = '圆脸'
                self.plainTextEdit_2.appendPlainText("脸型是：" + str(face_shape)+"\n")
                #眼睛
                if glasses == 'none':
                    glasses = "无眼镜"
                else:
                    if glasses =='common':
                        glasses = "普通眼镜"
                    else:
                        glasses = "墨镜"
                self.plainTextEdit_2.appendPlainText("是否佩戴眼睛：" + str(glasses)+"\n")
                #情绪
                if emotion == 'angry':
                    emotion = "愤怒"
                else:
                    if emotion == 'disgust':
                        emotion ="厌恶"
                    else:
                        if emotion == 'fear':
                            emotion="恐惧"
                        else:
                            if emotion == 'happy':
                                emotion = "高兴"
                            else:
                                if emotion == 'sad':
                                    emotion = "伤心"
                                else:
                                    if emotion == 'surprise':
                                        emotion = "惊讶"
                                    else:
                                        if emotion == 'neutral':
                                            emotion = "无表情"
                                        else:
                                            if emotion == 'pouty':
                                                emotion = "撅嘴"
                                            else:
                                                emotion = "鬼脸"


                self.plainTextEdit_2.appendPlainText("情绪是：" + str(emotion)+"\n")
                if mask == 0:
                    mask = "否"
                else:
                    mask = "是"
                self.plainTextEdit_2.appendPlainText("是否佩戴口罩：" + mask+'\n')
                '''
                 #画出人脸框,会有卡顿，因为API是500ms返回一次结果
                self.leftTopX = int(left)
                self.leftTopY = int(top)
                self.rightBottomX = int(left+width)
                self.rightBottomY = int(top+width)
                img = self.cameravideo.read_camera()
                cv2.rectangle(img, (self.leftTopX, self.leftTopY), (self.rightBottomX, self.rightBottomY),(0,255,0),3)
                cv2.imshow("face", img)
                '''

    #人脸检测与属性分析请求,想得到如年龄、性别等信息。
    #未被调用
    def get_face(self):
        '''
        这是打开对话框获取画面
        #获取一张图片（一帧画面）
        #getOpenFileName()通过对话框的形式获取一张图片（.jpg）路径
        path,ret= QFileDialog.getOpenFileName(self,"open picture",".","图片格式(*.jpg)")
        print(path)
        #把图片转换成base64编码
        fp = open(path,'rb')#以二进制只读打开文件
        #将以二进制形式读到的图片进行base64编码操作
        base64_image = base64.b64encode(fp.read())
        '''
        #摄像头获取画面
        #得到摄像头数据
        camera_data = self.cameravideo.read_camera()
        #把摄像头画面转换成图片，然后设置为base64编码
        _,enc = cv2.imencode('.jpg',camera_data)#返回两个元组
        base64_image = base64.b64encode(enc.tobytes())
        #发送请求地址
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        #请求参数，是一个字典，在字典中存储了，百度AI要识别的图片信息，属性内容
        params = {
            "image":base64_image,#图片信息字符串
            "image_type":"BASE64",#图片信息的格式
            "face_field":"gender,age,beauty,expression,face_shape,glasses,emotion,mask",#请求识别人脸的属性，各个属性在字符串中用逗号隔开
            "max_face_num":10#最多可以检测人脸的数目为：10
                }

        #访问令牌，已经获取到
        access_token = self.access_token
        #把请求地址和访问令牌组成可用的网络地址
        request_url = request_url + "?access_token=" + access_token
        #参数，设置请求格式体（字典）
        headers = {'content-type': 'application/json'}
        #发送网络post请求，请求百度AI进行人脸检测，返回检测结果
        #发送网络请求，就会一定的等待时间，程序就会在这里阻塞执行
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()

    #槽函数，接受从线程传来的数据并进行显示
    def get_search_data(self,data):
        self.plainTextEdit.setPlainText(data)


    #添加用户组（班级）功能函数
    #添加班级的同时创建两张表，学生表:class_*_student(*号对应班级），签到表：class_*_student_sign
    def add_group(self):
        '''
        创建用户组（班级）
        '''

        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/add"
        #这里设置一下，可以在界面上自己输入用户组
        #打开对话框，进行输入用户组,group是一个元组,只需要第一个数据
        group,ret = QInputDialog.getText(self,"添加班级","请输入班级(由数字、字母、下划线组成)")

        params = {
                 "group_id":group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            message = response.json()
            if message['error_code'] == 0:
                # 创建两张表
                conn = sqlite3.connect('my.db')
                c = conn.cursor()
                # 添加班级学生表，class3_STUDENT
                table_1 = group + '_STUDENT'
                c.execute("CREATE TABLE '" + table_1 + "'(ID int PRIMARY KEY NOT NULL,NAME TEXT NOT NULL,CLASS TEXT)")
                # 添加班级学生签到表 class3_STUDENT_SINGN
                table_2 = group + '_STUDENT_SIGN'
                # 签到成功表包含：学号，姓名，班级，签到日期
                c.execute(
                    "CREATE TABLE '" + table_2 + "'(ID INT PRIMARY KEY NOT NULL,NAME TEXT NOT NULL,CLASS TEXT,DATE TXET NOT NULL)")
                conn.commit()
                print("创表成功！")
                print("添加班级成功！")
                QMessageBox.about(self,"班级添加结果","班级添加成功")

            else:
                QMessageBox.about(self,"班级添加结果","班级添加失败\n"+message['error_msg'])



    #删除用户组
    def delgroup(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/delete"
        #删除，需要知道存在哪些组，应先完成列表查询
        list = self.getlist()

        #提示可以删除哪些用户组的对话框
        group,ret = QInputDialog.getText(self,"存在的班级","班级信息\n"+str(list['result']['group_id_list']))
        params = {
            "group_id":group#要删除的用组织Id
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
             data = response.json()
             if data['error_code'] == 0:
                QMessageBox.about(self,"班级删除","删除成功")
             else:
                QMessageBox.about(self, "用户组删除", "删除失败")
        #删除两张表
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        table_1 = group + '_STUDENT'
        c.execute("drop TABLE '" + table_1 + "'")
        print("ok1")
        table_2 = group + '_STUDENT_SIGN'
        c.execute("drop TABLE '" + table_2 + "'")
        print("删表成功！")
        print("删除班级成功！")
        conn.commit()
    #用户组查询
    def getlist(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getlist"
        #两个参数，起始，结束
        params = {
            "start":0,"length":100
                  }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()

    #显示查询到的用户组
    def getgrouplist(self):
        list = self.getlist()
        str = ''
        for i in list['result']['group_id_list']:
            str = str +'\n'+i
        QMessageBox.about(self,"班级列表",str)

    #再写一个函数，为了一直打开添加学生这个窗口
    def adduser(self):
        # 创建一个窗口来选择这些内容
        # 在请求参数中，需要获取人脸，转换人脸编码，添加的组id，添加的用户id，新用户的id信息
        # 开始签到和添加用户是互斥的操作，用到操作系统里面的互斥信号量机制，摄像头就是这个信号
        if self.camera_status:
            QMessageBox.about(self, "摄像头状态", "摄像头已打开，正在进行人脸签到，请关闭签到再添加用户\n")
            return
        list = self.getlist()
        #首先选择班级，选择好后传到后台
        i = ''
        for l in list['result']['group_id_list']:
            i=i+l+' '
        group, ret = QInputDialog.getText(self, "添加学生", "请选择添加学生的班级\n" + i,QLineEdit.Normal, "class1")
        #再次打开添加人脸窗口
        while(1):
            self.window = adduserwindow(group, self)
            # 新创建窗口，通过exec()函数一直执行，阻塞执行，窗口不进行关闭exec()函数不会退出
            # 窗口关闭时会有一个结束的标志
            window_status = self.window.exec_()
            # 根据返回值（选择项）不同进行优化,窗口不会有错误变化
            if window_status != 1:
                return
            self.adduser_1()


    #添加用户(人脸注册)
    def adduser_1(self):
        print(self.window.group_id)
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
        #需要进行判断，判断是否点击确定进行关闭
        params = {
            #人脸图片
            "image":self.window.base64_image,
            #人脸图片编码
            "image_type":"BASE64",
            #组id
            "group_id":self.window.group_id,
            #新用户id
            "user_id":self.window.user_id,
            #用户信息
            "user_info":'姓名:'+self.window.msg_name
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            if data['error_code'] == 0:
                print("添加成功")

            '''
            需要自己创建一个窗口来表示人脸信息是否添加成功
            if data['error_code'] == 0:
                print("添加成功")
            else:
                print("添加失败")
            '''
    #删除用户中的一张人脸信息(face_token)
    def del_face_token(self,group,user,face_token):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete"
        params = {
            "user_id":user,
            "group_id":group,
            "face_token":face_token
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
                    return response.json()

    #获取用户列表,需要传一个用户组过来
    def getuserslist(self,group):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getusers"

        params = {
                 "group_id":group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()

    #获取人脸列表，需要传递两个参数:group和user
    def user_face_list(self,group,user):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/getlist"

        params = {
            "user_id": user,
            "group_id": group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()
    #删除用户
    def deluser(self):
        #查询用户人脸信息(face_token)
        #获取用户组，进行选择
        list = self.getlist()
        accesstoken = self.access_token
        #改进：通过界面来选择删除用户
        window_2 = delfacewindow(list['result']['group_id_list'],accesstoken,self)
        window_status = window_2.exec_()
        if window_status != 1:
            return

        #获取到用户人脸的face_token值
        face_list = self.user_face_list(window_2.group_id, window_2.user_id)
        #从face_list（人脸列表）中取出face_token值
        for i in face_list['result']['face_list']:
                face_token = i['face_token']
        #调用删除人脸信息的函数，参数不需要self!!!
        status = self.del_face_token(window_2.group_id,window_2.user_id,face_token)
        if status['error_msg'] == 'SUCCESS':
            print("删除成功")
        else:
            print("删除失败")
        '''
            提示删除成功或者失败
            print(status['error_msg'])
        if status['error_msg'] == 'SUCCESS':
            QMessageBox.about("删除成功")
        else:
            QMessageBox.about("删除失败")
        '''

        '''
        group,ret = QInputDialog.getText(self,"班级获取","班级信息\n"+str(list['result']['group_id_list']))
        #获取用户，进行选择
        userlist = self.getuserslist(group)
        user, ret = QInputDialog.getText(self, "用户获取", "用户信息\n" + str(userlist['result']['user_id_list']))
        #获取用户的人脸列表
        face_list  = self.user_face_list(group,user)
        #千辛万苦得到了face_token值
        for i in face_list['result']['face_list']:
            self.del_face_token(group,user,i['face_token'])
        '''

    #查看签到成功的信息
    def on_actionsave(self):
        list = self.getlist()
        i = ''
        for l in list['result']['group_id_list']:
            i = i + l + ' '
        group, ret = QInputDialog.getText(self, "添加学生", "请选择添加学生的班级\n" + i, QLineEdit.Normal, "class1")
        window_3 = sign_sussesswindow(group,self)
        status = window_3.exec_()

    #播放广告视频
    def playVideo(self):
        ret, data = self.cap.read()  # ret是否成功，data是数据
        if not ret:
            print("获取摄像头数据失败!!!")
            return None
        currentframe = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        # 设置宽和高
        # self.currentframe = cv2.cvtColor(self.currentframe,(640,480))
        # 转换格式（界面能够显示的格式）lable显示Qpixmap
        # 获取画面的宽度和高度
        height, width = currentframe.shape[:2]
        # 先转换成QImage类型的图片（画面），创建QImage对象，使用摄像头的画面数据进行创建
        # QImage(data,width,height,format)创建：数据，宽度，高度，格式
        qimg = QImage(currentframe, width, height, QImage.Format_RGB888)
        # 由于上面的形式不适合图像显示，故还需要转换格式
        qpixmap = QPixmap.fromImage(qimg)
        return qpixmap

    #cz
    def openVideoFile(self):
        self.player.setPlaylist(self.playList)
        self.player.play()  # 播放视频


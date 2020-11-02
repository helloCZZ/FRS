'''
#QThread就是Pyqt5提供的线程类
#由于是一个已经完成了的类，功能已经写好，线程类的功能需要自己完成
#需要自己完成需要的线程类，创建一个新的线程类（功能自己定义），继承QThread
#新写的类具有线程的功能
'''
import base64
import cv2
import sqlite3
import requests
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QDateTime, QSettings


#线程进行执行，只会执行线程类中的run函数，如果有新的功能需要实现，需要重新写一个run函数完成
class detect_thread(QThread):#新的线程类，并继承QThread
    #创建信号槽，字典类型
    transmit_data = pyqtSignal(dict)
    #创建第二个信号槽,将人脸搜索的结果返回到主界面
    search_data = pyqtSignal(str)
    #ok(布尔值)用于判断退出while循环
    ok = True

    #标志位，判断是否检测到人脸
    faceMark = False

    #最后一次检测到的人脸
    lastFace = ''
    # 判断最后一次检测到的人脸
    isLastFace = True

    #创建字典，用来存放签到数据
    sign_list = {}
    def __init__(self,token,group):#进行初始化,需要传递一个token(访问令牌)参数
        super(detect_thread, self).__init__()#初始化父类 后面括号不需要self
        self.access_token = token
        self.group = group
        self.condition = False
        #活体检测
        self.liveness_control = QSettings('config.ini', QSettings.IniFormat).value("liveness_control")
    #run函数执行结束代表线程结束
    def run(self):
        print("run")

        '''
        # 让run函数一直执行的函数
        self.exec_()
        self.time = QTimer()
        self.time.start(1000)
        #关联信号和槽
        self.time.timeout.connect(self.detect_face)
        '''
        #让run函数一直执行detect_face()函数
        while self.ok:
            #当condition=True(即得到数据)时执行detect_face()
            if self.condition:
                self.detect_face(self.base64_image)
                #执行完一次将condition设置为False
                self.condition = False
    def get_base64(self,base64_image):
        #当窗口产生信号，调用这个槽函数，就把传递的数据，存放在现存的变量中
        self.base64_image = base64_image
        self.condition = True
    # 脸检测与属性分析请求,想得到如年龄、性别等信息(放到了线程里面)
    #detect_face(self)前身是get_face(self)函数
    def detect_face(self,base64_image):
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

        # 发送请求地址
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        # 请求参数，是一个字典，在字典中存储了，百度AI要识别的图片信息，属性内容
        params = {
            "image": base64_image,  # 图片信息字符串
            "image_type": "BASE64",  # 图片信息的格式
            "face_field": "gender,age,beauty,expression,face_shape,glasses,emotion,mask",  # 请求识别人脸的属性，各个属性在字符串中用逗号隔开
            "max_face_num": 10,# 最多可以检测人脸的数目为：10
            "liveness_control":self.liveness_control
        }

        # 访问令牌，已经获取到
        access_token = self.access_token
        # 把请求地址和访问令牌组成可用的网络地址
        request_url = request_url + "?access_token=" + access_token
        # 参数，设置请求格式体（字典）
        headers = {'content-type': 'application/json'}
        # 发送网络post请求，请求百度AI进行人脸检测，返回检测结果
        # 发送网络请求，就会一定的等待时间，程序就会在这里阻塞执行
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            #print(data)
            #做一个判断：如果没有检测到人脸，将错误代码返还回去，注意需要有return语句
            if data['error_code'] !=0:
                self.transmit_data.emit(data)
                self.search_data.emit("摄像头未获取到画面，请不要遮挡摄像头")
                self.faceMark = False
                return
            #当检测到有人脸时执行人脸搜索功能
            if data['result']['face_num'] > 0:
                # 发送信号emit()，将获取到的数据传到主界面
                self.transmit_data.emit(dict(data))
                self.face_search()

                #将人脸标志位设置为True
                self.faceMark = True
            #当没有检测到人脸，发送空数据过去
            else:
                # 发送信号emit()
                print("not detectface")
                # 将人脸标志位设置为False
                self.faceMark = False
    #人脸搜索功能,只识别一个人
    def face_search(self):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"

        params = {
            "image":self.base64_image,
            "image_type":"BASE64",
            #从哪些组中进行人脸识别,点击签到时就将组号传过来
            "group_id_list":self.group
           }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            print(data)
            if data['error_code'] == 0:
                #判断相似度是否大于90，大于能用，否则不能用
                if data['result']['user_list'][0]['score']>90:

                    #存储要保存的签到的数据，方便进行显示
                    #将相似度删除掉，不用保存
                    del[data['result']['user_list'][0]['score']]
                    #获取当前系统时间
                    datetime = QDateTime.currentDateTime()
                    #将时间转换成字符串,只显示月日 时间
                    datetime = datetime.toString("MM-dd hh:mm:ss")
                    data['result']['user_list'][0]['datetime'] = datetime
                    #设置一个键，唯一标识一个人，防止错误重复进行签到
                    key = data['result']['user_list'][0]['group_id']+data['result']['user_list'][0]['user_id']
                    #如果key不存在，则进行添加
                    if key not in self.sign_list.keys():
                        self.sign_list[key] = data['result']['user_list'][0]
                    #0表示第一个人，因为是只检测一张人脸
                    #通过信号槽的方式将人脸搜索返回的结果传到主界面
                    user_id = data['result']['user_list'][0]['user_id']
                    user_info = data['result']['user_list'][0]['user_info']

                    if self.lastFace != user_id:
                        self.isLastFace = False
                    # 保存最后一次的人脸id
                    self.lastFace = user_id
                    self.search_data.emit("用户人脸识别成功!\n\n"+"编号:"+user_id+'\n\n'+user_info)
            else:
                self.search_data.emit("用户签到不成功,找不到对应的用户")

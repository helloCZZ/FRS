import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from mywindow import mywindow
import sys,os
from PyQt5.QtWidgets import QDialog
from login import Ui_Dialog
class login_window(Ui_Dialog,QDialog):
    def __init__(self):
        super(login_window,self).__init__()
        self.setupUi(self)
        # 创建Qsettings对象
        self.app_data = QSettings('config.ini', QSettings.IniFormat)
        self.app_data.setIniCodec('UTF-8')  # 设置ini文件编码为 UTF-8
        # 检查是否有数据进行初始化
        if os.path.exists('./config.ini'):  # 方式2
            # 如果存在数据就进行初始化
            self.init_info()
        else:
            # 没有数据就认为是第一次打开软件，进行第一次QSettings 数据存储
            self.save_info()

        self.pushButton_1.clicked.connect(self.on_pushButton_enter_clicked)
        self.pushButton_2.clicked.connect(QCoreApplication.instance().quit)
    # 对帐号和密码进行判读
    def on_pushButton_enter_clicked(self):
        # 账号判断
        if self.lineEdit.text() == None:
            QMessageBox(self, "温馨提示", "没有输入账号！")
            return
        # 密码判断
        elif self.lineEdit_2.text() == " ":
            QMessageBox(self, "温馨提示", "没有输入密码！")
            return
        else:

            client_id = self.lineEdit.text()
            client_secret = self.lineEdit_2.text()
            host = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s" % (
                client_id, client_secret)
            # 发送网络请求 requests 网络库
            # 使用get函数发送网络请求，参数为网络请求地址，执行时会返回执行结果，
            response = requests.get(host)
            if response:
                response = response.json()
                self.access_token = response['access_token']
                self.save_info()
                # 通过验证，关闭对话框并返回1

                self.accept()
            else:
                QMessageBox.about(self, "温馨提示", "帐号或密码错误，请检查后重新输入！\n")
                return
    def transport(self):
        return self.access_token

    #保存帐号和密码到配置文件中去
    def save_info(self):
        time = QDateTime.currentDateTime() #获取当前时间，并存储在self.qpp_data
        self.app_data.setValue('time', time.toString())  #数据0：time.toString()为字符串类型
        self.text = self.lineEdit.text()
        self.text_2 = self.lineEdit_2.text()
        print(self.text)
        #self.text = self.textEdit.toPlainText()#获取当前文本框的内容
        self.app_data.setValue('API_Key', self.text)#数据1：也是字符串类型
        self.app_data.setValue('Secret_Key',self.text_2)
        a = 1  #数据3：数值类型
        list = [1,'a',2] #数据4：列表类型
        bool = True #数据:5：布尔类型
        dict = {'a':'abc','b':2} #数据6：字典类型
        self.app_data.setValue('a', a)
        self.app_data.setValue('list', list)
        self.app_data.setValue('bool', bool)
        self.app_data.setValue('dict', dict)

    def init_info(self):
        time = self.app_data.value('time')
        self.text = self.app_data.value('API_Key')
        self.text_2 = self.app_data.value('Secret_Key')
        a = self.app_data.value('a')
        list = self.app_data.value('list')
        bool = self.app_data.value('bool')
        dict = self.app_data.value('dict')
        #初始化文本框的内容
        self.lineEdit.setText(self.text)
        self.lineEdit_2.setText(self.text_2)


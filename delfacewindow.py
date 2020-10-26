#删除人脸信息
import sqlite3

import requests
from PyQt5.QtWidgets import QDialog
from delface import Ui_Dialog
from PyQt5 import QtCore
#创建一个delfacewindow类，QDialog不能省略（不知道具体是做什么的）

class delfacewindow(Ui_Dialog,QDialog):
    #初始化函数，用户组列表和用户显示是在初始化函数中实现的,需要从主窗口传过来一个用户组列表(list)
    def __init__(self,list,accesstoken,parent=None):
        self.accesstoken = accesstoken
        super(delfacewindow,self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('删除学生')
        # 把组信息显示在列表框中
        self.show_list(list)
        self.pushButton_3.clicked.connect(self.show_userlist)
        self.pushButton.clicked.connect(self.get_data_close)
        self.pushButton_2.clicked.connect(self.close_window)

    # 把组信息显示在列表框中
    def show_list(self, list):
        for l in list:
            self.listWidget.addItem(l)

    #根据选择的用户组，显示对应的用户列表
    def show_userlist(self):
        #得到用户组列表的id
        self.group_id = self.listWidget.currentItem().text()
        #根据用户组的id获取用户列表
        list_user = self.getuserslist(self.group_id,self.accesstoken)
        #先清除之前画面的内容
        self.listWidget_2.clear()
        # 得到用户列表后显示到界面中
        for i in range(len(list_user)):
            #根据学生学号找到学生，并将学号和姓名显示到界面上
            conn = sqlite3.connect('my.db')
            c = conn.cursor()
            cursor = c.execute("select name,id from student_1 where id = '" + list_user[i] + "'")
            #cursor = c.execute("select name from student_1 where id = ?",123)
            #print(c.fetchall())
            for l in cursor:
                name = str(l[0])
                id = str(l[1])
                print(str(name))
                self.listWidget_2.addItem(id+'  '+name)


    # 获取用户列表,需要传一个用户组过来
    def getuserslist(self, group,accesstoken):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getusers"

        params = {
            "group_id": group
        }
        access_token = accesstoken
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            data = response.json()
            user_id = data['result']['user_id_list']
            return user_id

    # 确定按钮功能
    def get_data_close(self):
        self.group_id = self.listWidget.currentItem().text()
        self.user_id = self.listWidget_2.currentItem().text()
        #点击确定后关闭窗口
        #accept()函数返回值是1
        self.accept()

    #取消按钮功能
    def close_window(self):
        #reject()函数的返回值是0
        self.reject()


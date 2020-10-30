
from PyQt5.QtWidgets import QApplication
from mywindow import mywindow
import sys
from login_window import QDialog, login_window
import PyQt5
'''
程序的解释执行文件
if...判断当前是否为执行文件，可以不写
'''

if __name__ == '__main__':
    # 创建应用程序对象
    app = QApplication(sys.argv)
    dialog = login_window()
    # 通过验证进入主窗口
    if dialog.exec_() == QDialog.Accepted:
        #从login中获取到token值，并传给主界面
        token = dialog.transport()
        # 创建窗口
        ui = mywindow(token)
        # 显示窗口
        ui.show()
        # 应用程序执行
        app.exec_()
        # 退出
        sys.exit(0)
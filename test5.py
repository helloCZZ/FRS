import sys
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

################################################

items_list = ["张", "C++", "Java", "Python", "JavaScript", "C#", "Swift", "go", "Ruby", "Lua", "PHP"]


################################################
class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(self)
        self.lineedit = QLineEdit(self, minimumWidth=200)
        self.combobox = QComboBox(self, minimumWidth=200)
        self.combobox.setEditable(True)

        layout.addWidget(QLabel("QLineEdit", self))
        layout.addWidget(self.lineedit)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        layout.addWidget(QLabel("QComboBox", self))
        layout.addWidget(self.combobox)
        # 初始化combobox
        self.init_combobox()

    def init_combobox(self):
        # 增加选项元素
        for i in range(len(items_list)):
            self.combobox.addItem(items_list[i])
        self.combobox.setCurrentIndex(-1)
        # 增加自动补全
        self.completer = QCompleter(items_list)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.combobox.setCompleter(self.completer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())





from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class Preferences(QDialog):
    checkboxsig=pyqtSignal(bool)
    def __init__(self,parent=None,showToolbar=True):
        super(Preferences, self).__init__(parent)

        self.resize(100,200)
        self.setWindowTitle("Preferences")
        self.checkBox=QCheckBox("Show main toolbar")
        self.checkBox.setChecked(showToolbar)
        self.closeBtn=QPushButton("Close")

        layout=QVBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.closeBtn)
        self.setLayout(layout)

        self.closeBtn.clicked.connect(self.close)
        self.checkBox.stateChanged.connect(self.checkBoxStateChanged)
        #self.checkboxsig.connect(self.deneme)


    def checkBoxStateChanged(self):
        self.checkboxsig.emit(self.checkBox.isChecked())


    def deneme(self,param):
        print("signal ok")
        print(param)
#
# if __name__ == '__main__':
#     app=QApplication(sys.argv)
#
#     form=Preferences()
#
#     form.show()
#     sys.exit(app.exec_())

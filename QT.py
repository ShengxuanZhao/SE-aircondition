# !/usr/bin/python3
# -*- coding: utf-8 -*-

#exitButton = QAction(QIcon('/Users/victoria/Downloads/d0c2c5f7cb95aed783f10ba6cd687c73.jpg'), 'Exit', self)
import sys
from PyQt5.QtCore import (QDate, Qt)
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot



class Controler(QDialog):

    text = " "


    def __init__(self, parent=None):
        super(Controler, self).__init__(parent)
        roomid = QLabel("请选择您想查看的房间号🏨", self)
        combo=QComboBox(self)
        #调取所有的房间
        
        combo.addItem("sda")
        combo.addItem("QWE")
        self.text = combo.currentText()


        self.buttonBox = QPushButton("👌",self) #QDialogButtonBox(QDialogButtonBox.Ok)

        self.paidCheckBox = QCheckBox("&Paid")
        checkNumLabel = QLabel("Check &No.:")
        self.checkNumLineEdit = QLineEdit()
        checkNumLabel.setBuddy(self.checkNumLineEdit)

        bankLabel = QLabel("&Bank:")
        self.bankLineEdit = QLineEdit()
        bankLabel.setBuddy(self.bankLineEdit)

        accountNumLabel = QLabel("Acco&unt No.:")
        self.accountNumLineEdit = QLineEdit()
        accountNumLabel.setBuddy(self.accountNumLineEdit)

        sortCodeLabel = QLabel("Sort &Code:")
        self.sortCodeLineEdit = QLineEdit()
        sortCodeLabel.setBuddy(self.sortCodeLineEdit)

        creditCardLabel = QLabel("&Number:")
        self.creditCardLineEdit = QLineEdit()
        creditCardLabel.setBuddy(self.creditCardLineEdit)

        validFromLabel = QLabel("&Valid From:")
        self.validFromDateEdit = QDateEdit()
        validFromLabel.setBuddy(self.validFromDateEdit)
        self.validFromDateEdit.setDisplayFormat("MMM yyyy")
        self.validFromDateEdit.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        expiryLabel = QLabel("E&xpiry Date:")
        self.expiryDateEdit = QDateEdit()
        expiryLabel.setBuddy(self.expiryDateEdit)
        self.expiryDateEdit.setDisplayFormat("MMM yyyy")
        self.expiryDateEdit.setAlignment(Qt.AlignRight|Qt.AlignVCenter)


        tabWidget = QTabWidget()
        cashWidget = QWidget()
        cashLayout = QHBoxLayout()
        cashLayout.addWidget(self.paidCheckBox)
        cashWidget.setLayout(cashLayout)
        tabWidget.addTab(cashWidget, "系统管理")
        checkWidget = QWidget()
        checkLayout = QGridLayout()
        checkLayout.addWidget(checkNumLabel, 0, 0)
        checkLayout.addWidget(self.checkNumLineEdit, 0, 1)
        checkLayout.addWidget(bankLabel, 0, 2)
        checkLayout.addWidget(self.bankLineEdit, 0, 3)
        checkLayout.addWidget(accountNumLabel, 1, 0)
        checkLayout.addWidget(self.accountNumLineEdit, 1, 1)
        checkLayout.addWidget(sortCodeLabel, 1, 2)
        checkLayout.addWidget(self.sortCodeLineEdit, 1, 3)
        checkWidget.setLayout(checkLayout)
        tabWidget.addTab(checkWidget, "报表系统")

        gridLayout = QGridLayout()
        gridLayout.addWidget(roomid, 0, 0)
        gridLayout.addWidget(combo, 0, 1)

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addWidget(tabWidget)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        for lineEdit in (self.checkNumLineEdit, self.accountNumLineEdit,
                self.bankLineEdit, self.sortCodeLineEdit,
                self.creditCardLineEdit):
            lineEdit.textEdited.connect(self.updateUi)

        for dateEdit in (self.validFromDateEdit, self.expiryDateEdit):
            dateEdit.dateChanged.connect(self.updateUi)

        self.paidCheckBox.clicked.connect(self.updateUi)

        self.updateUi()
        self.setWindowTitle("服务端控制面板")

    @pyqtSlot()
    def onclick(self):
        print("点击弹出窗口成功")
        print(self.text)
        # 用萱萱的函数获取

    def updateUi(self):
        i=1
        today = QDate.currentDate()
        #self.text = combo.currentText()
        if self.text!=" ":
            self.buttonBox.setEnabled(bool(True))
            self.buttonBox.clicked.connect(self.onclick)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Controler()
    form.show()
    app.exec_()

"""
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(520, 401)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(350, 260, 91, 51))
        self.quitButton.setAutoDefault(False)
        self.quitButton.setDefault(False)
        self.quitButton.setFlat(False)
        self.quitButton.setObjectName("quitButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 520, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("hi", "hi"))
        self.quitButton.setText(_translate("MainWindow", "quit2333"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(widget)
    widget.show()
    sys.exit(app.exec_())
"""
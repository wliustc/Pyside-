#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-08 13:07:08
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import json
import os
import sys
from PySide import QtGui
from PySide import QtCore
from config import *

if not os.path.exists(userSettingDate):
    with open(userSettingDate, 'w'):
        pass


def setUpDate(newOption):
    with open(userSettingDate, 'rb') as rf:
        if rf.read():
            rf.seek(0)
            oldDate = json.load(rf)
        else:
            oldDate = {}
    with open(userSettingDate, 'wb') as f:
        oldDate.update(newOption)
        json.dump(oldDate, f)


def showOption():
    with open(userSettingDate) as f:
        date = json.load(f)
        return date


class CaptchaOption(QtGui.QWidget):

    def __init__(self, parent=None):
        super(CaptchaOption, self).__init__(parent)
        captchaLayout = QtGui.QGridLayout(self)
        self.platformLabel = QtGui.QLabel()
        self.platformLabel.setText(u'打码平台: ')
        self.platformBox = QtGui.QComboBox()
        self.platformBox.addItem(u'UU打码')
        self.uuuser = QtGui.QLabel()
        self.uuuser.setText(u'平台帐号: ')
        self.userLineEdit = QtGui.QLineEdit()
        self.uupasswd = QtGui.QLabel()
        self.uupasswd.setText(u'平台密码: ')
        self.passwdLineEdit = QtGui.QLineEdit()
        self.checkBox = QtGui.QCheckBox(u'是否启用打码平台')

        captchaLayout.addWidget(self.platformLabel, 0, 0)
        captchaLayout.addWidget(self.platformBox, 0, 1)
        captchaLayout.addWidget(self.uuuser, 1, 0)
        captchaLayout.addWidget(self.userLineEdit, 1, 1)
        captchaLayout.addWidget(self.uupasswd, 2, 0)
        captchaLayout.addWidget(self.passwdLineEdit, 2, 1)
        captchaLayout.addWidget(self.checkBox, 3, 1)


class SysOption(QtGui.QWidget):

    def __init__(self, parent=None):
        super(SysOption, self).__init__(parent)
        mainLayout = QtGui.QGridLayout(self)

        capInfo = QtGui.QSplitter()
        self.captcha = CaptchaOption(capInfo)
        capInfo.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)

        buttonLayout = QtGui.QHBoxLayout()
        changeButton = QtGui.QPushButton(u"修改")
        saveButton = QtGui.QPushButton(u'保存设置')
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(changeButton)
        buttonLayout.addWidget(saveButton)

        mainLayout.addWidget(capInfo, 0, 1)
        mainLayout.addLayout(buttonLayout, 1, 1)

        saveButton.clicked.connect(self.saveOption)
        changeButton.clicked.connect(self.setEditorsEnable)

        self.checkBoxList = [('uuPlatform', self.captcha.checkBox)]
        self.editList = [('uuUser', self.captcha.userLineEdit),
                         ('uuPasswd', self.captcha.passwdLineEdit)]
        self.initializtion()

    def initializtion(self):
        self.setEditorsEnable(False)
        oldOption = showOption()
        [edit.setText(oldOption[kw]) for kw, edit in self.editList]
        [chcekBox.setCheckState(QtCore.Qt.Checked)
            for kw, chcekBox in self.checkBoxList if oldOption[kw]]

    def setEditorsEnable(self, bo=True):
        [edit.setEnabled(bo) for kw, edit in self.editList + self.checkBoxList]

    def saveOption(self):
        setNewText = {kw: edit.text() for kw, edit in self.editList}
        setNewCheck = {kw: check.checkState() == QtCore.Qt.Checked
                       for kw, check in self.checkBoxList}
        self.setEditorsEnable(False)
        setNewCheck.update(setNewText)
        setUpDate(setNewCheck)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = SysOption()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-08 11:47:55
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import sys
from PySide import QtGui
from automation import Automation
from sysOption import SysOption


class MainDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        tabWidget = QtGui.QTabWidget(self)
        system_tab = SysOption()
        self.automation_tab = Automation()
        tabWidget.addTab(self.automation_tab, self.tr("自动化下单"))
        tabWidget.addTab(system_tab, self.tr('系统设置'))
        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.addWidget(tabWidget)
        self.setWindowTitle(u'吾宁当当自动下单')
        self.resize(800, 800)

    def center(self):
        # 获得窗口的数据,PySide.QtCore.QRect
        qr = self.frameGeometry()
        # 获得本机可视窗口的中心点坐标
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        # 将QRect移动到中心点
        qr.moveCenter(cp)
        # 用模拟矩形得到的位置，将窗口本身移动到中心点
        self.move(qr.topLeft())

    def closeEvent(self, event):
        # 将弹出窗口的结果赋值给reply
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        # 检验用户返回，并返回对应的结果
        if reply == QtGui.QMessageBox.Yes:
            if hasattr(self.automation_tab, 'threadsList'):
                [t.dangDangXiaDan.browser.close()
                 for t in self.automation_tab.threadsList
                    if t.isRunning()]
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    k = MainDialog()
    k.show()
    app.exec_()

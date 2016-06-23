#!/usr/bin/env python
# @Date    : 2016-06-08 11:47:55
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import sys
from PySide import QtGui
from automation import Automation
from sysOption import SysOption


class MainDialog(QtGui.QWidget):
    '''
    主窗口界面，包括两个Tab页
    下单界面以及系统设置
    '''
    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        tabWidget = QtGui.QTabWidget(self)
        system_tab = SysOption()
        self.automation_tab = Automation()
        tabWidget.addTab(self.automation_tab, self.tr("自动化下单"))
        tabWidget.addTab(system_tab, self.tr('系统设置'))
        # 网格布局
        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.addWidget(tabWidget)
        # 设置标题
        self.setWindowTitle(u'吾宁当当自动下单')
        # 设置500左右避免某些低分辨率电脑界面超出屏幕范围
        self.resize(1000, 500)

    def center(self):
        '''
        设置主界面在初始化的时候在屏幕中央
        '''
        # 获得窗口的数据,PySide.QtCore.QRect
        qr = self.frameGeometry()
        # 获得本机可视窗口的中心点坐标
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        # 将QRect移动到中心点
        qr.moveCenter(cp)
        # 用模拟矩形得到的位置，将窗口本身移动到中心点
        self.move(qr.topLeft())

    def closeEvent(self, event):
        '''
        设置窗口关闭事件
        '''
        # 将弹出窗口的结果赋值给reply
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           u"确定要关闭当前窗口吗?",
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        # 检验用户返回，并返回对应的结果
        if reply == QtGui.QMessageBox.Yes:
            # 关闭窗口停止正在运行的browser
            if hasattr(self.automation_tab, 'threadsList'):
                [t.dangDangXiaDan.browser.close()
                 for t in self.automation_tab.threadsList
                    if t.isAlive()]
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    k = MainDialog()
    k.show()
    sys.exit(app.exec_())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-08 11:04:02
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import sys
import string
from PySide import QtGui
from PySide import QtCore
from config import *
from dangdang_pyside import DangDangXiaDan
from sysOption import showOption
# 重载sys时,偶尔会丢失标准输出，标准输入等，所以最好提前赋值
stdi, stdo, stde = sys.stdin, sys.stdout, sys.stderr
reload(sys)
sys.stdin, sys.stdout, sys.stderr = stdi, stdo, stde
# 重置系统编码格式为UTF8
sys.setdefaultencoding('utf8')

# 设置全局的slef.tr的字符串编码为utf8
QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf8"))


class Communicate(QtCore.QObject):
    # 收发无参数信号
    sig = QtCore.Signal()


def csv_processing(filename):
    '''
    读取csv文件，并处理数据
    '''
    with open(filename) as f:
        # 最好加上判断字符编码集
        base_info = f.read().decode('gb2312').encode('utf8')
    # 清理数据
    pre_user_info_list = [i.split(',') for i in base_info.split('\n')[1:] if i]
    user_info_list = []
    for i in pre_user_info_list:
        # 为选中，日志等建立空列
        [i.insert(1, '') for a in range(4)]
        # 处理图书信息
        i[7] = i[7].split(';')
        i[8] = i[8].split(';')
        user_info_list.append(i)
    print(u'获得%s 个订单...' % len(user_info_list))
    return user_info_list


class Automation(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Automation, self).__init__(parent)
        self.mainLayout = QtGui.QGridLayout(self)
        self.bottomLayout = QtGui.QHBoxLayout()
        self.text = QtGui.QTextBrowser()
        self.fileLabel = QtGui.QLabel(self.tr(''))

        self.loadButton = QtGui.QPushButton(self.tr("导入文件"))
        beginButton = QtGui.QPushButton(self.tr("开始任务"))
        stopButton = QtGui.QPushButton(self.tr("暂停"))

        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.loadButton)
        self.bottomLayout.addWidget(stopButton)
        self.bottomLayout.addWidget(beginButton)

        self.mainLayout.addWidget(self.fileLabel, 1, 0)
        self.mainLayout.addWidget(self.text, 2, 0)
        self.mainLayout.addLayout(self.bottomLayout, 3, 0)
        self.setLayout(self.mainLayout)

        self.loadButton.clicked.connect(self.load_file)
        stopButton.clicked.connect(self.stop_event)
        beginButton.clicked.connect(self.begin_event)

    def load_file(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '')
        if sum(filename.endswith(i) for i in ['.csv']):  # , '.xls', '.xlsx']):
            self.fileLabel.setText(filename)
            self.user_list = csv_processing(filename)
            self.tableWidget = MainTable(self.user_list)
            self.mainLayout.addWidget(self.tableWidget, 2, 0)
            # self.loadButton.setEnabled(False)

        else:
            QtGui.QMessageBox.question(self, 'Message',
                                       u"目前仅支持.csv文件!",
                                       QtGui.QMessageBox.Yes)

    def setTableItem(self, workThread, threadNum):
        self.picLabel = PicLabel(workThread)
        self.captchaLineEdit = EnterLineEdit(self.picLabel)
        self.tableWidget.setCellWidget(threadNum, 3, self.picLabel)
        self.tableWidget.setCellWidget(threadNum, 4, self.captchaLineEdit)

    def showInfo(self, s):
        info, threadNum = s
        exec('self.tableWidget.item%s2.setText(self.tr(info))' % threadNum)

    def begin_event(self):
        options = showOption()
        uu = options.get('uuPlatform', None)
        uuUser = options.get('uuUser', None)
        uuPasswd = options.get('uuPasswd', None)
        if hasattr(self, 'user_list'):
            self.threadsList = []
            if uu:
                for i, userInfo in enumerate(self.user_list):
                    t = UuWorker(userInfo, i, uuUser, uuPasswd)
                    t.dangDangXiaDan.c.sig.connect(self.showInfo)
                    t.start()
                    setattr(self, 'thread%s' % str(i + 1), t)
                    self.threadsList.append(t)
            else:
                for i, userInfo in enumerate(self.user_list):
                    t = Worker(userInfo, i)
                    self.setTableItem(t, i)
                    t.dangDangXiaDan.c.sig.connect(self.showInfo)
                    t.start()
                    setattr(self, 'thread%s' % str(i + 1), t)
                    self.threadsList.append(t)
        else:
            QtGui.QMessageBox.question(self, 'Message',
                                       u"请确认已导入订单信息!",
                                       QtGui.QMessageBox.Yes)

    def stop_event(self):
        event.clear()


class MainTable(QtGui.QTableWidget):

    def __init__(self, argList, parent=None):
        super(MainTable, self).__init__(parent)
        self.setFont(QtGui.QFont("Courier New", 10))
        self.setRowCount(len(argList))
        titleList = [u'帐号', u'选中', u'运行日志', u'验证码',
                     u'输入验证码', u'密码', u'支付密码', u'商品编号',
                     u'购买数量', u'省', u'市', u'县/区',
                     u'街道', u'详细地址', u'邮编', u'收货人',
                     u'手机号码']
        self.setColumnCount(len(titleList))
        self.setHorizontalHeaderLabels(titleList)
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, 250)

        for count, arg in enumerate(argList):
            self.setRowHeight(count, 35)
            for col in range(len(titleList)):
                item = QtGui.QTableWidgetItem()
                self.setItem(count, col, item)
                setattr(self, 'item%s%s' % (count, col), item)
                if col == 1:
                    item.setCheckState(QtCore.Qt.Checked)
                elif isinstance(arg[col], list):
                    item.setText(*arg[col])
                else:
                    item.setText(self.tr(arg[col]))
        self.show()


class PicLabel(QtGui.QLabel):
    '''
    验证码控件，
    点击事件将触发信号，发送信号给主tab界面(Automation)

    待优化事件
    dangDangWoreker,为了建立图片触发事件之间的关联
    '''
    def __init__(self, dangDangWorker, parent=None):
        super(PicLabel, self).__init__(parent)
        self.dangDangWorker = dangDangWorker
        self.dangDangThread = dangDangWorker.dangDangXiaDan
        # 生成验证码图片并将图片放入QLabel控件
        self.showPic()

    def showPic(self):
        # 下载验证码图片
        self.dangDangThread.download_captcha()
        pix = QtGui.QPixmap(self.dangDangThread.imgfile)
        self.setPixmap(pix)
        self.dangDangThread.browser.save_screenshot('jj.jpg')
        print self.dangDangThread.imgfile
        # self.resize(90, 50)

    def mousePressEvent(self, event):
        self.showPic()


class EnterLineEdit(QtGui.QLineEdit):
    '''
    验证码输入框控件

    待优化事件
    验证完成时，tab跳转至下一个输入框
    piclabel，建立触发事件关联
    '''
    def __init__(self, piclabel, parent=None):
        super(EnterLineEdit, self).__init__(parent)
        # self.setFixedSize(100, 40)
        # 为输入框添加一个事件过滤器
        self.installEventFilter(self)
        self.piclabel = piclabel
        self.dangDangThread = piclabel.dangDangThread

    def keyPressEvent(self, e):
        '''
        监听键盘事件，
        判断回车事件传回验证码，并反馈
        '''
        # 16777220 为键盘enter事件触发返回的event.key()的值
        if e.key() == 16777220:
            captcha = self.text()
            if len([i for i in captcha if i in string.letters]) == 4:

                if self.dangDangThread.checkCaptcha(captcha):
                    self.setEnabled(False)
                    self.piclabel.setEnabled(False)
                    self.piclabel.setFrameStyle(QtGui.QFrame.Panel |
                                                QtGui.QFrame.Sunken)
                    self.piclabel.setText(u'Done!')
                    self.setText(u'完成！')
                    self.piclabel.dangDangWorker.s.sig.emit()
                else:
                    self.piclabel.setEnabled(True)
                    self.piclabel.showPic()
                    self.clear()
                    self.setText(u"错误的验证码")
                    self.selectAll()
            else:
                self.setText(u"错误的验证码")
                self.selectAll()
        else:
            QtGui.QLineEdit.keyPressEvent(self, e)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn:
            if self.text().strip() in [u'请输入验证码', u'错误的验证码']:
                self.clear()
        elif event.type() == QtCore.QEvent.FocusOut:
            if self.text().strip() == '':
                self.setText(u"请输入验证码")
                self.selectAll()
        return False


class Worker(QtCore.QThread):

    def __init__(self, userInfo, threadNum):
        super(Worker, self).__init__()
        self.flags = True
        self.dangDangXiaDan = DangDangXiaDan(userInfo, threadNum)
        self.s = Communicate()

    def setFlags(self):
        self.flags = False

    def run(self):
        self.s.sig.connect(self.setFlags)
        while self.flags:
            time.sleep(1)
        self.dangDangXiaDan.shopping()


class UuWorker(QtCore.QThread):

    def __init__(self, userInfo, threadNum, uuUser, uuPasswd):
        super(UuWorker, self).__init__()
        self.uuUser = uuUser
        self.uuPasswd = uuPasswd
        self.dangDangXiaDan = DangDangXiaDan(userInfo, threadNum)

    def run(self):
        self.dangDangXiaDan.automationShopping(self.uuUser, self.uuPasswd)

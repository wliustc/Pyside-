#!/usr/bin/env python
# @Date    : 2016-06-08 11:04:02
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import sys
import string
import time
from PySide import QtGui
from PySide import QtCore
from config import *
import threading
from dangdang import DangDangXiaDan, inventory
from sysOption import showOption
# 重载sys时,偶尔会丢失标准输出，标准输入等，所以最好提前赋值
stdi, stdo, stde = sys.stdin, sys.stdout, sys.stderr
reload(sys)
sys.stdin, sys.stdout, sys.stderr = stdi, stdo, stde
# 重置系统编码格式为UTF8
sys.setdefaultencoding('utf8')

# 设置全局的slef.tr的字符串编码为utf8
QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf8"))

options = {}


class Communicate(QtCore.QObject):
    # 收发无参数信号
    sig = QtCore.Signal(str)


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
    '''
    自动化下单主界面
    '''
    def __init__(self, parent=None):
        super(Automation, self).__init__(parent)
        # 设置界面布局
        self.mainLayout = QtGui.QGridLayout(self)
        self.bottomLayout = QtGui.QHBoxLayout()
        self.text = QtGui.QTextBrowser()
        self.fileLabel = QtGui.QLabel(self.tr(''))

        # 建立按钮
        self.loadButton = QtGui.QPushButton(self.tr("导入文件"))
        beginButton = QtGui.QPushButton(self.tr("开始任务"))
        stopButton = QtGui.QPushButton(self.tr("暂停"))

        # 加入弹簧，设置按钮布局
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.loadButton)
        self.bottomLayout.addWidget(stopButton)
        self.bottomLayout.addWidget(beginButton)

        # 设置主界面布局
        self.mainLayout.addWidget(self.fileLabel, 1, 0)
        self.mainLayout.addWidget(self.text, 2, 0)
        self.mainLayout.addLayout(self.bottomLayout, 3, 0)
        self.setLayout(self.mainLayout)

        # 关联按钮事件
        self.loadButton.clicked.connect(self.load_file)
        stopButton.clicked.connect(self.stop_event)
        beginButton.clicked.connect(self.begin_event)

        self.c = Communicate()

    def load_file(self):
        '''
        读取文件
        '''
        filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '')
        if sum(filename.endswith(i) for i in ['.csv', '']):  # , '.xls', '.xlsx']):
            self.fileLabel.setText(filename)
            self.input_list = csv_processing(filename)
            self.tableWidget = MainTable(self.input_list)
            self.mainLayout.addWidget(self.tableWidget, 2, 0)
            # self.loadButton.setEnabled(False)

        else:
            QtGui.QMessageBox.question(self, 'Message',
                                       u"目前仅支持.csv文件!",
                                       QtGui.QMessageBox.Yes)

    def setTableItem(self, workThread, threadNum):
        '''
        按线程ID为规定行初始化验证码图片
        '''
        self.picLabel = PicLabel(workThread)
        self.captchaLineEdit = EnterLineEdit(self.picLabel)
        self.tableWidget.setCellWidget(threadNum, 3, self.picLabel)
        self.tableWidget.setCellWidget(threadNum, 4, self.captchaLineEdit)

    def showInfo(self, s):
        '''
        按线程ID为规定行输入日志信息
        '''
        info, threadNum = s
        self.tableWidget.setItem(threadNum, 2,
                                 QtGui.QTableWidgetItem(unicode(info)))

    def getNewThread(self, finishedNum):
        '''
        uu
        根据已完成线程ID，
        按勾选事件返回顺序，
        开启下一个线程
        '''
        item = getattr(self.tableWidget, 'item%s1' % finishedNum)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.count += 1
        if self.count < len(self.user_list):
            userInfo = self.user_list[self.count]
            t = UuWorker(self.c, *userInfo, **options)
            t.dangDangXiaDan.c.sig.connect(self.showInfo)
            t.setDaemon(True)
            t.start()
            setattr(self, 'thread%s' % str(self.count + 1), t)
            self.threadsList.append(t)

    def getNew(self, finishedNum):
        '''
        开启下一个线程
        '''
        item = getattr(self.tableWidget, 'item%s1' % finishedNum)
        item.setCheckState(QtCore.Qt.Unchecked)
        self.count += 1
        if self.count < len(self.user_list):
            userInfo = self.user_list[self.count]
            t = Worker(self.c, *userInfo, **options)
            self.setTableItem(t, userInfo[0])
            t.dangDangXiaDan.c.sig.connect(self.showInfo)
            t.setDaemon(True)
            t.start()
            setattr(self, 'thread%s' % str(self.count + 1), t)
            self.threadsList.append(t)

    def getRow(self, row):
        '''
        读取tablewidget内规定行的数据
        '''
        return [getattr(self.tableWidget, 'item%s%s' % (row, column)).text()
                for column, _ in enumerate(self.tableWidget.titleList)]

    def begin_event(self):
        global options
        options = showOption()
        uu = options.get('uuPlatform', None)
        maxThread = int(options.get('maxThreadCount', 1))

        columnItem = [getattr(self.tableWidget, 'item%s1' % row)
                      for row, _ in enumerate(self.input_list)]
        self.user_list = [(index, self.getRow(index))
                          for index, b in enumerate(columnItem)
                          if b.checkState() == QtCore.Qt.Checked]

        preTotalBook = [zip(b[7].split(';'), b[8].split(';'))
                        for a, b in self.user_list]
        preTotalBook = reduce(lambda x, y: x + y, preTotalBook)
        bookIDs = set(name for name, q in preTotalBook)
        totalBookList = [(i, sum(int(q)
                                 for name, q in preTotalBook if name == i))
                         for i in bookIDs]

        errorBooks = []
        for bookid, quantity_want_to_buy in totalBookList:
            bookname, q = inventory(bookid)
            if q < quantity_want_to_buy:
                errorBooks.append((bookname, bookid, quantity_want_to_buy, q))
        if errorBooks:
            temp = u'商品:%s,(ID:%s),\n本次订单预购%s, 库存数量%s,无法完成该订单'
            warnnings = '\n\n'.join(temp % i for i in errorBooks)

            QtGui.QMessageBox.question(self, 'Message',
                                       warnnings,
                                       QtGui.QMessageBox.Yes)
            # QtGui.QMessageBox.No,
            # QtGui.QMessageBox.No)
            return
            # 检验用户返回，并返回对应的结果
            # if reply != QtGui.QMessageBox.Yes:
            #     return

        if hasattr(self, 'user_list'):
            if u'请选择' not in options.values():
                self.threadsList = []
                if uu:
                    self.c.sig.connect(self.getNewThread)
                    for i, userInfo in enumerate(self.user_list[:maxThread]):
                        self.t = UuWorker(self.c, *userInfo, **options)
                        self.t.dangDangXiaDan.c.sig.connect(self.showInfo)
                        self.t.setDaemon(True)
                        self.t.start()
                        setattr(self, 'thread%s' % str(i + 1), self.t)
                        self.threadsList.append(self.t)
                        self.count = i

                else:
                    global flags
                    flags = [True] * len(self.input_list)
                    self.c.sig.connect(self.getNew)
                    for i, userInfo in enumerate(self.user_list[:maxThread]):
                        self.t = Worker(self.c, *userInfo, **options)
                        self.setTableItem(self.t, userInfo[0])
                        self.t.dangDangXiaDan.c.sig.connect(self.showInfo)
                        self.t.setDaemon(True)
                        self.t.start()
                        setattr(self, 'thread%s' % str(i + 1), self.t)
                        self.threadsList.append(self.t)
                        self.count = i
            else:
                QtGui.QMessageBox.question(self, 'Message',
                                           u"请确认系统设置是否配置完全!",
                                           QtGui.QMessageBox.Yes)
        else:
            QtGui.QMessageBox.question(self, 'Message',
                                       u"请确认已导入订单信息!",
                                       QtGui.QMessageBox.Yes)

    def stop_event(self):
        if hasattr(self, 'threadsList'):
            [t.dangDangXiaDan.browser.close()
             for t in self.threadsList
                if t.isAlive()]
            for i, userInfo in enumerate(self.user_list):
                exec('self.tableWidget.item%s2.setText(self.tr(%s))'
                     % (i, "'任务已被用户终止...'"))


class MainTable(QtGui.QTableWidget):

    def __init__(self, argList, parent=None):
        super(MainTable, self).__init__(parent)
        self.setFont(QtGui.QFont("Courier New", 10))
        self.setRowCount(len(argList))
        self.titleList = [u'帐号', u'选中', u'运行日志', u'验证码',
                          u'输入验证码', u'密码', u'支付密码', u'商品编号',
                          u'购买数量', u'省', u'市', u'县/区',
                          u'街道', u'详细地址', u'邮编', u'收货人',
                          u'手机号码']
        self.setColumnCount(len(self.titleList))
        self.setHorizontalHeaderLabels(self.titleList)
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, 250)

        for count, arg in enumerate(argList):
            self.setRowHeight(count, 35)
            for col in range(len(self.titleList)):
                item = QtGui.QTableWidgetItem()
                self.setItem(count, col, item)
                if col == 1:
                    item.setCheckState(QtCore.Qt.Checked)
                elif isinstance(arg[col], list):
                    item.setText(';'.join(arg[col]))
                else:
                    item.setText(self.tr(arg[col]))
                    # item.setFlags(~QtCore.Qt.ItemIsEditable)
                setattr(self, 'item%s%s' % (count, col), item)


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
                    self.setFocus()
                    global flags
                    flags[self.dangDangThread.threadNum] = False
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


class Worker(threading.Thread):

    def __init__(self, c, threadNum, userInfo, **kw):
        super(Worker, self).__init__()
        self.c = c
        self.isFinished = False
        self.threadNum = threadNum
        self.dangDangXiaDan = DangDangXiaDan(userInfo, threadNum, **kw)

    def run(self):
        while flags[self.threadNum]:
            time.sleep(1)
        self.dangDangXiaDan.shopping(self.c)
        self.isFinished = True


class UuWorker(threading.Thread):

    def __init__(self, c, threadNum, userInfo, **kw):
        super(UuWorker, self).__init__()
        self.c = c
        self.isFinished = False
        self.dangDangXiaDan = DangDangXiaDan(userInfo, threadNum, **kw)

    def run(self):
        self.dangDangXiaDan.automationShopping(self.c)
        self.isFinished = True

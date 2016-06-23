#!/usr/bin/env python
# @Date    : 2016-06-08 13:07:08
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import json
import os
import sys
from PySide import QtGui
from PySide import QtCore
from config import *

# 判断配置文件是否存在，如果没有新建一个
# 建立一个本地配置文件，持久化存储用户偏好设置
if not os.path.exists(userSettingDate):
    with open(userSettingDate, 'w') as f:
        json.dump({'uuPlatform': False,
                   'uuUser': '',
                   'uuPasswd': '',
                   'maxThreadCount': '1',
                   'invoiceTitleInfo': '',
                   'deliveryMthods': u'请选择',
                   'payMethods': u'请选择',
                   'invoiceTitle': u'请选择',
                   'invoice': u'请选择',
                   'promoCode': '',
                   'coupon': '',
                   'cancelItem': '',
                   }, f)


def setUpDate(newOption):
    '''
    更新存储配置文件
    josn为本地明文存储数据，如果要密文，可简单改为pickle模块存储
    josn优点跨语言可支持性高
    pickle简单的加密甚至支持存储类的实例，缺点:仅支持python
    '''
    with open(userSettingDate, 'rb') as rf:
        oldDate = json.load(rf)
    with open(userSettingDate, 'wb') as f:
        oldDate.update(newOption)
        json.dump(oldDate, f)


def showOption():
    '''
    获取配置文件数据
    '''
    with open(userSettingDate) as f:
        date = json.load(f)
        return date


class ThreadOption(QtGui.QWidget):

    '''
    线程设置界面
    '''

    def __init__(self, parent=None):
        super(ThreadOption, self).__init__(parent)
        # 配置线程数量
        threadLayout = QtGui.QGridLayout(self)
        self.maxThreadLabel = QtGui.QLabel(u'线程数量:')
        self.maxThreadEdit = QtGui.QLineEdit()
        self.tipsThreadLabel = QtGui.QLabel(u'(默认为1)')

        # 线程部件布局
        threadLayout.addWidget(self.maxThreadLabel, 0, 0)
        threadLayout.addWidget(self.maxThreadEdit, 0, 1)
        threadLayout.addWidget(self.tipsThreadLabel, 0, 2)


class PromotionOption(QtGui.QWidget):

    '''
    优惠配置
    '''

    def __init__(self, parent=None):
        super(PromotionOption, self).__init__(parent)
        promotionLayout = QtGui.QGridLayout(self)
        # 设置优惠选项
        self.cancelLabel = QtGui.QLabel(u'取消预购:')
        self.cancelEdit = QtGui.QLineEdit()
        self.promoCodeLabel = QtGui.QLabel(u'优惠码:')
        self.promoCodeEdit = QtGui.QLineEdit()
        self.couponLabel = QtGui.QLabel(u'礼券关键字:')
        self.couponEdit = QtGui.QLineEdit()
        self.couponTips = QtGui.QLabel(
            u'建议:如果没有礼券请勿填写，可以填100,200等')

        # 优惠部件布局
        promotionLayout.addWidget(self.cancelLabel, 0, 0)
        promotionLayout.addWidget(self.cancelEdit, 0, 1)
        promotionLayout.addWidget(self.promoCodeLabel, 1, 0)
        promotionLayout.addWidget(self.promoCodeEdit, 1, 1)
        promotionLayout.addWidget(self.couponLabel, 2, 0)
        promotionLayout.addWidget(self.couponEdit, 2, 1)
        promotionLayout.addWidget(self.couponTips, 3, 1)


class CaptchaOption(QtGui.QWidget):

    '''
    验证码平台账号密码设置
    '''

    def __init__(self, parent=None):
        super(CaptchaOption, self).__init__(parent)
        captchaLayout = QtGui.QGridLayout(self)
        # 验证码选项
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

        # 验证码部件布局
        captchaLayout.addWidget(self.platformLabel, 0, 0)
        captchaLayout.addWidget(self.platformBox, 0, 1)
        captchaLayout.addWidget(self.uuuser, 1, 0)
        captchaLayout.addWidget(self.userLineEdit, 1, 1)
        captchaLayout.addWidget(self.uupasswd, 2, 0)
        captchaLayout.addWidget(self.passwdLineEdit, 2, 1)
        captchaLayout.addWidget(self.checkBox, 3, 1)


class PayOption(QtGui.QWidget):

    '''
    结算偏好设置
    '''

    def __init__(self, parent=None):
        super(PayOption, self).__init__(parent)
        payLayout = QtGui.QGridLayout(self)
        # 送货方式选项
        self.payLabel = QtGui.QLabel(u'送货方式:')
        self.payBox = QtGui.QComboBox()
        self.deliveryMthods = [u'请选择', u'时间不限 ', u'只工作日送货 ', u'只双休日、假日送货 ']
        [self.payBox.addItem(i) for i in self.deliveryMthods]

        # 支付方式选项
        self.payMethodsLabel = QtGui.QLabel(u'支付方式:')
        self.payMethodsBox = QtGui.QComboBox()
        self.payMethods = [u'请选择', u'网上支付', u'货到付款-支付宝扫码支付',
                           u'货到付款-现金', u'货到付款-POS机刷卡',
                           u'银行转帐', u'他人代付']
        [self.payMethodsBox.addItem(i) for i in self.payMethods]

        # 发票类型选项
        self.invoiceTitleLabel = QtGui.QLabel(u'发票抬头:')
        self.invoiceTitleBox = QtGui.QComboBox()
        self.invoiceTitles = [u'请选择', u'个人', u'单位']
        [self.invoiceTitleBox.addItem(i) for i in self.invoiceTitles]
        self.invoiceTitleLineEdit = QtGui.QLineEdit()

        self.invoiceLabel = QtGui.QLabel(u'发票内容:')
        self.invoiceBox = QtGui.QComboBox()
        self.invoice = [u'请选择', u'图书', u'资料', u'办公用品']
        [self.invoiceBox.addItem(i) for i in self.invoice]

        # 结算部件布局
        payLayout.addWidget(self.payLabel, 0, 0)
        payLayout.addWidget(self.payBox, 0, 1)
        payLayout.addWidget(self.payMethodsLabel, 1, 0)
        payLayout.addWidget(self.payMethodsBox, 1, 1)
        payLayout.addWidget(self.invoiceTitleLabel, 2, 0)
        payLayout.addWidget(self.invoiceTitleBox, 2, 1)
        payLayout.addWidget(self.invoiceTitleLineEdit, 3, 1)
        payLayout.addWidget(self.invoiceLabel, 4, 0)
        payLayout.addWidget(self.invoiceBox, 4, 1)


class SysOption(QtGui.QWidget):

    '''
    系统设置主界面
    '''

    def __init__(self, parent=None):
        super(SysOption, self).__init__(parent)
        mainLayout = QtGui.QGridLayout(self)

        # 验证码部件
        capInfo = QtGui.QSplitter()
        self.captcha = CaptchaOption(capInfo)
        # 设置边框
        capInfo.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)

        # 线程部件
        threadInfo = QtGui.QSplitter()
        self.threadOpt = ThreadOption(threadInfo)
        threadInfo.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)

        # 结算部件
        payInfo = QtGui.QSplitter()
        self.payOpt = PayOption(payInfo)
        payInfo.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)

        # 优惠部件
        promotionInfo = QtGui.QSplitter()
        self.promotionOpt = PromotionOption(promotionInfo)
        promotionInfo.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)

        # 按钮部件
        buttonLayout = QtGui.QHBoxLayout()
        changeButton = QtGui.QPushButton(u"修改")
        saveButton = QtGui.QPushButton(u'保存设置')
        # 添加弹簧
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(changeButton)
        buttonLayout.addWidget(saveButton)

        # 主界面布局
        mainLayout.addWidget(payInfo, 0, 0)
        mainLayout.addWidget(threadInfo, 0, 1)
        mainLayout.addWidget(capInfo, 1, 1)
        mainLayout.addWidget(promotionInfo, 1, 0)
        mainLayout.addLayout(buttonLayout, 2, 1)

        # 建立按钮链接
        saveButton.clicked.connect(self.saveOption)
        changeButton.clicked.connect(self.setEditorsEnable)

        # 勾选部件列表
        self.checkBoxList = [('uuPlatform', self.captcha.checkBox)]

        # 下拉框部件列表
        self.ComboBoxList = [('UuplatformBox', self.captcha.platformBox),
                             ('deliveryMthods', self.payOpt.payBox),
                             ('payMethods', self.payOpt.payMethodsBox),
                             ('invoiceTitle', self.payOpt.invoiceTitleBox),
                             ('invoice', self.payOpt.invoiceBox)]

        # 输入框部件列表
        self.editList = [('uuUser', self.captcha.userLineEdit),
                         ('uuPasswd', self.captcha.passwdLineEdit),
                         ('maxThreadCount', self.threadOpt.maxThreadEdit),
                         ('invoiceTitleInfo', self.payOpt.invoiceTitleLineEdit),
                         ('promoCode', self.promotionOpt.promoCodeEdit),
                         ('coupon', self.promotionOpt.couponEdit),
                         ('cancelItem', self.promotionOpt.cancelEdit),
                         ]

        # 初始化上一次用户设置
        self.initializtion()

    def initializtion(self):
        '''
        还原用户最后一次保存的选项
        '''
        # 设置初始化项目为不允许修改
        self.setEditorsEnable(False)
        # 读取本地存储数据
        oldOption = showOption()
        # 填写输入框
        [edit.setText(unicode(oldOption[kw])) for kw, edit in self.editList]
        # 勾选
        [chcekBox.setCheckState(QtCore.Qt.Checked)
            for kw, chcekBox in self.checkBoxList if oldOption[kw]]
        # 选择下拉框
        self.payOpt.payBox.setCurrentIndex(self.payOpt.deliveryMthods.index(oldOption['deliveryMthods']))
        self.payOpt.payMethodsBox.setCurrentIndex(self.payOpt.payMethods.index(oldOption['payMethods']))
        self.payOpt.invoiceTitleBox.setCurrentIndex(self.payOpt.invoiceTitles.index(oldOption['invoiceTitle']))
        self.payOpt.invoiceBox.setCurrentIndex(self.payOpt.invoice.index(oldOption['invoice']))

    def setEditorsEnable(self, bo=True):
        '''
        设置所有部件是否可用，
        默认可用
        '''
        [edit.setEnabled(bo) for kw, edit in self.editList + self.checkBoxList + self.ComboBoxList]

    def saveOption(self):
        '''
        保存系统设置到本地文件
        '''
        # 读取输入框信息
        setNewText = {kw: edit.text() for kw, edit in self.editList}
        # 读取勾选框信息
        setNewCheck = {kw: check.checkState() == QtCore.Qt.Checked
                       for kw, check in self.checkBoxList}
        # 读取下拉框信息
        setNewCombo = {kw: combo.currentText()
                       for kw, combo in self.ComboBoxList}
        # 设置所有部件不可用
        self.setEditorsEnable(False)
        setNewCheck.update(setNewText)
        setNewCheck.update(setNewCombo)
        # 存储设置
        setUpDate(setNewCheck)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = SysOption()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

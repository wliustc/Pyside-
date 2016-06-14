#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-08 11:23:36
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import re
import time
import requests
from bs4 import BeautifulSoup
from PIL import Image
from PySide import QtCore
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from config import *
from uu_captcha import Ucode
# 为phantom添加headers信息
dcap = DesiredCapabilities.PHANTOMJS
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) firefox/15.0.87"
)


def inventory(id):

    pre_id = '1468491271'
    url = '''http://shopping.dangdang.com/shoppingcart/cart_append_new?product_ids=%7B%22product%22%3A%5B%7B%22productId%22%3A%221468491271%22%2C%22productCount%22%3A%221000000%22%2C%22promotion%22%3A%5B%5D%7D%5D%2C%22referer%22%3A%22http%3A//product.dangdang.com/1468491271.html%22%2C%22prev_referer%22%3A%22http%3A//shopping.dangdang.com/shoppingcart/shopping_cart.aspx%3Fproduct_ids%3D0%26referer%3Dhttp%3A//shopping.dangdang.com/shoppingcart/cart_append_new%3Fproduct_ids%3D%257B%2522product%2522%253A%255B%257B%2522productId%2522%253A%25221468491271%2522%252C%2522productCount%2522%253A%25229999%2522%252C%2522promotion%2522%253A%255B%255D%257D%255D%252C%2522referer%2522%253A%2522http%253A//product.dangdang.com/1468491271.html%2522%252C%2522prev_referer%2522%253A%2522http%253A//book.dangdang.com/%2522%257D%22%7D#http://product.dangdang.com/product.aspx?product_id=1468491271'''

    url = url.replace(pre_id, str(id))
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    l = soup.find('span', {'class': 'gift_lack_detail'})
    quantity = re.findall('\d+', l.text)[0]
    title = soup.find('span', {'class': 'gift_lack_name'}).text.strip('\n')
    return title, int(quantity)


class FSig(QtCore.QObject):
    # 建立一个signal类用于收发list类信号
    sig = QtCore.Signal(list)

    def __init__(self):
        QtCore.QObject.__init__(self)


class DangDangXiaDan(object):

    def __init__(self, userInfo, threadNum, **options):
        self.loginUrl = 'https://login.dangdang.com/signin.php'
        self.addressUrl = 'http://customer.dangdang.com/myaddress/myaddress.php'
        profile = FirefoxBinary('/home/never/下载/firefox/firefox')
        self.browser = webdriver.Firefox(firefox_binary=profile)
        # self.browser = webdriver.PhantomJS(executable_path=phantomjs_path,
        #                                    desired_capabilities=dcap)
        self.browser.get(self.loginUrl)
        self.browser.maximize_window()
        self.options = options
        self.username = userInfo[0]
        self.password = userInfo[5]
        self.booklist = zip(userInfo[7], userInfo[8])
        address = {'name': userInfo[15],
                   'pro': userInfo[9],
                   'city': userInfo[10],
                   'town': userInfo[11],
                   'addr_detail': userInfo[13],
                   'postcode': userInfo[14],
                   'phone': userInfo[16]}
        self.address = {x: unicode(y) for x, y in address.items()}
        self.c = FSig()
        self.threadNum = threadNum
        self.imgfile = imgfile % threadNum

    def myprint(self, info):
        print info
        self.c.sig.emit([info.encode('utf8'), self.threadNum])

    def _switch_new_window(self):
        self.windows = self.browser.window_handles
        self.browser.switch_to.window(self.windows[-1])
        time.sleep(1)
        self.myprint('Now we are at %s' % self.browser.title.encode(
            'utf8'))

    # 下载验证码到本地
    def download_captcha(self):
        try:
            self.browser.find_element_by_id("J_loginMaskClose").click()
        except:
            if self.browser.current_url != self.loginUrl:
                return
        element = self.browser.find_element_by_id('imgVcode')
        element.click()
        location = element.location
        size = element.size
        self.browser.save_screenshot('1.jpg')
        self.browser.save_screenshot(self.imgfile)
        im = Image.open(self.imgfile)
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = im.crop((left, top, right, bottom))  # 870, 328, 956, 366
        im.save(self.imgfile)  # saves new cropped image

    def login(self):
        # self.browser.get(self.loginUrl)
        try:
            self.browser.find_element_by_id("J_loginMaskClose").click()
        except:
            pass
        self.download_captcha()
        username_input = self.browser.find_element_by_id("txtUsername")
        username_input.clear()
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("txtPassword")
        password_input.clear()
        password_input.send_keys(self.password)
        ucode = Ucode(self.options['uuUser'], self.options['uuPasswd'])
        captcha = ucode.uu_captcha(self.imgfile)
        if captcha:
            print 'captcha:', captcha
            self.browser.find_element_by_id(
                'codeReplacer').send_keys(captcha)
            self.browser.find_element_by_id("submitLoginBtn").click()
        time.sleep(1)
        try:
            self.browser.find_element_by_id("txtUsername")
            self.myprint(u'登陆失败,正在返回失败验证码...失败原因 %s' % ucode.fail_requests())
            return False
        except:
            self.myprint(u'login successfully')
            time.sleep(2)
            return True

        self.myprint(u'帐号:%s, login fail...' % self.username)

    def checkCaptcha(self, captcha):
        username_input = self.browser.find_element_by_id("txtUsername")
        username_input.clear()
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("txtPassword")
        password_input.clear()
        password_input.send_keys(self.password)
        self.browser.find_element_by_id(
            'codeReplacer').send_keys(captcha)
        self.browser.find_element_by_id("submitLoginBtn").click()
        time.sleep(2)
        if self.browser.current_url == self.loginUrl:
            self.myprint(u'login failed...')
            return False
        else:
            self.myprint(u'login successfully')
            return True

    def add_address(self):
        self.browser.get(self.addressUrl)
        time.sleep(1)
        try:
            old_address_txt = self.browser.find_element_by_class_name(
                'address_text').text
            old_address_list = old_address_txt.split(',')
            new_address_list = [self.address['name'], u' 中国',
                                ' ' + self.address['pro'],
                                ' ' + self.address['city'],
                                ' ' + self.address['town'],
                                ' ' + '*' * 4 +
                                self.address['addr_detail'][4:],
                                ' ' + self.address['postcode'],
                                ' ' + self.address['phone'][:3] + '*' * 4 + self.address['phone'][7:]]
        except:
            old_address_list, new_address_list = [], None
        if old_address_list != new_address_list:
            try:
                self.browser.find_element_by_name('button_delete').click()
                self.browser.find_element_by_class_name('b_yes').click()
                self.myprint(u'已删除多余的默认地址')
            except:
                self.myprint(u'没有要删除的多余地址')
            self.myprint(u'正在填写收件人信息...')
            self.browser.find_element_by_id(
                'ship_man').send_keys(self.address['name'])
            self.myprint(u'正在填写收件人地址...')
            Select(self.browser.find_element_by_id('province_id')
                   ).select_by_visible_text(self.address['pro'])
            time.sleep(2)
            Select(self.browser.find_element_by_id('city_id')
                   ).select_by_visible_text(self.address['city'])
            Select(self.browser.find_element_by_id('town_id')
                   ).select_by_visible_text(self.address['town'])
            self.browser.find_element_by_id(
                'addr_detail').send_keys(self.address['addr_detail'])
            self.browser.find_element_by_id('ship_zip').send_keys(
                self.address['postcode'])
            self.browser.find_element_by_id('ship_mb').send_keys(
                self.address['phone'])
            self.myprint(u'正在将地址设置为默认地址...')
            self.browser.find_element_by_id('default_flg').click()
            self.myprint(u'提交地址信息...')
            self.browser.find_element_by_xpath(
                '//*[@id="myaddress"]/div/p[7]/button').click()
        else:
            self.myprint(u'没有要删除的多余地址')

    def empty_shopping_list(self):
        self.myprint(u'正在清理购物车...')
        # empty shoppinglist if you have
        self.browser.find_element_by_name(u'购物车').click()
        self._switch_new_window()
        try:
            self.browser.find_element_by_class_name(
                'checknow fn-checkall').click()
        except:
            pass
        try:
            self.browser.find_element_by_css_selector(
                'a#j_removeproducts.fn-batch-remove').click()
            self.browser.find_element_by_css_selector(
                'a.pop_btn.fn-confirm-batchremovebox').click()
        except:
            self.myprint(u'未检索到需要清理的项目...')
        self.browser.close()
        self.browser.switch_to.window(self.windows[0])
        self.myprint(u'已清空之前的购物车'.encode('utf8'))

    def search_books(self, book_id, number, min_price=0, limited_price=1000):
        book_url = 'http://product.dangdang.com/%s.html' % book_id
        self.myprint(u'正在检索书目%s...' % book_id)
        self.browser.get(book_url)
        # temp = self.browser.find_element_by_class_name('name_info')
        # kw = temp.find_element_by_tag_name('h1').get_attribute('title')
        self.myprint(u'正在修改购买数量...')
        num = self.browser.find_element_by_id('buy_num')
        num.clear()
        num.send_keys(number)
        num.send_keys(Keys.ENTER)
        self.browser.find_element_by_id('part_buy_button').click()
        # self.myprint(u'帐号:%s, 已检索到%s, 加入购物车 %s 本' % (self.username, kw, number))
        self.myprint(u'帐号:%s, 已检索到%s, 加入购物车 %s 本' % (self.username, book_id, number))

    def pay(self):
        self.myprint(u'开始支付...')
        self.browser.find_element_by_name(u'购物车').click()
        self.browser.find_element_by_id('checkout_btn').click()
        try:
            self.browser.find_element_by_id('ck_link').click()
        except:
            pass
        try:
            Select(self.browser.find_element_by_id('sel_ship_time_1_0_0')
                   ).select_by_visible_text(self.options['deliveryMthods'])
            self.browser.find_element_by_id('btn_shipment_save_0_0').click()
            self.browser.find_element_by_id(
                'rd_pay_id_0_0').find_element_by_id(paydict[self.options['payMethods']]).click()
            self.browser.find_element_by_id('btn_payment_save_0_0').click()
            self.browser.find_element_by_id(invoicedict[self.options['invoiceTitle']]).click()
            Select(self.browser.find_element_by_id('invoice_content_0_0')
                   ).select_by_visible_text(self.options['invoice'])
            self.browser.find_element_by_id('invoice_submit_0_0')
        except:
            pass
        self.browser.find_element_by_id('submit').click()
        time.sleep(2)
        self.browser.close()
        self.myprint(u'帐号:%s, 完成订单' % self.name)

    def shopping(self, c):
        self.add_address()
        self.empty_shopping_list()
        for i in self.booklist:
            self.search_books(*i)
        self.empty_shopping_list()
        # self.pay()
        self.browser.close()
        c.sig.emit(str(self.threadNum))

    def automationShopping(self, c):
        if self.login():
            self.add_address()
            self.empty_shopping_list()
            for i in self.booklist:
                self.search_books(*i)
            self.empty_shopping_list()
        self.browser.close()
        c.sig.emit(str(self.threadNum))

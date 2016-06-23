#!/usr/bin/env python
# @Date    : 2016-06-20 11:56:30
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)
import re
import time
import requests
import random
from bs4 import BeautifulSoup
from PIL import Image
from PySide import QtCore
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from config import *
from uu_captcha import Ucode
from cid import cid
# 为phantom添加headers信息
dcap = DesiredCapabilities.PHANTOMJS
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) firefox/15.0.87"
)


def inventory(id):
    '''
    检测商品实时库存，
    用于校验订单数量与商品存量
    '''
    # 发送url请求直接校验商品库存，
    # 通过正则匹配存量信息
    baseurl = ('http://shopping.dangdang.com/shoppingcart/cart_append_new?'
               'product_ids={"product":[{"productId":"%s",'
               '"productCount":"1000000","promotion":[]}]}'
               '#http://product.dangdang.com/product.aspx?product_id=%s')

    url = baseurl % (id, id)
    html = requests.get(url).content
    # html.parser为python内置解析， 如果安装了lxml建议换lxml
    soup = BeautifulSoup(html, 'html.parser')
    # 根据标签定位库存信息
    l = soup.find('span', {'class': 'gift_lack_detail'})
    # 通过正则匹配数量
    if re.findall('\d+', l.text):
        quantity = re.findall('\d+', l.text)[0]
    else:
        # 未找到则返回0
        quantity = 0
    # 获取商品名称
    title = soup.find('span', {'class': 'gift_lack_name'}).text.strip('\n')
    return title, int(quantity)


def mysleep(res=3):
    # 随机睡眠
    time.sleep(random.random() * res)


class FSig(QtCore.QObject):
    # 建立一个signal类用于收发list类信号
    sig = QtCore.Signal(list)

    def __init__(self):
        QtCore.QObject.__init__(self)


class DangDangXiaDan(object):

    '''
    当当下单
    '''

    def __init__(self, userInfo, threadNum, **options):
        # 登陆网页url
        self.loginUrl = 'https://login.dangdang.com/signin.php'
        # 提交表单信息的基础url
        self.baseSubmitUrl = ('http://checkoutb.dangdang.com/'
                              'web/consignee/submit')
        # 选择使用什么浏览器运行selenium
        profile = FirefoxBinary('/home/never/下载/firefox/firefox')
        self.browser = webdriver.Firefox(firefox_binary=profile)
        # self.browser = webdriver.PhantomJS(executable_path=phantomjs_path,
        #                                    desired_capabilities=dcap)
        # 运行selenium登陆
        self.browser.get(self.loginUrl)
        # 最大化窗口
        # 由于需要截取验证码，最大化窗口避免不同电脑分辨率不同对验证码位置运算的影响
        self.browser.maximize_window()
        # 对参数进行unicode存储
        self.options = {x: unicode(y) for x, y in options.items()}

        # 基础信息建立
        self.username = userInfo[0]
        self.password = userInfo[5]
        self.itemID = userInfo[7].split(';')
        self.booklist = zip(userInfo[7].split(';'), userInfo[8].split(';'))
        address = {'name': userInfo[15],
                   'pro': userInfo[9],
                   'city': userInfo[10],
                   'district': userInfo[11],
                   'addr_detail': userInfo[13],
                   'postcode': userInfo[14],
                   'phone': userInfo[16]}
        # unicode编码传输网络数据
        self.address = {x: unicode(y) for x, y in address.items()}
        # 实例化信号类，用于传输siganl给QT
        self.c = FSig()
        # 记录下线程号码
        self.threadNum = threadNum
        self.imgfile = imgfile % threadNum

    def myprint(self, info):
        '''
        将日志与线程ID传送回QT界面
        '''
        print info
        self.c.sig.emit([info.encode('utf8'), self.threadNum])

    def _switch_new_window(self):

        self.windows = self.browser.window_handles
        self.browser.switch_to.window(self.windows[-1])
        time.sleep(1)
        self.myprint('Now we are at %s' % self.browser.title.encode(
            'utf8'))

    def download_captcha(self):
        '''
        # 下载验证码到本地
        '''
        try:
            self.browser.find_element_by_id("J_loginMaskClose").click()
        except:
            if self.browser.current_url != self.loginUrl:
                return
        # 定位验证码元素，点击以刷新
        element = self.browser.find_element_by_id('imgVcode')
        element.click()
        # 获得验证码坐标，位置等信息
        location = element.location
        size = element.size
        # 二次存储验证码
        self.browser.save_screenshot('1.jpg')
        self.browser.save_screenshot(self.imgfile)
        # 使用PIL截取需要的部分
        im = Image.open(self.imgfile)
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = im.crop((left, top, right, bottom))  # 870, 328, 956, 366
        im.save(self.imgfile)  # saves new cropped image

    def login(self):
        '''
        以打码平台自动化登陆当当
        '''
        # 关闭提示弹窗
        try:
            self.browser.find_element_by_id("J_loginMaskClose").click()
        except:
            pass
        # 下载验证码
        self.download_captcha()
        # 输入账号密码等信息
        username_input = self.browser.find_element_by_id("txtUsername")
        username_input.clear()
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("txtPassword")
        password_input.clear()
        password_input.send_keys(self.password)
        # 请求UU打码传回验证码
        ucode = Ucode(self.options['uuUser'], self.options['uuPasswd'])
        captcha = ucode.uu_captcha(self.imgfile)
        if captcha:
            print 'captcha:', captcha
            self.browser.find_element_by_id(
                'codeReplacer').send_keys(captcha)
            self.browser.find_element_by_id("submitLoginBtn").click()
        time.sleep(1)
        # 判断当前页面是否还属于登陆页面，来判断登陆成功
        if self.loginUrl in self.browser.current_url:
            self.browser.find_element_by_id("txtUsername")
            self.myprint(u'登陆失败,正在返回失败验证码...失败原因 %s' % ucode.fail_requests())
            return False
        else:
            self.myprint(u'login successfully')
            time.sleep(2)
            return True
        self.myprint(u'帐号:%s, login fail...' % self.username)

    def checkCaptcha(self, captcha):
        '''
        获取QT界面回传值登陆
        '''
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

    def empty_shopping_list(self):
        '''
        清空购物车
        '''
        # 先进入购物车页面获取当前购物车商品编号
        shoppingListUrl = ('http://shopping.dangdang.com/shoppingcart/'
                           'shopping_cart.aspx')
        self.browser.get(shoppingListUrl)
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        shopping_list = '%2C'.join(i.get('data-item', '') for i in
                                   soup.select('tbody > tr > td > a')
                                   if i.get('data-item', ''))
        # 请求清空购物车
        emp_url = ('http://shopping.dangdang.com'
                   '/shoppingcart/remove?itemIds=') + shopping_list
        self.browser.get(emp_url)
        self.myprint(u'已清空之前的购物车')

    def search_books(self, book_id, number):
        '''
        加入商品到购物车
        '''
        # 请求规定商品数量加入购物车
        # 注意此时无法校验该商品是否在某地去缺货
        book_url = ('http://shopping.dangdang.com/shoppingcart/'
                    'cart_append_new?product_ids={"product":'
                    '[{"productId":"%s","productCount":"%s",'
                    '"promotion":[]}]}') % (book_id, number)
        self.browser.get(book_url)
        self.myprint(u'帐号:%s, 已检索到%s, 加入购物车 %s 本' % (self.username, book_id, number))

    def pay(self):
        '''
        结算购物车
        '''
        self.myprint(u'填写地址...')
        # 当当订单网址
        orderUrl = 'http://checkoutb.dangdang.com/checkout.aspx#'

        # 填写送货地址信息
        # 获取地址在当当内部的ID号
        # 注意有可能需要刷新该cid文件，但是需要抓取几千页面耗时很久
        countryid = cid[u'中国']
        proid = countryid[1][self.address['pro']]
        cityid = proid[1][self.address['city']]
        districtid = cityid[1][self.address['district']]
        # 获取当前页面cookie
        cookie = [item["name"] + "=" + item["value"]
                  for item in self.browser.get_cookies()]
        cookiestr = ';'.join(item for item in cookie)
        # 构造请求头，注意Content-Type很重要，如果不填写会导致信息传输不正确
        headers = {'Cookie': cookiestr,
                   'Connection': 'keep-alive',
                   'Host': 'checkoutb.dangdang.com',
                   'User-Agent': (' Mozilla/5.0 (X11; Linux i686 '
                                  'on x86_64; rv:45.0) Gecko/20100101'
                                  ' Firefox/45.0'),
                   'Accept': ('text/html,application/xhtml+xml,'
                              'application/xml;q=0.9,*/*;q=0.8'),
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip, deflate',
                   'Content-Type': ('application/x-www-form-urlencoded;'
                                    'charset=utf-8'),
                   'Referer': orderUrl}
        # 构造数据表单
        data = {'ship_name': self.address['name'],
                'country_id': countryid[0],
                'province_id': proid[0], 'city_id': cityid[0],
                'town_id': districtid[0], 'quarter_id': districtid[0],
                'ship_zip': self.address['postcode'],
                'ship_mb': self.address['phone'], 'ship_tel': '',
                'ship_address': self.address['addr_detail'],
                'address_status': '2'}
        # 由于表单内含有中文字符，当前页面不支持中文url解析，只能用post请求发送
        requests.post(self.baseSubmitUrl, headers=headers, data=data)
        self.myprint(u'保存输入新地址')

        # 填写送货方式
        # inherit_status=true, set all orders the same delivermthods
        # 多个订单时注意inherit_status参数
        delBaseUrl = ('http://checkoutb.dangdang.com/web/shipment/submit?'
                      'ship_type=1&ship_date_type=%s&cur_edit_area=1&'
                      'shop_id=0&order_sequence_id=0_0&inherit_status=true'
                      '&addr_id=136463321&packing_type=0&'
                      'is_submit_packing_type=true&order_type=0')
        delUrl = delBaseUrl % deliverydict[self.options['deliveryMthods']]
        self.browser.get(delUrl)
        mysleep()

        # 填写支付方式
        # inherit_status=true, set all orders the same delivermthods
        # 多个订单时注意inherit_status参数
        payBaseUrl = ('http://checkoutb.dangdang.com/web/payment/submit?'
                      'pay_type=0&pay_id=%s&order_sequence_id=0_0&'
                      'inherit_status=true')
        payUrl = payBaseUrl % paydict[self.options['payMethods']]
        self.browser.get(payUrl)
        self.browser.get(orderUrl)
        time.sleep(2)

        # 处理发票信息
        # 无法发送请求，对同一表单发送请求时失败，原因中文字符解码问题，尚未找到解决
        # 暂用元素点击事件代替
        try:
            ele = WebDriverWait(self.browser, 30).until(
                expected_conditions.element_to_be_clickable((By.ID, 'invoiceCollapse')))
            if ele:
                ele.click()
            else:
                print('Cannot find element id=invoiceCollapse')
        except:
            print('wait worng element invoiceCollapse')
        mysleep(3)
        try:
            self.browser.find_element_by_id('rb_invoice_0_0').click()
            try:
                self.browser.find_element_by_id(invoicedict[self.options['invoiceTitle']][1]).click()
            except:
                print(invoicedict[self.options['invoiceTitle']][0])
                self.browser.find_element_by_id(invoicedict[self.options['invoiceTitle']][0]).click()
            Select(self.browser.find_element_by_id('invoice_content_0_0')).select_by_visible_text(self.options['invoice'])
            self.browser.find_element_by_id('invoice_submit_0_0').click()
        except:
            print('Cannot find element invoice_type_0_0')

        # 优惠码，礼券
        self.promoCode = self.options.get('promoCode', '')
        self.coupon = self.options.get('coupon', '')
        if self.promoCode:
            self.browser.find_element_by_id('expandDiscountCode').click()
            self.brower.find_element_by_id('iptUseDiscountCode').send_keys(self.promoCode)
            self.browser.find_element_by_id('submitDiscountCode').click()
        # 获取当前页面内礼券ID，以QT回传的关键字匹配礼券并使用
        if self.coupon:
            self.browser.find_element_by_id('expandCoupon').click()
            html = self.browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            ele = soup.find('select', {'id': 'orderCouponSlt_0_0'})
            ourCoupons = [(i['value'], i.text)
                          for i in ele.find_all('option')
                          if i.get('value', '')]
            couponID = [cou for cou, n in ourCoupons if self.coupon in n]
            if couponID:
                couponBaseUrl = ('http://checkoutb.dangdang.com/web/coupon/'
                                 'use?coupon_numer=%s&'
                                 'order_sequence_id=0_0')
                couponUrl = couponBaseUrl % couponID[0]
                self.browser.get(couponUrl)
                mysleep()
                self.browser.get(orderUrl)
            else:
                self.myprint(u'没找到相关的优惠券...')
                time.sleep(2)
        self.browser.find_element_by_id('submit').click()
        self.myprint(u'帐号:%s, 完成订单' % self.username)

    def cancel(self):
        '''
        取消预购的商品，
        取消为凑单优惠而加入的预购商品
        '''
        # 获取QT传回的商品ID
        self.cancelItem = self.options.get('cancelItem', '')
        if self.cancelItem in self.itemID:
            self.myprint(u'检测要取消的预购商品')
            orderUrl = 'http://orderb.dangdang.com/myallorders.aspx'
            self.browser.get(orderUrl)
            eles = self.browser.find_elements_by_name('ordercancellink')
            eles = [i for i in eles
                    if self.cancelItem in i.get_attribute('href')]
            for ele in eles:
                ele.click()
                self.browser.find_element_by_class_name('btn_or').click()
                self.browser.find_element_by_class_name('btn_or').click()
            self.myprint(u'已经取消预购商品')

    def shopping(self, c):
        '''
         手动填写验证码下单
        '''
        try:
            self.empty_shopping_list()
            for i in self.booklist:
                self.search_books(*i)
            self.pay()
            self.cancel()
            self.browser.close()
            self.myprint('Done!')
            c.sig.emit(str(self.threadNum))
        except:
            self.myprint(u'fail...')

    def automationShopping(self, c):
        '''
        自动填写验证码下单
        '''
        try:
            if self.login():
                self.empty_shopping_list()
                for i in self.booklist:
                    self.search_books(*i)
                # self.empty_shopping_list()
                self.pay()
                self.cancel()
            self.browser.close()
            self.myprint('Done!')
            c.sig.emit(str(self.threadNum))
        except Exception as e:
            print e
            self.myprint(u'fail...')

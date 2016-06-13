#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-06-08 11:07:06
# @Author  : Nevermoreluo (nevermoreluo@gmail.com)


imgfile = 'screenshot%s.jpg'

# 设置phantomjs路径
phantomjs_path = ''
userSettingDate = 'userSetting'

paydict = {u'网上支付': '-1',
           u'货到付款-支付宝扫码支付': '56',
           u'货到付款-现金': '1',
           u'货到付款-POS机刷卡': '54',
           u'银行转帐': '2',
           u'他人代付': '100'}

invoicedict = {u'个人': 'invoice_title_person_0_0',
               u'单位': 'invoice_title_company_0_0'}

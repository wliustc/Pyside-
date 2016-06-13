# 简单图形化界面dangdang下单

当当自动下单功能

需要uu打码功能的请自行修改uu_captcha内的软件ID和软件key

手动打码的可以不填

目前环境为python2

库依赖selenuim,PIL,PySide,requests

依赖PhantomJS，请在config内填写好您安装的phantomjs的地址

或者有火狐又不怕慢的同学可以修改dangdang_pyside.py内的self.browser

mianWindow.py为主界面窗口，运行即可。

目前已支持：

1.支持多线程同时工作

2.支持自动化填写地址，清空购物车，检索书目，执行下单

3.支持日志时时打印反馈

4.支持打码平台帐号保存

5.支持数据导入

6.支持执行中终止所有线程任务

7.支持线程队列事件，即限定线程数

8.提供更多的参数设置，例如：送货时间，送货方式，付款方式，发票类型，价格区间等的自定义

待开发：

1.支持python3

2.线程挂起事件

3.完成订单自动取消勾选，提供报错，下次可重新开始任务

4.支持宽带重播，即更换IP(windows已实现)

5.支持更多规格的数据导入，xls，xlsx，mysql等

6.校验商品库存数量

7.订单完成反馈

8.更人性化的报错提示




近期更新：
# @Date    : 2016-06-13 22:51:34
修正了手动打码时的线程信号阻塞
增加了送货时间，发票类型，支付方式等系统设置
增加了下拉框系统设置本地保存

python初学者，项目持续更新，望各位提出宝贵的意见。

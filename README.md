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

8.提供更多的参数设置，例如：送货时间，送货方式，付款方式，发票类型，等的自定义

9.完成订单自动取消勾选，提供报错，下次可重新开始任务

10.校验商品库存数量

待开发：

1.订单完成反馈，价格区间

2.线程挂起事件

3.支持更多规格的数据导入，xls，xlsx，mysql等

4.支持宽带重播，即更换IP(windows已实现)

5.更人性化的报错提示

6.支持python3





近期更新：
# @Date    : 2016-06-16 00:00:34
增加了导入数据，用户可修改扩展
修正了异常退出时，子线程并未随主线程退出的bug

python初学者，项目持续更新，望各位提出宝贵的意见。

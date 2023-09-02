import os
import time
import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver import ChromeOptions

"""
程序目的
1. 实现登录
2. 抢票并下单
3. 付款
"""

# 大麦网主页
damai_url = "https://www.damai.cn/"
# 登录
login_url = "https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"
# 抢票目标页
target_url = "https://detail.damai.cn/item.htm?spm=a2oeg.search_category.0.0.1d9b6a637jYgCo&id=638663502196&clicktitle=%E5%90%89%E6%9E%97%E7%9C%81%E5%BE%B7%E4%BA%91%E7%A4%BE%C2%B7%E7%BA%A2%E4%BA%8B%E4%BC%9A-%E3%80%8A%E7%9B%B8%E5%A3%B0%E5%A4%A7%E4%BC%9A%E3%80%8B-%E9%95%BF%E6%98%A5"


# class Concert: 一台iPhone18
class Concert:

    # 初始化加载
    def __init__(self):
        # browser = get_browser()
        self.status = 0  # 状态，表示当前操作执行到那个步骤
        self.login_method = 1  # {0:模拟登录，1:cookie登录} 自行选择登录的方式
        # 设置浏览器,防止selenium被检测出来
        self.options = ChromeOptions()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        os.environ['PATH'] += r"D:\SeleniumDrivers\chromedriver_win32"  # 当前浏览器驱动对象
        # self.driver = webdriver.Chrome(chrome_options=self.options)
        self.driver = webdriver.Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chrome.exe', chrome_options=self.options)

    # cookies: 网站用于记录用户登录的信息
    def set_cookies(self):
        # 登陆调用设置cookies
        self.driver.get(damai_url)
        print("###请点击登录###")  # ————————这条代码可以优化
        while self.driver.title == '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':  # 如果页面还停留在主页，就休眠1秒
            sleep(1)
        print("###请扫码登录###")  # ————————这条代码可以优化
        while self.driver.title == '大麦登录':  # 如果页面还停留在登录页面，就休眠1秒
            sleep(1)
        print("###扫码成功###")
        # get_cookies: 是driver里面的方法
        pickle.dump(self.driver.get_cookies(),
                    open('cookies.pkl', 'wb'))  # 将self.driver.get_cookie()写入已打开的文件open('cookies.pkl','wb')中
        print("###cookies保存成功###")
        self.driver.get(target_url)
        sleep(10)

    # 如果说现在本地有 cookies.pkl 那么直接获取
    def get_cookie(self):
        cookies = pickle.load(open('cookies.pkl', 'rb'))  # 从本地读取 cookies.pkl 文件
        for cookie in cookies:
            cookie_dict = {
                'domain': '.damai.cn',
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            self.driver.add_cookie(cookie_dict)
        print('###正在载入cookies###')
        self.driver.get(target_url)

    def login(self):
        '''登录'''
        if self.login_method == 0:
            self.driver.get(login_url)
            print("###开始登录###")
        elif self.login_method == 1:
            # 创建文件夹，文件是否存在
            if not os.path.exists('./cookies.pkl'):
                self.set_cookies()  # 没有文件的情况登录
            else:
                self.driver.get(login_url)  # 跳转到抢票页
                self.get_cookie()  # 登录

    def login_rf(self, username, password):
        # 找到输入框，这里需要自行在F12的Elements中找输入框的位置，然后在这里写入
        user_input = self.driver.find_element_by_xpath('//*[@id="fm-login-id"]')
        pw_input = self.driver.find_element_by_xpath('//*[@id="fm-login-password"]')
        login_btn = self.driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button')

        # 输入用户名和密码，点击登录
        user_input.send_keys(username)
        pw_input.send_keys(password)
        time.sleep(1)
        login_btn.click()
        time.sleep(1)

    def enter_concert(self):
        """打开浏览器"""
        print("###打开浏览器###")
        # 调用登录
        self.login()  # 登录
        self.driver.refresh()  # 刷新页面
        self.status = 2  # 登录成功标识
        print("###登录成功###")

    #  2. 抢票并下单

    def choose_ticket(self):
        """ 选票操作 """
        if self.status == 2:
            print("=" * 30)
            print("### 开始进行日期及票价选择 ###")
            while self.driver.title.find("确认订单") == -1:
                try:
                    buybutton = self.driver.find_element_by_class_name('buybtn').text
                    if buybutton == '提交缺货登记':
                        self.status = 2  # 没有进行更改操作
                        self.driver.get(target_url)  # 刷新页面 继续执行操作
                    elif buybutton == '立即预定':
                        # 点击立即预定
                        self.driver.find_element_by_class_name('buybtn').click()
                        self.status = 3
                    elif buybutton == '立即购买':
                        self.driver.find_element_by_class_name('buybtn').click()
                        self.status = 4
                    elif buybutton == '选座购买':
                        self.driver.find_element_by_class_name('buybtn').click()
                        self.status = 5

                except:
                    print("###没有跳转到订单结束页面###")

                title = self.driver.title
                if title == '选座购买':
                    # 选座购买逻辑
                    self.choice_seats()
                    if self.driver.title == '大麦登录':
                        # 定义目标URL信息
                        aim_url = {
                            'username': '13760265708',
                            'password': 'Li60265708'
                        }
                        # 登录
                        self.login_rf(aim_url['username'], aim_url['password'])
                        print("###重新登录###")
                        self.check_order()
                    else:
                        print("###正在抢票###")
                        self.check_order()
                    break
                elif title == '确认订单':
                    # 实现下单逻辑
                    while True:
                        # 如果标题为确认订单
                        print('正在加载。。。。。。')
                        if self.isElementExist('//*[@id="container"]/div/div[9]/button'):
                            # 下单操作
                            self.check_order()
                            break

    def choice_seats(self):
        """ 选择座位 """
        while self.driver.title == '选座购买':
            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[1]/div[2]/img'):
                print('请快速选择座位。。。')
            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[2]/div/div'):
                self.driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div[2]/button').click()

    def check_order(self):
        """ 下单 """
        if self.status in [3, 4, 5]:
            print('###开始确认订单###')
            try:
                # 默认选第一个购票人信息
                time.sleep(0.5)
                self.driver.find_element_by_xpath('//*[@id="container"]/div/div[2]/div[2]/div[1]/div/label').click()
            except Exception as e:
                print("###购票人信息选择失败###")
                print(e)
            # 最后一步提交订单
            time.sleep(0.5)  # 太快了不好，影响加载，导致点击无效
            self.driver.find_element_by_xpath('//*[@id="container"]/div/div[9]/button').click()

    def isElementExist(self, element):
        """判断元素是否存在"""
        flag = True
        browser = self.driver
        try:
            browser.find_element_by_xpath(element)
            return flag
        except:
            flag = False
            return flag

    def finish(self):
        """抢票完成，退出"""
        self.driver.quit()


if __name__ == '__main__':
    try:
        con = Concert()
        con.enter_concert()  # 打开浏览器
        con.choose_ticket()  # 选择座位
    except Exception as e:
        print(e)
        con = Concert()
        con.finish()

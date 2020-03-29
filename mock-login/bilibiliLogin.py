#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
#@ Author    :   Eva
#@ Contact   :   1985467552@qq.com
#@ Time      :   2020/3/27 3:07 下午
#@ Desc      :   None
'''
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import base64
import random
from PIL import Image
from io import BytesIO
from config import USER_NAME_BLBL, PASSWORD_BLBL

BORDER = 8 #滑块验证码图片的border，移动滑块时减去此值才能准确移动，此处粗略记为8

class BilibiliLogin(object):
    def __init__(self, username, password):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 50)
        self.username = username
        self.password = password
        self.login_url = r'https://passport.bilibili.com/login'

    # def __del__(self):
    #     self.browser.close()

    def open(self):
        self.browser.get(self.login_url)
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'login-username'))
        )
        username_input.clear()
        username_input.send_keys(self.username)
        password_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'login-passwd'))
        )
        password_input.clear()
        password_input.send_keys(self.password)

    def get_geetest_image(self):
        js = 'return document.getElementsByClassName("geetest_canvas_fullbg")[0].toDataURL("image/png");'
        img_info = self.browser.execute_script(js)
        img_bs64 = img_info.split(',')[1]
        img = base64.b64decode(img_bs64)
        c_image = Image.open(BytesIO(img))
        c_image.save('c_image.png')

        js = 'return document.getElementsByClassName("geetest_canvas_bg")[0].toDataURL("image/png");'
        img_info = self.browser.execute_script(js)
        img_bs64 = img_info.split(',')[1]
        img = base64.b64decode(img_bs64)
        ic_image = Image.open(BytesIO(img))
        ic_image.save('ic_image.png')
        return c_image, ic_image

    def is_pixel_similar(self, c_image, ic_image, x, y):
        c_pixel = c_image.load()[x, y]
        ic_pixel = ic_image.load()[x, y]
        #阈值 允许误差
        threshold = 60
        # 比较RGB的绝对值是否小于阈值60,如果在阈值内则相同,反之不同
        if abs(c_pixel[0] - ic_pixel[0]) < threshold and abs(c_pixel[1] - ic_pixel[1]) < threshold and abs(c_pixel[2] - ic_pixel[2]) < threshold :
            return True
        return False

    def get_gap(self, c_image, ic_image):
        """
        获取偏移的值
        :param c_image: 完整的图片
        :param ic_image: 带缺口的图片
        :return:
        """
        left = 60
        # c_image.size:['width', 'height']
        for x in range(c_image.size[0]):
            for y in range(c_image.size[1]):
                if not self.is_pixel_similar(c_image, ic_image, x, y):
                    left = x
                    return left
        return left

    def get_random_seconds(self):
        """
        :return:随机的拖动暂停时间
        """
        return random.uniform(0.6, 0.9)

    def drag_slider(self, source, gap):
        """
        模仿人的拖拽动作：快速沿着X轴拖动（存在误差），再暂停，然后修正误差
        防止被检测为机器人，出现“图片被怪物吃掉了”等验证失败的情况
        :param source:要拖拽的html元素
        :param gap: 拖拽目标x轴距离
        :return: None
        """
        action_chains = ActionChains(self.browser)
        # 点击，准备拖拽
        action_chains.click_and_hold(source)
        # 拖动次数，二到三次
        dragCount = random.randint(2, 3)
        if dragCount == 2:
            # 总误差值
            sumOffsetx = random.randint(-15, 15)
            action_chains.move_by_offset(gap + sumOffsetx, 0)
            # 暂停一会
            action_chains.pause(self.get_random_seconds())
            # 修正误差，防止被检测为机器人，出现图片被怪物吃掉了等验证失败的情况
            action_chains.move_by_offset(-sumOffsetx, 0)
        elif dragCount == 3:
            # 总误差值
            sumOffsetx = random.randint(-15, 15)
            action_chains.move_by_offset(gap + sumOffsetx, 0)
            # 暂停一会
            action_chains.pause(self.get_random_seconds())

            # 已修正误差的和
            fixedOffsetX = 0
            # 第一次修正误差
            if sumOffsetx < 0:
                offsetx = random.randint(sumOffsetx, 0)
            else:
                offsetx = random.randint(0, sumOffsetx)

            fixedOffsetX += offsetx
            action_chains.move_by_offset(-offsetx, 0)
            action_chains.pause(self.get_random_seconds())

            # 最后一次修正误差
            action_chains.move_by_offset(-sumOffsetx + fixedOffsetX, 0)
            action_chains.pause(self.get_random_seconds())

        else:
            raise Exception("莫不是系统出现了问题？!")

        # 参考action_chains.drag_and_drop_by_offset()
        action_chains.release().perform()

    def login_success(self):
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'signin')))
            )
        except TimeoutException:
            return False

    def login(self):
        #打开登录页，输入用户名和密码
        self.open()
        #获取登录按钮
        login_button = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btn-login'))
        )
        #点击登录
        login_button.click()
        # 休眠, 让验证码图片加载出来
        time.sleep(2)
        #获取验证码完整和不完整的图片
        c_image, ic_image = self.get_geetest_image()
        #计算偏移量
        gap = self.get_gap(c_image, ic_image)
        print(f'缺口的偏移量为:{gap}')
        #获取移动轨迹
        gap -= BORDER
        #获取滑块按钮
        slider = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'geetest_slider_button'))
        )
        self.drag_slider(slider, gap)

        if self.login_success():
            print('登录成功')
        else:
            self.login()

if __name__ == '__main__':
    bilibiliLogin = BilibiliLogin(USER_NAME_BLBL, PASSWORD_BLBL)
    bilibiliLogin.login()

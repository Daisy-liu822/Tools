import pyautogui
import random
import time

#定义屏幕边界
screeWidth, screenHeight = pyautogui.size()

#定义随机移动鼠标的函数
def move_mouse_randomly():
    x = random.randint(0, screeWidth - 1)
    y = random.randint(0, screenHeight -1)
    duration = random.uniform(0.1 , 2.0) #移动时间在0.5到2秒之间
    pyautogui.moveTo(x, y, duration)
    print("Moved mouse to ({}, {})".format(x, y))

# 主循环
try:
    while True:
        move_mouse_randomly()
        time.sleep(random.uniform(10, 30)) # 等待一段时间再移动鼠标
        # 点击
        pyautogui.click(1400,500)

except KeyboardInterrupt:
    print("Program interrupted by user.")
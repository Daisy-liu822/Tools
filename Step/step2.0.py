import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 配置常量
ACCOUNT = "1369023165@qq.com"
PASSWORD = "liuxu123"
STEP_MIN, STEP_MAX = 20000, 30000
URL = "https://shuabu.vip/"

def setup_driver():
    """初始化并返回Chrome浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=chrome_options)

def click_if_exists(driver, selector, wait=2):
    """
    如果元素存在则点击
    :param driver: selenium driver
    :param selector: CSS选择器
    :param wait: 点击后等待秒数
    """
    try:
        btn = driver.find_element(By.CSS_SELECTOR, selector)
        btn.click()
        time.sleep(wait)
    except Exception:
        pass  # 元素不存在时忽略

def job():
    """自动填写账号、密码、步数，等待人工滑块并提交"""
    driver = setup_driver()
    driver.get(URL)
    time.sleep(2)  # 等待页面加载

    # 处理弹窗
    click_if_exists(driver, '#app > div > div:nth-child(4) > div > div > footer > span > button.el-button.el-button--primary')
    click_if_exists(driver, '#app > div > div:nth-child(5) > div > div > footer > span > button.el-button.el-button--primary')

    try:
        # 输入账号
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入手机号或邮箱"]').send_keys(ACCOUNT)
        # 输入密码
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入密码"]').send_keys(PASSWORD)
        # 输入步数
        step_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入步数"]')
        step_input.clear()
        step_input.send_keys(str(random.randint(STEP_MIN, STEP_MAX)))
    except Exception as e:
        print(f"表单填写失败: {e}")
        driver.quit()
        return

    input("请手动完成滑块验证码后，按回车继续...")

    try:
        driver.find_element(By.CSS_SELECTOR, '.submit-btn').click()
        time.sleep(5)
    except Exception as e:
        print(f"提交失败: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    job()
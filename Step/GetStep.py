import schedule
import time
import random
import requests
from datetime import datetime
import logging
import threading

# 配置部分
ACCOUNT = "136982316@qq.com"
PASSWORD = "liuxu520"
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 5  # 重试延迟（秒）
STEP_MIN, STEP_MAX = 23000, 25000
CHECK_INTERVAL = 1  # 定时任务检查间隔（秒）
SCHEDULE_TIME = "18:00"  # 定时任务时间

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def job():
    # 生成随机步数
    steps = random.randint(STEP_MIN, STEP_MAX)

    # API地址
    url = f"https://steps.api.030101.xyz/api?account={ACCOUNT}&password={PASSWORD}&steps={steps}"

    retry_count = 0
    logging.info(current_timestamp() + '开始今日推送')
    while retry_count < MAX_RETRIES:
        try:
            response = requests.get(url,timeout=10, verify=False)

            # 判断响应结果
            if response.status_code == 200:
                logging.info(f"步数: {steps}步,推送成功")
                break
            else:
                logging.warning(f"步数推送失败，返回状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"请求过程中发生错误: {e}")

        retry_count += 1
        if retry_count < MAX_RETRIES:
            logging.info(f"重试 {retry_count}/{MAX_RETRIES} 次后重试...")
            time.sleep(RETRY_DELAY)
        else:
            logging.error("已达到最大重试次数，放弃重试。")


# # 定时任务，每天下午6点触发任务
# schedule.every().day.at(SCHEDULE_TIME).do(job)
#
# logging.info(f"定时任务已启动，每天下午6点会推送步数。")
# logging.info("输入 'manual' 手动触发任务，输入 'exit' 退出程序。")


# # 手动触发机制
# def manual_trigger():
#     while True:
#         user_input = input().strip().lower()
#         if user_input == 'manual':
#             logging.info("手动触发任务...")
#             job()
#         elif user_input == 'exit':
#             logging.info("退出程序...")
#             return
#         else:
#             logging.warning("无效的输入，请输入 'manual' 手动触发任务，输入 'exit' 退出程序。")
#
#
# def run_schedule():
#     while True:
#         schedule.run_pending()
#         time.sleep(CHECK_INTERVAL)  # 等待指定的时间，防止 CPU 占用过高


# if __name__ == "__main__":
#     schedule_thread = threading.Thread(target=run_schedule)
#     manual_trigger_thread = threading.Thread(target=manual_trigger)
#
#     schedule_thread.start()
#     manual_trigger_thread.start()
#
#     schedule_thread.join()
#     manual_trigger_thread.join()

if __name__ == "__main__":
    job()
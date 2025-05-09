import time
import requests
import json
from datetime import datetime

class SheinOrderFlow:
    def __init__(self):
        # 生成唯一的参考号
        timestamp = str(int(time.time()))[:8]
        self.ref_num = f'TR250{timestamp}'
        self.user_id = '2D63B8A9C67D18B6482587C2005D89DF'
        self.lt_ref_num = None
        self.base_url = 'https://api-gateway.qcore-preprod.qima.com'
        
    def log(self, message):
        """简单的日志函数"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
        
    def step1_2_mock_shein_booking_request(self):
        """步骤1-2: 模拟SHEIN发送订单请求到QIMA"""
        self.log(f"开始模拟SHEIN发送订单请求, 使用RefNum: {self.ref_num}")
        
        url = f"{self.base_url}/exchange-service/v1.0/shein/mock/order-info?refNum={self.ref_num}"
        
        payload = {
            "sheinNo": self.ref_num,
            "payer": 0,
            "checkTypeName": "纺织品",
            "applyInfo": {
                "applyUserName": "东岳纺织",
                "contactNum": "18670467038",
                "email": "111@qq.com",
                "address": "四会市东成街道新江科技城蕉园",
                "businessLicenseName": "广东东岳纺织有限公司",
                "businessLicenseAddress": "四会市东成街道新江科技城蕉园"
            },
            "sampleInfoList": [
                {
                    "sampleNo": "",
                    "sampleNoType": 1,
                    "ingredient": "",
                    "complianceLabel": None,
                    "imgUrlList": [
                        "https://sit-supply.oss-cn-shenzhen.aliyuncs.com/web/uploadFile/35774380753ef7dd47b127602471fbd3.png?Expires=1716778499&OSSAccessKeyId=LTAI5tRoCW5YFGVY6MxxWKBM&Signature=FAZ3nJ8nxTpY02kXmdbmpWl9CfM%3D"
                    ]
                }
            ],
            "checkRequirement": {
                "level": 0,
                "checkRemark": "",
                "itemCodeList": [
                    {
                        "itemCode": 6671838499660908509,
                        "itemName": "耐互染色牢度",
                        "checkType": 1
                    },
                    {
                        "itemCode": 7000000000000000015,
                        "itemName": "耐折牢度1",
                        "checkType": 0
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            self.log(f"获取到响应: {response.text}")
            
            response_data = response.json()
            assert response_data['code'] == 200, f"API返回错误: {response_data['message']}"
            assert response_data['message'] == "mock shein order info data success", "响应消息不符合预期"
            
            self.log("SHEIN订单模拟请求发送成功")
            return True
        except Exception as e:
            self.log(f"SHEIN订单模拟请求失败: {str(e)}")
            return False
    
    def step3_4_process_booking_request(self):
        """步骤3-4: 处理SHEIN订单请求并创建LT订单"""
        self.log(f"开始处理SHEIN订单请求并创建LT订单, RefNum: {self.ref_num}")
        
        url = f"{self.base_url}/exchange-service/v1.0/shein/booking?refNum={self.ref_num}&userId={self.user_id}&isCache=true"
        
        headers = {
            'X-Kong-Request-Id': '6332705931cba414ed1cc84ece081f3c'
        }
        
        try:
            response = requests.post(url, headers=headers)
            self.log(f"获取到响应: {response.text}")
            
            response_data = response.json()
            
            if response_data['code'] == 0 and 'data' in response_data:
                assert response_data['message'] == "SUCCESS", "响应消息不符合预期"
                assert 'ltRefNum' in response_data['data'], "缺少ltRefNum字段"
                assert 'ltRefId' in response_data['data'], "缺少ltRefId字段"
                assert response_data['data']['refNum'] == self.ref_num, "refNum不匹配"
                
                self.lt_ref_num = response_data['data']['ltRefNum']
                self.ref_id = response_data['data']['ltRefId']
                self.log(f"成功创建订单，AIMS订单号: {self.lt_ref_num}, LT订单ID: {self.ref_id}")
                return True
            else:
                self.log(f"创建订单失败: {json.dumps(response_data)}")
                self.log("可能原因: refNum已存在或API服务不可用，请检查preprod环境状态")
                return False
        except Exception as e:
            self.log(f"处理订单请求失败: {str(e)}")
            return False
    
    def step5_verify_order_in_aims(self):
        """步骤5: 验证AIMS中的订单"""
        self.log("注意: AIMS验证需要通过浏览器自动化完成，本脚本未实现该功能")
        self.log("如需实现，建议使用Selenium WebDriver进行浏览器自动化测试")
        
        """
        # 使用Selenium实现浏览器自动化的示例代码（需要额外安装Selenium并配置webdriver）
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        
        driver = webdriver.Chrome()  # 需要安装Chrome驱动
        
        # 登录AIMS系统
        driver.get("https://ppsso.qima.com/login")
        driver.find_element(By.ID, "username").send_keys("daisy.liu")
        driver.find_element(By.ID, "password").send_keys("Daisyliu123")
        driver.find_element(By.ID, "loginBtn").click()
        
        # 等待登录完成
        time.sleep(2)
        
        # 访问订单详情页面
        driver.get(f"https://ppsso.qima.com/aims-web/order-basic?action=edit&orderId={self.ref_id}&section=orderStyleInfo&status=Pending")
        
        # 验证订单信息
        order_no = driver.find_element(By.ID, "labOrderNumber").text
        assert self.lt_ref_num in order_no, "订单号不匹配"
        
        client_name = driver.find_element(By.CSS_SELECTOR, "a.linked-ele h4.selected-value").text
        assert client_name.strip().upper() == "SHEIN", f"不是SHEIN订单，实际为: {client_name}"
        
        self.log(f"成功验证AIMS中的SHEIN订单: {self.lt_ref_num}")
        
        driver.quit()
        """

    def run_all_steps(self):
        """执行所有测试步骤"""
        self.log("开始SHEIN订单流程测试")
        
        # 步骤1-2
        if not self.step1_2_mock_shein_booking_request():
            self.log("测试中断: 步骤1-2失败")
            return False
            
        # 步骤3-4
        if not self.step3_4_process_booking_request():
            self.log("测试中断: 步骤3-4失败")
            return False
            
        # 步骤5 (可选)
        # self.step5_verify_order_in_aims()
        
        self.log(f"SHEIN订单流程测试完成，订单参考号: {self.ref_num}, AIMS订单号: {self.lt_ref_num}")
        return True

if __name__ == "__main__":
    # 执行测试
    shein_test = SheinOrderFlow()
    shein_test.run_all_steps()

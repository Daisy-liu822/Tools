from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from services_extract import extract_services
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from config_loader import load_config
from typing import Tuple

def retry_decorator(retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class JenkinsDeployer:
    def __init__(self, max_workers=3, build_timeout=1800, headless=True):
        self.driver = None  # 初始化为 None
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 从HTML文件中动态加载services
        with open('JenkisBuild/jenkins_build_page.html', 'r', encoding='utf-8') as file:
            html = file.read()
        self.services = extract_services(html)
        
        # 从配置文件加载skip_services
        config = load_config()
        self.skip_services = config.get('skip_services', [])
        
        self.base_url = "https://jenkins.qima.com/job/PP/job/{}/build?delay=0sec"
        self.it_dependency_url = "https://jenkins.qima.com/job/Prod/job/prod-lt-dependency/build?delay=0sec"
        self.max_workers = max_workers
        self.build_timeout = build_timeout
        self.headless = headless  # 添加headless属性
        self.driver = webdriver.Edge(options=self._get_browser_options())
        
    def _get_browser_options(self):
        """配置浏览器选项"""
        options = webdriver.EdgeOptions()
        if self.headless:
            options.add_argument('--headless')
        else:
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # 增加以下配置来抑制更多日志
            options.add_argument('--log-level=3')  # 仅显示 FATAL
            options.add_argument('--silent')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-smartscreen')  # 禁用 SmartScreen
            options.add_argument('--disable-identity-provider-fetch')  # 禁用身份验证提供者获取
            options.add_argument('--disable-qqbrowser-importer')  # 禁用 QQBrowser 导入器
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-extensions')  # 禁用扩展
            options.add_argument('--disable-infobars')  # 禁用信息栏
            options.add_argument('--disable-popup-blocking')  # 禁用弹出窗口拦截
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')  # 禁用隔离特性
        return options

    def deploy(self, services_branches: dict):
        """
        部署多个服务，失败时重试一次
        :param services_branches: Dict[service_name: str, branch: str]
        """
        if not services_branches:
            return
        
        self.logger.info(f"开始批量部署服务: {list(services_branches.keys())}")
        start_time = time.time()
        
        try:
            for service, branch in services_branches.items():
                if service not in self.services and service != 'it-dependency':
                    self.logger.warning(f"服务 {service} 不在预定义列表中")
                    continue
                    
                service_start_time = time.time()
                self.logger.info(f"===== 开始部署服务: {service} =====")
                self.logger.info(f"分支: {branch}")
                
                success = False
                for attempt in range(2):  # 最多尝试2次（初次+1次重试）
                    if attempt > 0:
                        self.logger.info(f"第 {attempt + 1} 次尝试部署: {service}")
                    
                    try:
                        url = self.it_dependency_url if service == 'it-dependency' else self.base_url.format(service)
                        self.logger.info(f"访问构建页面: {url}")
                        self.driver.get(url)
                        
                        self.logger.info(f"填写分支信息: {branch}")
                        branch_input = self._wait_for_element((By.XPATH, 
                            '//*[@id="main-panel"]/form/div[1]/div[1]/div[3]/div/input[2]'))
                        branch_input.clear()
                        branch_input.send_keys(branch)
                        
                        self.logger.info("触发构建")
                        build_button = self._wait_for_element((By.XPATH, 
                            '//*[@id="bottom-sticker"]/div/button'))
                        build_button.click()
                        
                        if self._check_build_result():
                            success = True
                            break
                        else:
                            self.logger.error(f"服务 {service} 构建失败")
                    except Exception as e:
                        self.logger.error(f"部署服务 {service} 时发生错误: {str(e)}")
                    
                    if not success and attempt < 1:
                        self.logger.info(f"等待 5 秒后进行重试...")
                        time.sleep(5)
                
                service_end_time = time.time()
                duration = round(service_end_time - service_start_time, 2)
                self.logger.info(f"===== 服务 {service} 部署：{branch}{'成功' if success else '失败'} =====")
                self.logger.info(f"耗时: {duration} 秒")
                
        finally:
            total_duration = round(time.time() - start_time, 2)
            self.logger.info(f"部署结束，总耗时: {total_duration} 秒")
            if len(services_branches) > 0:
                try:
                    self.driver.quit()
                    self.driver = None
                except Exception as e:
                    self.logger.warning(f"关闭浏览器时发生错误: {str(e)}")

    def deploy_all_master(self):
        """部署所有服务的master分支"""
        # 配置日志
        import urllib3
        urllib3.disable_warnings()
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        
        # 构建所有服务的master分支字典
        services_to_deploy = {
            service: "master" for service in self.services 
            if service not in self.skip_services
        }
        
        # 使用deploy_concurrent进行部署
        return self.deploy_concurrent(services_to_deploy)
    
    def _wait_for_element(self, locator, timeout=10, retries=3) -> WebElement:
        """等待元素出现，带重试机制"""
        for attempt in range(retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                self.logger.warning(f"等待元素 {locator} 失败，重试第 {attempt + 1} 次")
                time.sleep(1)

    def _check_build_result(self, driver=None, max_retries=60):
        """检查构建结果"""
        retry_interval = 10
        driver = driver or self.driver
        self.logger.info("开始监控构建状态...")
        start_time = time.time()
        
        # 先等待一段时间让构建开始
        time.sleep(5)
        
        for attempt in range(max_retries):
            try:
                status_link = WebDriverWait(driver, retry_interval).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "build-status-link"))
                )
                title = status_link.get_attribute("title")
                
                if any(status in title.lower() for status in ["progress", "running", "pending"]):
                    elapsed = round(time.time() - start_time, 2)
                    self.logger.info(f"构建进行中... ({attempt + 1}/{max_retries}) - 已耗时: {elapsed}秒")
                    time.sleep(retry_interval)
                    driver.refresh()
                    continue
                
                if "Success" in title:
                    total_time = round(time.time() - start_time, 2)
                    self.logger.info(f"构建成功! 总耗时: {total_time}秒")
                    return True
                elif any(status in title for status in ["Failure", "Aborted"]):
                    total_time = round(time.time() - start_time, 2)
                    self.logger.error(f"构建失败! 总耗时: {total_time}秒")
                    return False
                    
            except StaleElementReferenceException:
                self.logger.warning(f"元素已过期，重试中... ({attempt + 1}/{max_retries})")
            except TimeoutException:
                self.logger.warning(f"等待超时，重试中... ({attempt + 1}/{max_retries})")
            except Exception as e:
                self.logger.error(f"检查构建结果时发生错误: {str(e)}")
                
            time.sleep(retry_interval)
            driver.refresh()
        
        total_time = round(time.time() - start_time, 2)
        self.logger.error(f"构建监控超时，总耗时: {total_time}秒")
        return False
        
    def __del__(self):
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    def deploy_concurrent(self, services_branches: dict):
        """并发部署多个服务"""
        if not services_branches:
            return {}
        
        # 配置日志
        import selenium.webdriver.remote.remote_connection as remote_connection
        remote_connection.LOGGER.setLevel(logging.WARNING)
        import urllib3
        urllib3.disable_warnings()
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        
        service_start_time = time.time()
        self.logger.info(f"===== 开始部署服务: {services_branches} =====")
        self.logger.info(f"分支: {services_branches}")
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            drivers = {}  # 使用字典来跟踪每个service对应的driver
            
            try:
                for service, branch in services_branches.items():
                    if service not in self.services and service != 'it-dependency':
                        self.logger.warning(f"服务 {service} 不在预定义列表中")
                        continue
                        
                    driver = webdriver.Edge(options=self._get_browser_options())
                    drivers[service] = driver
                    futures.append(
                        executor.submit(self._deploy_single_service_with_driver, 
                                      driver, service, branch)
                    )
                
                for future in futures:
                    try:
                       service, success = future.result()
                       results[service] = success
                       self.logger.info(f"服务 {service} 部署{'成功' if success else '失败'}")
                    except Exception as e:
                       self.logger.error(f"部署服务 {service} 时发生错误: {str(e)}")
                       results[service] = False
                    
            finally:
                # 清理所有driver
                for driver in drivers.values():
                    try:
                        driver.quit()
                    except Exception as e:
                        self.logger.warning(f"关闭driver时发生错误: {str(e)}")
                    
        return results

    def _deploy_single_service_with_driver(self, driver, service: str, branch: str) -> Tuple[str, bool]:
        """使用预创建的driver部署服务"""
        try:
            driver.set_page_load_timeout(30)
            success = self._execute_deploy(driver, service, branch)
            return service, success
        except Exception as e:
            self.logger.error(f"部署服务 {service} 时发生错误: {str(e)}")
            return service, False

    @retry_decorator(retries=2)
    def _fill_branch_and_build(self, driver, branch):
        """填写分支并触发构建"""
        branch_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                '//*[@id="main-panel"]/form/div[1]/div[1]/div[3]/div/input[2]'))
        )
        branch_input.clear()
        branch_input.send_keys(branch)
        
        build_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, 
                '//*[@id="bottom-sticker"]/div/button'))
        )
        build_button.click()

    def _execute_deploy(self, driver, service: str, branch: str) -> bool:
        """执行单个服务的部署"""
        try:
            url = self.it_dependency_url if service == 'it-dependency' else self.base_url.format(service)
            self.logger.info(f"访问构建页面: {url}")
            driver.get(url)
            self.logger.info(f"填写分支信息: {branch}")
            # 填写分支并构建
            self._fill_branch_and_build(driver, branch)
            self.logger.info(f"访问构建页面: {url}")
            # 检查构建结果
            return self._check_build_result(driver)
        except Exception as e:
            self.logger.error(f"部署服务 {service} 失败: {str(e)}")
            return False

if __name__ == "__main__":
    # 1.指定部署的服务和分支依次部署
    deployer = JenkinsDeployer(max_workers=3, build_timeout=1800, headless=False)
    services_to_deploy = {
        # 'it-dependency': 'master',
        # 'pp-lt-aims-web': 'master',
        # 'pp-lt-aims-service': 'master',
        # 'lt-document-service': 'master',
        'pp-iptb-service': 'master',
        # 'pp-lt-aims-web': 'master'
        
    }
    
    deployer.deploy(services_to_deploy)

    # # 假设你要检查特定构建的URL
    # build_url = "https://jenkins.qima.com/job/PP/job/pp-auditor-app-api/"
    # deployer.driver.get(build_url)
    # result = deployer._check_build_result()
    # print(f"构建结果: {'成功' if result else '失败'}")




    # # 并发部署
    # results = deployer.deploy_concurrent(services_to_deploy)
    # print(f"并发部署结果: {results}")

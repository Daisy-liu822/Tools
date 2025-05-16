import requests
from bs4 import BeautifulSoup
import time
import os
import pickle
import re
import json
import argparse
from pathlib import Path
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# JIRA URL - 使用JIRA的实际URL
JIRA_URL = "https://qima.atlassian.net/issues/?filter=20334"
COOKIES_FILE = os.path.join(SCRIPT_DIR, "jira_cookies.pkl")
HTML_FILE = os.path.join(SCRIPT_DIR, "jira_page_source.html")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "service_categories_from_list.txt")
LOGIN_URL = "https://qima.atlassian.net/login"

# Service categories - 从release_exctract.py复制过来
COMMONS = ['commons']
DEPENDENCY = ['lt-dependency']
BACK_END = [
    'psi-service', 'wqs-service', 'aims-service', 'external-service', 
    'data-service', 'document-service', 'irp-service', 'reports-service', 
    'customer-service', 'final-report-service', 'file-service', 'iptb-service'
]
FRONT_END = [
    'aca', 'parameter-web', 'irp-web', 'psi-web', 'public-api', 'back-office', 
    'aims-web', 'program-web', 'exchange-console', 'backoffice-portal-web', 
    'checklist-web', 'gi-web', 'auditor-app', 'B2b-service', 
    'iptb-web', 'b2b_dt_service'
]
EKS = [
    'claim', 'claim-cloud', 'aca-new', 'parameter-service-legacy-cloud', 
    'lt-external-service-cloud', 'ai-service-cloud', 'e-signature-service-cloud', 
    'exchange-service-cloud', 'exchange-worker-service-cloud', 'finance-service-cloud', 
    'report-service-cloud', 'ordercore-service-cloud', 'file-service-cloud', 
    'payment-service-cloud', 'mail-service-cloud', 'document-generation-service-cloud', 
    'document-verification-service-cloud', 'exchange-console-cloud', 
    'search-center-service-cloud', 'dynamic-order-cloud', 'dynamic-order-service-cloud', 
    'factory-service-cloud', 'price-service-cloud', 'iptb-service-cloud', 
    'ip-service-cloud', 'program-service-cloud', 'message-service-cloud', 
    'invoice-service-cloud', 'gi-service-cloud', 'route-service-cloud', 'claim-service-cloud',
    'auditor-app-service-cloud', 'auditor-app-services-cloud', 'cia-new'
]
EXCLUDE_PROJECTS = [
    'lt-dao', 'lt-dto', 'lt-constant', 'lt-converter', 
    'lt-model', 'lt-utility', 'auditor-app-service',
    'na', 'none', 'n/a', '-'  # 添加无效的服务名
]

def reset_cookies():
    """重置cookies文件，删除可能已损坏的文件"""
    if os.path.exists(COOKIES_FILE):
        try:
            os.remove(COOKIES_FILE)
            print(f"已删除旧的cookies文件: {COOKIES_FILE}")
            return True
        except Exception as e:
            print(f"删除cookies文件时出错: {str(e)}")
            return False
    else:
        print(f"没有找到cookies文件: {COOKIES_FILE}")
        return True

def save_cookies(driver, filename=COOKIES_FILE):
    """保存浏览器cookies到文件"""
    print(f"保存cookies到文件 {filename}")
    
    # 确保我们在Atlassian的网站中，获取所有必要的Cookie
    print("访问Atlassian主域以获取所有Cookie...")
    driver.get("https://qima.atlassian.net")
    time.sleep(2)  # 减少等待时间
    
    # 尝试访问JIRA页面以获取JIRA特定的Cookie
    print("访问JIRA页面以获取JIRA特定的Cookie...")
    driver.get(JIRA_URL)
    time.sleep(2)  # 减少等待时间
    
    # 获取当前所有Cookie
    all_cookies = driver.get_cookies()
    print(f"获取到总共 {len(all_cookies)} 个Cookie")
    
    # 检查是否获取到了关键的会话Cookie
    session_cookies = [c for c in all_cookies if c.get('name') in ['JSESSIONID', 'atlassian.xsrf.token', 'cloud.session.token', 'tenant.session.token']]
    if not session_cookies:
        print("警告: 没有找到关键的会话Cookie，会话可能无效")
    else:
        print(f"找到 {len(session_cookies)} 个关键会话Cookie")
    
    # 只显示关键Cookie信息以减少日志输出
    for cookie in session_cookies:
        print(f"关键Cookie: {cookie.get('name')} (domain: {cookie.get('domain', 'N/A')}, path: {cookie.get('path', 'N/A')})")
    
    # 保存所有Cookie，不过滤
    with open(filename, 'wb') as f:
        pickle.dump(all_cookies, f)
    
    print(f"成功保存 {len(all_cookies)} 个Cookie到文件")
    return len(all_cookies) > 0

def load_cookies(driver, filename=COOKIES_FILE):
    """从文件加载cookies到浏览器"""
    if not os.path.exists(filename):
        print(f"Cookie文件 {filename} 不存在")
        return False
        
    try:
        # 加载保存的Cookie
        with open(filename, 'rb') as f:
            cookies = pickle.load(f)
            
        print(f"从文件加载了 {len(cookies)} 个cookies")
        
        # 检查是否包含Atlassian域的Cookie
        atlassian_cookies = [c for c in cookies if 'atlassian' in c.get('domain', '')]
        if not atlassian_cookies:
            print("没有找到有效的Atlassian域Cookie，需要重新登录")
            return False
            
        print(f"找到 {len(atlassian_cookies)} 个Atlassian域Cookie")
        
        # 直接访问目标页面以节省时间
        print("访问目标URL以设置Cookie...")
        driver.get(JIRA_URL)
        time.sleep(2)  # 减少等待时间
        
        # 验证是否被重定向到登录页面
        if "id.atlassian.com" in driver.current_url:
            print("已被重定向到登录页面，先访问Atlassian主域以设置Cookie...")
            driver.get("https://qima.atlassian.net")
            time.sleep(2)  # 减少等待时间
        
        # 添加所有Cookie
        print("开始添加所有Cookie...")
        for cookie in atlassian_cookies:
            try:
                # 提取必要的Cookie属性
                name = cookie.get('name')
                value = cookie.get('value')
                domain = cookie.get('domain', '')
                
                # 只显示关键Cookie信息以减少日志
                if name in ['JSESSIONID', 'atlassian.xsrf.token', 'cloud.session.token', 'tenant.session.token']:
                    print(f"添加关键Cookie: {name} (domain: {domain})")
                
                # 创建一个简化的Cookie字典
                cookie_dict = {
                    'name': name,
                    'value': value
                }
                
                # 只添加域名相关属性，如果存在
                if domain:
                    cookie_dict['domain'] = domain
                if 'path' in cookie:
                    cookie_dict['path'] = cookie['path']
                if 'secure' in cookie and cookie['secure']:
                    cookie_dict['secure'] = True
                if 'httpOnly' in cookie and cookie['httpOnly']:
                    cookie_dict['httpOnly'] = True
                
                # 添加Cookie
                driver.add_cookie(cookie_dict)
            except Exception as e:
                print(f"添加Cookie失败: {name} - {str(e)}")
                continue
                
        # 刷新页面以应用Cookie
        print("刷新页面以应用Cookie...")
        driver.refresh()
        time.sleep(2)  # 减少等待时间
        

        
        # 检查是否需要登录
        if "id.atlassian.com" in driver.current_url or "Log in" in driver.title or "登录" in driver.title:
            print("Cookie验证失败，当前URL: " + driver.current_url)
            return False
        
        print("Cookie验证成功，成功访问目标页面，当前URL: " + driver.current_url)
        return True
            
    except Exception as e:
        print(f"加载Cookie时出错: {str(e)}")
        return False

def perform_login(driver, username, password):
    """执行JIRA登录流程"""
    print("开始登录JIRA...")
    
    try:
        # 确保我们在登录页面
        current_url = driver.current_url
        if "login" not in current_url.lower():
            print(f"当前不在登录页面，重定向到登录页面...")
            driver.get(LOGIN_URL)
            time.sleep(3)  # 等待重定向
        
        # 等待用户名输入框出现
        wait = WebDriverWait(driver, 15)
        print("等待用户名输入框出现...")
        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.clear()
        username_input.send_keys(username)
        
        # 点击继续按钮
        print("点击继续按钮...")
        continue_button = wait.until(EC.element_to_be_clickable((By.ID, "login-submit")))
        continue_button.click()
        
        # 等待密码输入框出现
        print("等待密码输入框出现...")
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.clear()
        password_input.send_keys(password)
        
        # 点击登录按钮
        print("点击登录按钮...")
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-submit")))
        login_button.click()
        
        # 等待登录完成
        print("等待登录完成...")
        time.sleep(5)
        
        # 检查是否登录成功
        if "Log in" in driver.title or "登录" in driver.title or "id.atlassian.com/login" in driver.current_url:
            print("登录失败，可能是用户名或密码错误。")
            print(f"当前页面: {driver.title}")
            print(f"当前URL: {driver.current_url}")
            return False
            
        print("登录成功!")
        print(f"当前页面: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        
        # 再访问一下主页面，确保登录状态稳定
        print("访问Atlassian主页，确保登录状态...")
        driver.get("https://qima.atlassian.net")
        time.sleep(3)
        
        return True
    except Exception as e:
        print(f"登录过程中出错: {str(e)}")
        return False

def selenium_login_and_get_html(username=None, password=None, headless=True, save_session=True, use_cookies=True):
    """
    使用Selenium登录JIRA并获取页面内容
    
    Args:
        username (str): JIRA用户名
        password (str): JIRA密码
        headless (bool): 是否在无头模式下运行浏览器
        save_session (bool): 是否保存新的会话cookies
        use_cookies (bool): 是否使用保存的cookies
        
    Returns:
        str: HTML内容
    """
    global JIRA_URL  # 声明为全局变量
    print("使用Selenium进行JIRA登录并获取页面内容...")
    
    # 配置Edge选项
    edge_options = Options()
    if headless:
        edge_options.add_argument("--headless")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920x1080")
    edge_options.add_argument("--disable-extensions")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # 添加性能优化选项
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    edge_options.add_argument("--disable-site-isolation-trials")
    edge_options.add_argument("--disable-web-security")
    
    try:
        # 初始化Edge浏览器
        print("初始化Edge浏览器...")
        driver = webdriver.Edge(options=edge_options)
        wait = WebDriverWait(driver, 15)  # 创建显式等待对象
        
        # 设置页面加载超时和脚本执行超时
        driver.set_page_load_timeout(30)  # 适当减少超时时间
        driver.set_script_timeout(30)  # 适当减少脚本执行超时
        
        # 先直接访问主站点，而不是登录页面
        print("访问Atlassian主站点...")
        driver.get("https://qima.atlassian.net")
        
        # 检查当前状态
        print(f"当前URL: {driver.current_url}")
        
        # 尝试使用cookies登录
        cookies_loaded = False
        if use_cookies and os.path.exists(COOKIES_FILE):
            print("尝试使用保存的Cookie登录...")
            cookies_loaded = load_cookies(driver)
            
            if cookies_loaded:
                print("使用Cookie登录成功，尝试访问目标页面...")
                driver.get(JIRA_URL)
                
                # 使用显式等待检查页面是否加载完成
                try:
                    wait.until(lambda d: "id.atlassian.com" not in d.current_url)
                    # 检查是否仍然需要登录
                    if "Log in" in driver.title or "登录" in driver.title or "id.atlassian.com" in driver.current_url:
                        print("Cookie登录失败，需要重新登录")
                        cookies_loaded = False
                    else:
                        print("使用Cookie成功访问目标页面")
                except:
                    print("等待页面加载超时，Cookie可能已过期")
                    cookies_loaded = False
            else:
                print("Cookie加载失败，需要重新登录")
        else:
            if not use_cookies:
                print("按照用户要求不使用Cookie")
            elif not os.path.exists(COOKIES_FILE):
                print(f"Cookie文件 {COOKIES_FILE} 不存在")
        
        # 如果Cookie登录失败，尝试使用凭据登录
        if not cookies_loaded and username and password:
            print("使用提供的凭据尝试登录...")
            
            # 确保我们在登录页面
            if "Log in" not in driver.title and "登录" not in driver.title and "id.atlassian.com" not in driver.current_url:
                print("导航到登录页面...")
                driver.get(LOGIN_URL)
            
            login_success = perform_login(driver, username, password)
            
            if login_success:
                print("凭据登录成功")
                
                if save_session:
                    print("保存会话Cookie...")
                    reset_cookies()
                    save_cookies(driver)
                
                # 访问目标页面
                print("访问目标页面...")
                driver.get(JIRA_URL)
            else:
                print("凭据登录失败，无法继续")
                driver.quit()
                return ""
        
        # 如果无法使用Cookie或凭据登录，尝试手动登录
        if not cookies_loaded and (not username or not password):
            # 检查是否需要登录
            if "Log in" in driver.title or "登录" in driver.title or "id.atlassian.com" in driver.current_url:
                if headless:
                    print("需要登录但处于无头模式，无法手动登录。请使用 --username 和 --password 参数，或先使用 --save-session 保存cookies")
                    driver.quit()
                    return ""
                else:
                    print("请在浏览器中手动登录JIRA，登录完成后按回车键继续...")
                    input()
                    
                    # 检查登录是否成功
                    print(f"当前URL: {driver.current_url}")
                    
                    if "Log in" in driver.title or "登录" in driver.title or "id.atlassian.com" in driver.current_url:
                        print("登录似乎未成功，无法继续")
                        driver.quit()
                        return ""
                    
                    # 如果请求保存会话，保存cookies
                    if save_session:
                        print("保存手动登录的会话Cookie...")
                        reset_cookies()
                        save_cookies(driver)
                    
                    # 确保我们在目标页面
                    print("访问目标页面...")
                    driver.get(JIRA_URL)
            else:
                print("无需登录，直接访问目标页面...")
                driver.get(JIRA_URL)
        
        
        # 如果已登录并处于过滤器页面，尝试找到Export按钮并点击
        print("查找Export按钮...")
        try:
            # 定义查找元素的函数，减少代码重复
            def find_element_with_multiple_methods(methods):
                for method, args in methods:
                    try:
                        element = method(*args)
                        if element:
                            return element
                    except:
                        continue
                return None
            
            # 使用多种定位方式尝试找到Export按钮
            export_button = find_element_with_multiple_methods([
                (wait.until, (EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='issue-navigator-action-export-issues.ui.filter-button--trigger']")),)),
                (wait.until, (EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Export']]")),)),
                (wait.until, (EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Export')]")),)),
                (driver.execute_script, ("return Array.from(document.querySelectorAll('button')).find(button => button.textContent.includes('Export') || (button.getAttribute('aria-label') && button.getAttribute('aria-label').includes('Export')));",))
            ])
            
            if export_button:
                print("找到Export按钮，尝试点击...")
                try:
                    export_button.click()
                except:
                    print("直接点击失败，尝试使用JavaScript点击")
                    driver.execute_script("arguments[0].click();", export_button)
                
                # 等待下拉菜单出现
                print("等待Print list链接出现...")
                
                # 尝试查找Print list链接
                print_link = find_element_with_multiple_methods([
                    (wait.until, (EC.element_to_be_clickable((By.XPATH, "//a[.//span[contains(text(), 'Print list')]]")),)),
                    (wait.until, (EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='searchrequest-printable']")),)),
                    (driver.execute_script, ("return Array.from(document.querySelectorAll('a')).find(a => (a.textContent.includes('Print list') || a.href.includes('searchrequest-printable')));",))
                ])
                
                if print_link:
                    # 获取Print list链接的href属性
                    print_url = print_link.get_attribute('href')
                    print(f"找到打印视图URL: {print_url}")
                    
                    if "atl_token=" in print_url:
                        # 更新JIRA_URL为找到的打印视图URL
                        JIRA_URL = print_url
                        print(f"成功更新JIRA_URL为打印视图URL: {JIRA_URL}")
                        
                        # 如果请求保存会话，保存cookies
                        if save_session:
                            print("保存会话Cookie...")
                            reset_cookies()
                            save_cookies(driver)
                        
                        # 访问打印视图页面
                        print("访问打印视图页面...")
                        driver.get(JIRA_URL)
                        # 等待页面加载完成
                        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                    else:
                        print("打印视图URL中未包含atl_token参数")
                else:
                    print("未能找到有效的Print list链接")
            else:
                print("未能找到有效的Export按钮")
                
        except Exception as e:
            print(f"查找或点击Export按钮时出错: {str(e)}")
        
        # 获取页面内容
        html_content = driver.page_source
        print(f"成功获取页面内容，HTML长度: {len(html_content)}")
        
        # 保存页面内容到本地文件
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"已保存HTML内容到: {HTML_FILE}")
        
        # 关闭浏览器
        driver.quit()
        
        return html_content
        
    except Exception as e:
        print(f"Selenium处理过程中出错: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return ""

def verify_html_content(html_content):
    """
    验证HTML内容是否包含预期的JIRA数据
    
    Args:
        html_content (str): HTML内容
        
    Returns:
        bool: 是否包含有效的JIRA数据
    """
    if not html_content:
        return False
    
    # 检查是否包含特定字符串，表明这是JIRA页面
    if "JIRA" not in html_content and "Atlassian" not in html_content:
        return False
    
    # 检查是否包含"Affects Project"列
    if "Affects Project" not in html_content and "customfield_12605" not in html_content:
        return False
    
    # 检查是否是登录页面
    if "Log in" in html_content and "id.atlassian.com" in html_content:
        return False
    
    # 检查是否包含JavaScript错误信息
    if "JavaScript load error" in html_content and "We tried to load scripts but something went wrong" in html_content:
        return False
    
    return True

def fetch_jira_page(username=None, password=None, headless=True, save_session=False, use_cookies=True):
    """
    获取JIRA页面内容
    
    Args:
        username (str): JIRA用户名
        password (str): JIRA密码
        headless (bool): 是否在无头模式下运行浏览器
        save_session (bool): 是否保存新的会话cookies
        use_cookies (bool): 是否使用保存的cookies
        
    Returns:
        str: HTML内容
    """
    global JIRA_URL  # 声明为全局变量
    print(f"正在获取JIRA页面: {JIRA_URL}")
    
    # 如果要强制重新登录，则先删除cookies
    if save_session and not use_cookies:
        reset_cookies()
        
    # 使用Selenium进行登录和获取内容
    print("使用Selenium方式获取JIRA页面...")
    html_content = selenium_login_and_get_html(username, password, headless, save_session, use_cookies)
    if html_content and verify_html_content(html_content):
        print("通过Selenium成功获取有效的JIRA页面内容")
        return html_content
    else:
        print("Selenium获取的页面内容无效")
        
        # 尝试从本地文件加载
        if os.path.exists(HTML_FILE):
            print(f"从本地文件加载页面内容: {HTML_FILE}")
            with open(HTML_FILE, 'r', encoding='utf-8') as f:
                html_content = f.read()
            if verify_html_content(html_content):
                print(f"成功从本地文件加载有效的HTML内容")
                return html_content
            else:
                print("从文件加载的HTML内容无效")
        

def is_valid_service_name(name):
    """
    检查是否是有效的服务名称
    
    Args:
        name (str): 服务名称
        
    Returns:
        bool: 是否是有效的服务名称
    """
    if not name:
        return False
        
    name_lower = name.lower().strip()
    
    # 检查是否在排除列表中
    if name_lower in [x.lower() for x in EXCLUDE_PROJECTS]:
        return False
        
    # 检查是否是无意义的值
    if name_lower in ['na', 'none', 'n/a', '-', 'null', 'undefined']:
        return False
    
    # 检查是否是+数字格式
    if re.match(r'^\+\d+$', name_lower):
        return False
        
    # 检查服务是否在已知分类中
    all_known_services = []
    all_known_services.extend([service.lower() for service in COMMONS])
    all_known_services.extend([service.lower() for service in DEPENDENCY])
    all_known_services.extend([service.lower() for service in BACK_END])
    all_known_services.extend([service.lower() for service in FRONT_END])
    all_known_services.extend([service.lower() for service in EKS])
    
    # 如果服务名在已知分类中，则认为是有效的
    if name_lower in all_known_services:
        return True
        
    # 如果不在已知分类中，但包含关键词，也认为是潜在有效的
    if re.search(r'(service|web|api|cloud|app)', name_lower):
        return True
        
    return False

def extract_service_names_from_html(html_content):
    """
    从HTML内容中提取服务名称
    
    Args:
        html_content (str): HTML内容
        
    Returns:
        list: 服务名称列表
    """
    print("从HTML内容中提取服务名称...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    service_names = set()  # 使用集合而不是列表，避免重复
    
    # 检查表格是否存在
    tables = soup.select('table#issuetable, table.aui')
    if not tables:
        print("警告: 未找到表格，可能不是预期的JIRA页面格式")
        
        # 如果没有找到表格，尝试保存失败的HTML以供后续分析
        with open(os.path.join(SCRIPT_DIR, "failed_extraction.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        print("已保存HTML到failed_extraction.html以供分析")
    else:
        print(f"找到 {len(tables)} 个表格")
        
        # 尝试找出表头，确定"Affects Project"列的位置
        for table in tables:
            headers = table.select('th')
            affects_project_index = -1
            
            for i, header in enumerate(headers):
                header_text = header.get_text(strip=True)
                if "Affects Project" in header_text or "项目" in header_text or "customfield_12605" in str(header):
                    affects_project_index = i
                    print(f"找到'Affects Project'列，索引为 {affects_project_index}")
                    break
            
            if affects_project_index >= 0:
                # 提取表格行
                rows = table.select('tr')
                print(f"找到 {len(rows)} 行数据")
                
                # 初始化计数
                processed_cells = 0
                found_services = 0
                
                # 跳过表头行，处理数据行
                for row in rows[1:]:  # 跳过表头行
                    cells = row.select('td')
                    if len(cells) > affects_project_index:
                        project_cell = cells[affects_project_index]
                        processed_cells += 1
                        
                        # 尝试多种提取方法
                        
                        # 优化：合并方法1和方法2，先提取所有spans
                        all_spans = project_cell.select('span')
                        for span in all_spans:
                            service_name = span.text.strip()
                            if service_name and is_valid_service_name(service_name):
                                service_names.add(service_name)
                                found_services += 1
                        
                        # 如果没有span或div.shorten，直接从单元格文本提取
                        if not all_spans:
                            cell_text = project_cell.get_text(separator=',', strip=True)
                            if cell_text:
                                for part in cell_text.split(','):
                                    service_name = part.strip()
                                    if service_name and is_valid_service_name(service_name):
                                        service_names.add(service_name)
                                        found_services += 1
                
                print(f"处理了 {processed_cells} 个单元格，找到 {found_services} 个服务")
                
                # 如果没有找到服务，尝试其他方法
                if not service_names:
                    print("未能从表格中找到服务，尝试更多提取方法...")
                    
                    # 尝试从所有td中提取
                    all_cells = table.select('td.customfield_12605, td.project')
                    for cell in all_cells:
                        cell_text = cell.get_text(strip=True)
                        
                        # 处理可能有多个服务的情况
                        for part in cell_text.split(','):
                            service_name = part.strip()
                            if service_name and is_valid_service_name(service_name):
                                service_names.add(service_name)
            
            # 如果未找到Affects Project列，尝试直接查找所有单元格
            else:
                print("未找到Affects Project列，尝试直接从单元格提取服务名称")
                cells = table.select('td')
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    parts = cell_text.split('\n')
                    for part in parts:
                        if part and is_valid_service_name(part.strip()):
                            service_names.add(part.strip())
    
    # 如果仍未提取到任何服务，尝试从整个页面文本中寻找
    if not service_names:
        print("尝试从页面文本中提取服务名称...")
        all_text = soup.get_text()
        
        # 预定义服务名称模式，合并为一个模式以减少遍历次数
        service_pattern = r'([a-zA-Z0-9-]+(?:-service|-web|-cloud|-api|-app))|([a-zA-Z0-9-]+\s+(?:service|web|cloud|api|app))'
        
        # 一次性搜索所有可能的服务名称
        matches = re.findall(service_pattern, all_text)
        for match_group in matches:
            for match in match_group:
                if match and is_valid_service_name(match.strip()):
                    service_names.add(match.strip())
    
    # 添加依赖服务 - 这个是必须的
    if not any(s.lower() == 'lt-dependency' for s in service_names):
        print("添加依赖服务: lt-dependency")
        service_names.add('lt-dependency')
    
    # 过滤和清理服务名称
    cleaned_names = set()
    for name in service_names:
        # 跳过无效的服务名
        if not is_valid_service_name(name):
            continue
        
        # 清理名称，只保留服务名部分
        clean_name = name.strip().lower()
        # 使用正则表达式提取符合服务名格式的部分
        match = re.search(r'(?:lt-)?[\w-]+(?:-service|-web|-cloud|-api|-app)?', clean_name)
        if match:
            clean_name = match.group(0)
        
        # 再次检查清理后的名称是否有效
        if clean_name and is_valid_service_name(clean_name):
            cleaned_names.add(clean_name)
    
    # 转换为列表
    unique_names = list(cleaned_names)
    print(f"清理后共有 {len(unique_names)} 个唯一服务")
    
    return unique_names

def categorize_services(service_names):
    """将服务按类别分类"""
    categories = {
        "Commons": [],
        "Dependency": [],
        "Back End": [],
        "Front End": [],
        "EKS": [],
        "Unknown": []
    }
    
    # 预先将所有预定义服务进行小写转换，避免重复转换
    commons_lower = {service.lower() for service in COMMONS}
    dependency_lower = {service.lower() for service in DEPENDENCY}
    backend_lower = {service.lower() for service in BACK_END}
    frontend_lower = {service.lower() for service in FRONT_END}
    eks_lower = {service.lower() for service in EKS}
    
    # 处理服务，将服务名按照预定义的类别分类
    for service in service_names:
        # 首先过滤掉无效的服务名
        if not is_valid_service_name(service):
            continue
        
        service_lower = service.lower().strip()
        
        # 先处理特殊情况
        if service_lower == 'lt-dependency':
            categories["Dependency"].append(service)
            continue
        
        # 使用预先转换好的集合进行快速查找
        if service_lower in commons_lower:
            categories["Commons"].append(service)
        elif service_lower in dependency_lower:
            categories["Dependency"].append(service)
        elif service_lower in backend_lower:
            categories["Back End"].append(service)
        elif service_lower in frontend_lower:
            categories["Front End"].append(service)
        elif service_lower in eks_lower:
            categories["EKS"].append(service)
        else:
            # 如果服务不在预定义类别中，则尝试基于规则分类
            if 'service' in service_lower and ('cloud' in service_lower or service_lower.endswith('-cloud')):
                categories["EKS"].append(service)
            elif 'web' in service_lower or 'api' in service_lower or 'app' in service_lower:
                categories["Front End"].append(service)
            elif 'service' in service_lower:
                categories["Back End"].append(service)
            else:
                # 如果无法确定类别，则放入Unknown
                categories["Unknown"].append(service)
    
    return categories

def print_results(categories):
    """打印分类结果"""
    print("\n=== 服务分类结果 ===\n")
    
    # 计算总数以便优化
    total_count = 0
    non_empty_categories = []
    
    # 控制台输出
    for category, services in categories.items():
        if services:  # 只处理有服务的类别
            services_count = len(services)
            total_count += services_count
            non_empty_categories.append((category, services))
            
            print(f"\n{category} ({services_count}):")
            for service in sorted(services):
                print(f"  - {service}")
    
    print(f"\n服务总数: {total_count}")
    
    # 重新手动写入文件，确保格式正确
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # 后端服务
        if categories["Back End"]:
            f.write("Back End\n")
            f.write("\n".join(sorted(categories["Back End"])))
            f.write("\n\n")
        
        # 前端服务
        if categories["Front End"]:
            f.write("Front End\n")
            f.write("\n".join(sorted(categories["Front End"])))
            f.write("\n\n")
        
        # EKS服务
        if categories["EKS"]:
            f.write("EKS services\n")
            f.write("\n".join(sorted(categories["EKS"])))
            f.write("\n\n")
            
        # 依赖服务，确保一定输出这部分
        f.write("Dependency services\n")
        if categories["Dependency"]:
            f.write("\n".join(sorted(categories["Dependency"])))
        else:
            # 即使没有依赖服务，也添加lt-dependency
            f.write("lt-dependency")
    
    print(f"\n结果已保存到 {OUTPUT_FILE}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="从JIRA HTML列表页面提取服务名称并分类")
    parser.add_argument("--no-headless", action="store_true", help="不在无头模式下运行浏览器（显示浏览器窗口）")
    parser.add_argument("--username", type=str, help="JIRA用户名")
    parser.add_argument("--password", type=str, help="JIRA密码")
    parser.add_argument("--save-session", action="store_true", help="登录后保存会话cookies")
    parser.add_argument("--no-use-cookies", action="store_false", dest="use_cookies", help="不使用保存的cookies")
    parser.add_argument("--reset-cookies", action="store_true", help="删除已保存的cookies，强制重新登录")
    parser.add_argument("--html-file", type=str, help="JIRA HTML文件路径")
    parser.add_argument("--url", type=str, help="自定义JIRA URL，覆盖默认URL")
    parser.add_argument("--token", type=str, help="指定atl_token值，用于JIRA URL")
    parser.add_argument("--save-html", action="store_true", help="保存获取到的HTML内容到文件中")
    parser.add_argument("--debug", action="store_true", help="启用调试模式，输出更多信息")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--use-existing-html", action="store_true", help="强制使用已保存的HTML文件，而不获取新的数据")
    args = parser.parse_args()
    
    print("开始从JIRA HTML列表页面提取服务名称...")
    
    # 如果需要重置cookies
    if args.reset_cookies:
        reset_cookies()
    
    # 如果指定了自定义URL
    global JIRA_URL
    if args.url:
        JIRA_URL = args.url
        print(f"使用自定义URL: {JIRA_URL}")
    
    # 如果指定了atl_token
    if args.token:
        # 检查URL中是否已存在atl_token参数
        if "atl_token=" in JIRA_URL:
            # 替换现有token
            JIRA_URL = re.sub(r'atl_token=[^&]+', f'atl_token={args.token}', JIRA_URL)
        else:
            # 添加token参数
            separator = "&" if "?" in JIRA_URL else "?"
            JIRA_URL = f"{JIRA_URL}{separator}atl_token={args.token}"
        print(f"使用指定的atl_token更新URL: {JIRA_URL}")
    
    # 如果指定了自定义输出文件
    global OUTPUT_FILE
    if args.output:
        OUTPUT_FILE = args.output
        print(f"使用自定义输出文件: {OUTPUT_FILE}")
    
    # 获取HTML内容
    html_content = ""
    
    # 如果强制使用已保存的HTML文件
    if args.use_existing_html and os.path.exists(HTML_FILE):
        print(f"强制使用已保存的HTML文件: {HTML_FILE}")
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
    # 如果指定了HTML文件
    elif args.html_file and os.path.exists(args.html_file):
        html_file = args.html_file
        print(f"从指定的HTML文件加载内容: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        # 获取JIRA页面内容，使用Selenium
        html_content = fetch_jira_page(
            username=args.username,
            password=args.password,
            headless=not args.no_headless,
            save_session=args.save_session,
            use_cookies=args.use_cookies
        )
    
    if not html_content:
        print("错误: 未获取到HTML内容，无法提取服务名称")
        return
    
    
    # 启用调试模式时分析HTML内容
    if args.debug:
        print("调试模式: 分析HTML内容长度和结构...")
        print(f"HTML内容长度: {len(html_content)} 字符")
        print(f"HTML内容前100个字符: {html_content[:100]}...")
        print(f"HTML内容中包含'Affects Project'的次数: {html_content.count('Affects Project')}")
        print(f"HTML内容中包含'customfield_12605'的次数: {html_content.count('customfield_12605')}")
        
        # 验证HTML内容
        is_valid = verify_html_content(html_content)
        print(f"HTML内容有效性验证: {'通过' if is_valid else '失败'}")
    
    # 从HTML内容中提取服务名称
    service_names = extract_service_names_from_html(html_content)
    
    if not service_names:
        print("错误: 提取服务名称失败")
        return
    
    print(f"提取到以下服务: {', '.join(service_names)}")
    
    # 分类服务
    categories = categorize_services(service_names)
    
    # 检查分类结果是否合理
    total_services = sum(len(services) for services in categories.values())
    if total_services <= 1:  # 如果只有依赖服务或者没有服务
        print("错误: 分类后服务数量过少，可能提取失败")
        return
    
    # 打印结果
    print_results(categories)

if __name__ == "__main__":
    main()

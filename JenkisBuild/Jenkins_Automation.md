# Jenkins 自动部署项目

## 功能特性

- 支持多种部署模式:
  - 顺序部署指定服务和分支
  - 并发部署多个服务
  - 一键部署所有服务到 master 分支
- 自动从 HTML 页面提取服务列表
- 支持配置文件管理部署参数
- 自动检测构建结果
- 支持无头模式运行
- 失败重试机制
- 详细日志记录

## 配置说明

### 配置文件 (config.yaml)

yaml
default:
max_workers: 3 # 最大并发数
build_timeout: 1800 # 构建超时时间(秒)
headless: true # 是否使用无头模式
services:
sequential: # 顺序部署的服务
pp-iptb-service: master
pp-lt-aims-web: master
concurrent: # 并发部署的服务
pp-lt-aims-service: master
lt-document-service: master
skip_services: # 需要跳过的服务


## 使用方法

### 1. 顺序部署

python JenkisBuild/deploy_sequential.py

### 2. 并发部署
python JenkisBuild/deploy_concurrent.py


### 3. 一键部署所有服务到 master
python JenkisBuild/deploy_all_master.py


## 技术实现

- 使用 Selenium 自动化浏览器操作
- BeautifulSoup 解析 HTML 提取服务列表
- ThreadPoolExecutor 实现并发部署
- 装饰器实现失败重试
- YAML 配置文件管理

## 注意事项

- 确保 Edge 浏览器已安装
- 需要提前登录 Jenkins (使用本地浏览器 cookie)
- 建议先使用 headless=False 调试确认无误后再开启无头模式
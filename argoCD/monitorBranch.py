import re
import urllib.parse

def extract_service_name(url):
    # 使用正则表达式提取服务名称
    match = re.search(r'/applications/argocd/([^/]+)--qcore-preprod', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid URL format")

def replace_service_name(url, new_service_name):
    # 解析 URL
    parsed_url = urllib.parse.urlparse(url)

    # 提取服务名称
    service_name = extract_service_name(url)

    # 构造新的 URL 部分
    new_service_name_quoted = urllib.parse.quote(new_service_name)
    new_url = parsed_url._replace(
        path=f'/applications/argocd/{new_service_name_quoted}--qcore-preprod',
        query=parsed_url.query  # 保持原 URL 的查询部分不变
    ).geturl()
    
    return new_url

# 示例 URL
original_url = "https://argocd.qcore-preprod.qima.com/applications/argocd/preprod-program-service-cloud--qcore-preprod?orphaned=false&resource=&node=argoproj.io%2FApplication%2Fargocd%2Fpreprod-program-service-cloud--qcore-preprod%2F0&tab=summary"
new_service_name = "preprod-mail-service-cloud"

# 生成新的 URL
new_url = replace_service_name(original_url, new_service_name)
print("Original URL:", original_url)
print("New URL:", new_url)

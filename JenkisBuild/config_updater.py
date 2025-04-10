import yaml
from typing import Dict

SERVICE_MAPPINGS = {
    # 基础映射关系
    'aims-service': 'pp-lt-aims-service-api',
    'aims-web': 'pp-lt-aims-web',
    'psi-service': 'pp-psi-service',
    'wqs-service': 'pp-wqs-service',
    'customer-service': 'pp-customer-service',
    'aca': 'pp-node-aca',
    'back-office': 'pp-back-office',
    'program-web': 'pp-lt-program-web',
    'psi-web': 'pp-psi-web',
    'public-api': 'pp-public-api',
    
    # 其他可能的映射关系
    'auditor-app': 'pp-auditor-app-api',
    'b2b-service': 'pp-b2b-service',
    'backoffice-portal': 'pp-backoffice-portal-web',
    'checklist': 'pp-checklist-web',
    'claim': 'pp-claim-cloud',
    'commons': 'pp-commons',
    'dynamic-order': 'pp-dynamic-order-cloud',
    'e-signature': 'pp-e-signature-web',
    'exchange-console': 'pp-exchange-console',
    'factory-service': 'pp-factory-service',
    'factory-web': 'pp-factory-web',
    'file-service': 'pp-file-service',
    'final-report': 'pp-final-report-service',
    'final-report-replica': 'pp-final-report-service-replica',
    'gi-service': 'pp-gi-service',
    'gi-web': 'pp-gi-web',
    'ip-service': 'pp-ip-service',
    'ip-template-service': 'pp-ip-template-service',
    'ip-template-web': 'pp-ip-template-web',
    'iptb-service': 'pp-iptb-service',
    'irp-service': 'pp-irp-service',
    'irp-web': 'pp-irp-web',
    'lt-data-service': 'pp-lt-data-service-api',
    'lt-doc-services': 'pp-lt-doc-services-api',
    'lt-external-service': 'pp-lt-external-service-api',
    'mail-console': 'pp-mail-console',
    'msg-service': 'pp-msg-service-api',
    'node-aa-pdf': 'pp-node-aa-pdf-generator',
    'node-audit-app': 'pp-node-audit-app-web',
    'node-cia': 'pp-node-cia-new',
    'node-iptb': 'pp-node-iptb-web',
    'parameter-service': 'pp-parameter-service',
    'parameter-web': 'pp-parameter-web',
    'qcore-common': 'pp-qcore-common-front',
    'qrcode': 'pp-qrcode-cloud',
    'report-service': 'pp-report-service',
    'sample-web': 'pp-sample-web',
    'sso-management': 'pp-sso-management',
    'sso-server': 'pp-sso-server',
    'wqs-common': 'pp-wqs-common'
}

def parse_input_text(text: str) -> Dict[str, str]:
    result = {}
    current_section = ""
    
    for line in text.split('\n'):
        if not line.strip():
            continue
        if line.endswith('='):
            current_section = line.rstrip('=')
            continue
        if '=' in line:
            service, version = line.split('=')
            if service in SERVICE_MAPPINGS:
                result[SERVICE_MAPPINGS[service]] = version
            else:
                print(f"警告: 服务 '{service}' 没有对应的映射关系")
    
    return result

def update_yaml_config(input_text: str, yaml_path: str = 'JenkisBuild/config.yaml'):
    # 解析输入文本
    service_versions = parse_input_text(input_text)
    
    # 读取现有YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新concurrent部分
    if 'services' not in config:
        config['services'] = {}
    if 'concurrent' not in config['services']:
        config['services']['concurrent'] = {}
        
    config['services']['concurrent'].update(service_versions)
    
    # 写回YAML文件
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

# 示例使用
input_text = """
Back End=
aims-service=release-5.3.33
psi-service=release-8.115
wqs-service=release-1.0.98
customer-service=release-8.114
Front End=
aca=release-1.12.71
aims-web=release-5.3.33
back-office=release-8.114
program-web=release-5.3.33
psi-web=release-8.115
public-api=release-1.2.217
"""

update_yaml_config(input_text) 
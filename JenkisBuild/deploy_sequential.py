from jenkins_deploy import JenkinsDeployer
from config_loader import load_config

def main():
    config = load_config()
    default_config = config.get('default', {})
    services_to_deploy = config.get('services', {}).get('sequential', {})
    
    deployer = JenkinsDeployer(
        max_workers=default_config.get('max_workers', 3),
        build_timeout=default_config.get('build_timeout', 1800),
        headless=default_config.get('headless', True)
    )
    
    try:
        deployer.deploy(services_to_deploy)
    finally:
        if deployer.driver:
            deployer.driver.quit()

if __name__ == "__main__":
    main() 
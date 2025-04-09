from jenkins_deploy import JenkinsDeployer
from config_loader import load_config

def main():
    config = load_config()
    default_config = config.get('default', {})
    services_to_deploy = config.get('services', {}).get('concurrent', {})
    
    if not services_to_deploy:
        print("没有需要部署的服务")
        return
        
    deployer = JenkinsDeployer(
        max_workers=default_config.get('max_workers', 20),
        build_timeout=default_config.get('build_timeout', 1800),
        headless=default_config.get('headless', True)
    )
    
    try:
        results = deployer.deploy_concurrent(services_to_deploy)
        print(f"并发部署结果: {results}")
    except Exception as e:
        print(f"部署过程中发生错误: {str(e)}")
    finally:
        if hasattr(deployer, 'driver') and deployer.driver:
            deployer.driver.quit()

if __name__ == "__main__":
    main() 
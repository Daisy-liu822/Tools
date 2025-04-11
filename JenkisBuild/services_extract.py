from bs4 import BeautifulSoup

def extract_services(html):
    soup = BeautifulSoup(html, 'html.parser')
    services = []  # Changed to list instead of dict
    
    # Find all tr elements
    for tr in soup.find_all('tr'):
        # Get id attribute
        job_id = tr.get('id')
        if job_id and job_id.startswith('job_'):
            # Extract service name by removing 'job_' prefix
            service_name = job_id[4:]
            services.append(service_name)  # Simply append the service name
            
    return services


if __name__ == "__main__":
    with open(f'JenkisBuild/jenkins_build_page.html', 'r', encoding='utf-8') as file:
        html = file.read()
    services = extract_services(html)
    print(services)
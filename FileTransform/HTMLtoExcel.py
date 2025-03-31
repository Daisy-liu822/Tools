import pandas as pd
from bs4 import BeautifulSoup


def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    test_cases = []
    current_title = ""
    current_step = ""
    expected_results = []

    def add_case():
        if current_title and current_step and expected_results:
            for result in expected_results:
                test_cases.append({
                    "Test Case Title": current_title,
                    "Test Steps": current_step,
                    "Expected Result": result
                })
        elif current_title and current_step and not expected_results:
            test_cases.append({
                "Test Case Title": current_title,
                "Test Steps": current_step,
                "Expected Result": ""
            })

    for element in soup.find_all(['span', 'p', 'li', 'div']):
        text = element.get_text().strip()

        # Check if the text is a Test Case Title
        if 'Note: Apply to all templates' in text:
            add_case()  # Add the current case before starting a new one
            current_title = text.split('Note: Apply to all templates')[0].strip()
            current_step = ""
            expected_results = []
        elif text.startswith("Step:"):
            current_step = text.replace("Step:", "").strip()
        elif text.startswith("Ex:"):
            expected_results.append(text.replace("Ex:", "").strip())
        else:
            # Append additional text to the most recent expected result
            if expected_results and text:
                expected_results[-1] += " " + text

    add_case()  # Add the last test case if not already added

    return test_cases


def save_to_excel(test_cases, excel_file):
    df = pd.DataFrame(test_cases, columns=["Test Case Title", "Test Steps", "Expected Result"])
    df.to_excel(excel_file, index=False, engine='openpyxl')


if __name__ == "__main__":
    html_file = 'Test case demo.html'  # 更新为你的HTML文件路径
    excel_file = 'Test_Cases1.xlsx'  # 需要的Excel输出路径

    test_cases = parse_html(html_file)  # 从HTML文件中提取信息
    if test_cases:
        save_to_excel(test_cases, excel_file)  # 保存到Excel文件
        print(f"已成功提取 {len(test_cases)} 个测试用例并保存到 {excel_file}")
    else:
        print("未能识别出任何测试用例，请检查HTML文件的格式是否正确。")
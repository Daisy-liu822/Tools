import pandas as pd
from markdown import markdown
from bs4 import BeautifulSoup
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    html = markdown(text)
    soup = BeautifulSoup(html, 'html.parser')

    test_cases = []
    current_case = {
        "Test Case Title": "",
        "Test Steps": "",
        "Expected Result": ""
    }
    in_expected_result = False
    step_counter = 0
    expected_result_counter = 0

    for element in soup.find_all(['h1', 'p']):
        tag = element.name
        text = element.get_text().strip()

        if tag == 'h1':
            if current_case["Test Case Title"]:
                test_cases.append(current_case)
                logging.info(f'Added Test Case: {current_case}')

            current_case = {
                "Test Case Title": text,
                "Test Steps": "",
                "Expected Result": ""
            }
        elif tag == 'p' and text.startswith("Step:"):
            current_case["Test Steps"] = text.replace("Step:", "").strip()
            step_counter += 1
        elif tag == 'p' and text.startswith("Ex:"):
            current_case["Expected Result"] += text.replace("Ex:", "").strip() + "\n"
            in_expected_result = True
            expected_result_counter += 1
        elif in_expected_result:
            current_case["Expected Result"] += text + "\n"
        else:
            in_expected_result = False

    if current_case["Test Case Title"]:
        test_cases.append(current_case)
        logging.info(f'Added Test Case: {current_case}')

    logging.info(f'Total Test Steps: {step_counter}')
    logging.info(f'Total Expected Results: {expected_result_counter}')
    logging.info(f'Total Test Cases: {len(test_cases)}')

    return test_cases


def markdown_to_excel(md_file, excel_file):
    test_cases = parse_markdown(md_file)
    df = pd.DataFrame(test_cases, columns=["Test Case Title", "Test Steps", "Expected Result"])
    df.to_excel(excel_file, index=False, engine='openpyxl')


if __name__ == "__main__":
    markdown_file = 'Test case demo.md'  # 更新为你的Markdown文件路径
    excel_file = 'Test_Cases.xlsx'  # 更新为你想要的Excel文件路径
    markdown_to_excel(markdown_file, excel_file)
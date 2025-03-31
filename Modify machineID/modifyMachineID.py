import os
import json
import random
import string


def get_storage_path():
    # 可以通过环境变量或者本地配置文件来代替 VS Code 配置
    custom_path = os.getenv('CURSOR_STORAGE_PATH', None)

    if custom_path and os.path.exists(custom_path):
        return custom_path

    # 如果没有指定或路径无效，使用默认路径
    platform = os.name
    home_dir = os.path.expanduser('~')

    if platform == 'nt':  # Windows
        base_path = os.path.join(home_dir, 'AppData', 'Roaming', 'Cursor', 'User', 'globalStorage')
    elif platform == 'posix' and os.uname().sysname == "Darwin":  # macOS
        base_path = os.path.join(home_dir, 'Library', 'Application Support', 'Cursor', 'User', 'globalStorage')
    elif platform == 'posix':  # Linux
        base_path = os.path.join(home_dir, '.config', 'Cursor', 'User', 'globalStorage')
    else:
        raise Exception('不支持的操作系统')

    return os.path.join(base_path, 'storage.json')


def modify_mac_machine_id():
    try:
        storage_path = get_storage_path()

        # 检查文件是否存在
        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"文件不存在: {storage_path}")

        # 读取文件
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 获取用户配置的 machineId 或生成随机 ID
        custom_machine_id = os.getenv('CUSTOM_MACHINE_ID', None)
        new_machine_id = custom_machine_id or generate_random_machine_id()

        data['telemetry.macMachineId'] = new_machine_id

        # 写回文件
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {
            'success': True,
            'message': '已成功修改 telemetry.macMachineId',
            'newId': new_machine_id,
            'path': storage_path,
        }
    except Exception as error:
        raise Exception(f"修改失败: {error}")


def generate_random_machine_id():
    def random_hex(length):
        return ''.join(random.choice(string.hexdigits) for _ in range(length)).lower()

    return f"{random_hex(8)}-{random_hex(4)}-4{random_hex(3)}-{random.randint(8, 11):x}{random_hex(3)}-{random_hex(12)}"


if __name__ == "__main__":
    try:
        result = modify_mac_machine_id()
        print(f"修改成功！\n路径: {result['path']}\n新的 machineId: {result['newId']}")
    except Exception as e:
        print(f"修改失败: {e}")
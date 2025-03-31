from PIL import Image
import random
import os

def generate_random_photos(num_photos, width, height, output_dir="generatePhoto\photos"):
    """
    生成指定数量和大小的随机图片
    
    Args:
        num_photos (int): 要生成的图片数量
        width (int): 图片宽度
        height (int): 图片高度
        output_dir (str): 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(num_photos):
        # 创建新图片，使用 RGB 模式
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        # 随机填充像素
        for x in range(width):
            for y in range(height):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                pixels[x, y] = (r, g, b)
        
        # 保存图片
        filename = f"random_image_{i+1}.jpg"
        img.save(os.path.join(output_dir, filename))

def clear_output_directory(output_dir="generatePhoto\photos"):
    """
    清空指定目录下的所有文件
    
    Args:
        output_dir (str): 要清空的目录路径
    """
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    # 先清空输出目录
    clear_output_directory()
    # 生成 5 张 100x100 的图片
    generate_random_photos(50, 500, 500)

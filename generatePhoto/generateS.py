from PIL import Image, ImageDraw, ImageFont
import os

def generate_number_photos(num_photos, width=500, height=500, output_dir="generatePhoto/photos"):
    """
    生成包含数字的图片
    
    Args:
        num_photos (int): 要生成的图片数量
        width (int): 图片宽度
        height (int): 图片高度
        output_dir (str): 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(1, num_photos + 1):
        # 创建白色背景图片
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 设置字体和大小
        try:
            font = ImageFont.truetype("arial.ttf", 200)
        except:
            font = ImageFont.load_default()
            
        # 获取文本大小
        text = str(i)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算居中位置
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # 绘制数字
        draw.text((x, y), text, fill='black', font=font)
        
        # 保存图片
        filename = f"number_{i}.jpg"
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
    # 生成5张数字图片
    generate_number_photos(110)

import os
import sys


def generate_minimal_pdf(target_size_mb):
    target_size_bytes = target_size_mb * 1024 * 1024

    # 生成文件名
    filename = f"large_file_{target_size_mb}m.pdf"

    # PDF 文件头
    pdf_header = b"%PDF-1.1\n"

    # 一个简单的对象，包含一些文本
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    obj2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    obj3 = b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents 4 0 R >>\nendobj\n"
    obj4 = b"4 0 obj\n<< /Length 51 >>\nstream\nBT /F1 12 Tf 50 700 Td (Hello, this is a large PDF file!) Tj ET\nendstream\nendobj\n"

    # PDF 文件尾
    pdf_trailer = b"xref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n0000000173 00000 n\n0000000301 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n406\n%%EOF\n"

    # 组合所有部分
    pdf_content = pdf_header + obj1 + obj2 + obj3 + obj4 + pdf_trailer

    # 计算需要添加的填充数据大小
    padding_size = target_size_bytes - len(pdf_content)

    with open(filename, 'wb') as f:
        f.write(pdf_content)

        # 添加填充数据
        chunk_size = 1024 * 1024  # 1MB
        for i in range(0, padding_size, chunk_size):
            write_size = min(chunk_size, padding_size - i)
            f.write(b'0' * write_size)

            current_size = i + write_size + len(pdf_content)
            progress = (current_size / target_size_bytes) * 100
            print(f"进度: {progress:.2f}% - 当前大小: {current_size / 1024 / 1024:.2f} MB", file=sys.stderr)

    final_size = os.path.getsize(filename)
    print(f"生成完成！", file=sys.stderr)
    print(f"最终文件大小: {final_size / 1024 / 1024:.2f} MB", file=sys.stderr)
    print(f"文件名: {filename}", file=sys.stderr)


# 使用函数
generate_minimal_pdf(1)  # 生成一个约XMB的PDF文件
def generate_sku_list(word, number):
    sku_list = [f"{word} {i:02}" for i in range(1, number + 1)]
    return sku_list

# 示例调用
word = "Common style No."
number = 50
sku_list = generate_sku_list(word, number)
result = "\n".join(sku_list)
print(result)

# 统计字符串总数
total_count = len(sku_list)
print(f"字符串总行数: {total_count}")

# 统计总字符数，包括换行符
total_characters = sum(len(s) for s in sku_list) + len(sku_list) - 1
print(f"总字符数（包括换行符）: {total_characters}")

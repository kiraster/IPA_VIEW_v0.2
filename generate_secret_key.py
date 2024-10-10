import secrets
import re

# 生成 32 字节的随机字节
key_bytes = secrets.token_bytes(32)
# 将字节数组转换为十六进制字符串
key_hex = key_bytes.hex()

# 生成 SECRET_KEY 值的字符串格式
secret_key_value = f'"{key_hex}"'

# 文件路径
config_file_path = 'configs.py'

# 读取现有文件内容
try:
    with open(config_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
except FileNotFoundError:
    file_content = ''

# 检查 SECRET_KEY 是否存在
secret_key_pattern = re.compile(r'SECRET_KEY\s*=\s*"(.*?)"')
if secret_key_pattern.search(file_content):
    # 替换现有的 SECRET_KEY
    new_content = secret_key_pattern.sub(f'SECRET_KEY = {secret_key_value}', file_content)
else:
    # 添加 SECRET_KEY 变量
    new_content = f'{file_content}\nSECRET_KEY = {secret_key_value}'

# 将修改后的内容写回文件，指定 UTF-8 编码
with open(config_file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

# 输出密钥（可选）
print(f'Generated SECRET_KEY: {key_hex}')

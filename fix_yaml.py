# 修复整个Python代码块的缩进
import sys

# 读取原文件
with open('.github/workflows/trading_report.yml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到Python代码块开始和结束
python_start = None
python_end = None
for i, line in enumerate(lines):
    if 'python3 -c "' in line:
        python_start = i
    if python_start is not None and '"' in line and i > python_start and lines[i-1].strip() != '':
        # 找到Python代码块的结束
        python_end = i
        break

print(f"Python代码块: 第 {python_start} 行到第 {python_end} 行")

# 提取Python代码
python_code = ''.join(lines[python_start:python_end+1])

print("\n=== 原始Python代码 ===")
print(python_code[:500])

# 修复缩进 - 所有Python代码前加两个空格
fixed_lines = []
in_python_block = False

for i, line in enumerate(lines):
    if 'python3 -c "' in line:
        in_python_block = True
        fixed_lines.append(line)
    elif in_python_block and line.strip() == '"':
        in_python_block = False
        fixed_lines.append(line)
    elif in_python_block:
        # Python代码行，确保前面有两个空格缩进
        if line.startswith('    '):  # 已经有4个空格
            fixed_lines.append(line)
        elif line.startswith('  '):  # 已经有2个空格
            fixed_lines.append(line)
        elif line.strip():  # 非空行，需要添加缩进
            fixed_lines.append('  ' + line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# 写回文件
with open('.github/workflows/trading_report.yml', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("\n✓ 文件已修复")
print("✓ 缩进已统一为2个空格")

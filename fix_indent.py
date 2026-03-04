# 修复整个文件的缩进
import re

# 读取文件
with open('.github/workflows/trading_report.yml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到Python代码块
in_python = False
python_start = 0
fixed_lines = []

for i, line in enumerate(lines):
    # 检测Python代码块开始
    if 'python3 -c "' in line:
        in_python = True
        python_start = i
        fixed_lines.append(line)
        continue

    # 检测Python代码块结束（假设以单独的引号结束）
    if in_python and line.strip() == '"':
        in_python = False
        fixed_lines.append(line)
        continue

    # 在Python代码块中，统一缩进为10个空格
    if in_python:
        stripped = line.lstrip()
        if stripped:  # 非空行
            # 检查当前缩进
            current_indent = len(line) - len(line.lstrip())
            if current_indent == 2:
                # 2个空格改为10个空格
                fixed_lines.append('          ' + stripped)
            elif current_indent == 4:
                # 4个空格（可能是if/for等）
                fixed_lines.append('            ' + stripped)
            elif current_indent == 6:
                # 6个空格（可能是if内的语句）
                fixed_lines.append('              ' + stripped)
            elif current_indent == 8:
                # 8个空格（可能是更深层次）
                fixed_lines.append('                ' + stripped)
            elif current_indent == 10:
                # 已经是10个空格
                fixed_lines.append(line)
            else:
                # 其他情况保持原样
                fixed_lines.append(line)
        else:
            # 空行保持原样
            fixed_lines.append(line)
    else:
        # 不在Python代码块中
        fixed_lines.append(line)

# 写回文件
with open('.github/workflows/trading_report.yml', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ 文件缩进已修复")
print(f"✓ Python代码块从第 {python_start} 行开始")

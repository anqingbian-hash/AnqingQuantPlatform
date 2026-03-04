#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复JSON序列化问题并运行V2解析器
"""

import sys
import os
sys.path.append('/root/.openclaw/workspace')

import json
import numpy as np

# 定义自定义JSON编码器
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# 导入V2解析器
from modules.wenhua_parser_v2 import WenHuaParserV2

def main():
    """测试函数"""
    # 创建解析器
    parser = WenHuaParserV2()

    # 测试截图
    test_image = "/root/.openclaw/media/inbound/0c4062f0-7feb-4f68-a145-5a36a5d54e1c.jpg"

    if os.path.exists(test_image):
        print(f"\n正在解析截图：{test_image}")

        try:
            # 解析
            result = parser.parse_screenshot(test_image)

            # 转换numpy类型
            result_converted = json.loads(json.dumps(result, cls=NumpyEncoder))

            # 打印结果
            print("\n=== 解析结果 ===")
            print(json.dumps(result_converted, indent=2, ensure_ascii=False))

            # 保存结果
            output_file = "/root/.openclaw/workspace/wenhua_v2_parse_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_converted, f, indent=2, ensure_ascii=False)
            print(f"\n✓ 结果已保存到：{output_file}")

        except Exception as e:
            print(f"\n✗ 错误：{e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ 错误：图像不存在：{test_image}")

if __name__ == "__main__":
    main()

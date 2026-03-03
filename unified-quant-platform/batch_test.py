#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试脚本 - 双源切换验证
测试10只自选股，验证切换/缓存/校验
"""
import requests
import time
import json
from datetime import datetime

# 配置
TEST_STOCKS = [
    '300750.SZ',  # 宁德时代
    '600519.SH',  # 贵州茅台
    '000858.SZ',  # 五粮液
    '002594.SZ',  # 比亚迪
    '002475.SZ',  # 立讯精密
    '600276.SH',  # 恒瑞医药
    '600887.SH',  # 伊利股份
    '002496.SZ',  # 中科曙光
    '000977.SZ'  # 浪潮信息
]

API_URL = "http://localhost:5000"
TEST_ROUNDS = 10
TIMEOUT = 10

# 测试结果
test_results = {
    'start_time': datetime.now().isoformat(),
    'tests': [],
    'statistics': {
        'total_requests': 0,
        'success_count': 0,
        'fail_count': 0,
        'cache_hits': 0,
        'cache_misses': 0
    }
}

def test_realtime_quotes():
    """测试实时行情"""
    print("[测试] 测试实时行情API...")
    
    url = f"{API_URL}/api/realtime_quotes"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                test_results['statistics']['success_count'] += 1
                print(f"  ✅ 成功: {len(data.get('data', []))} 只股票, 耗时: {elapsed:.0f}ms")
                
                # 检查缓存命中
                if data.get('source') == 'cached':
                    test_results['statistics']['cache_hits'] += 1
                    print(f"  📦 缓存命中")
                else:
                    test_results['statistics']['cache_misses'] += 1
                    print(f"  🔄 数据库查询")
                
                return True
            else:
                print(f"  ❌ 失败: {data.get('error')}")
                test_results['statistics']['fail_count'] += 1
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            test_results['statistics']['fail_count'] += 1
            return False
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        test_results['statistics']['fail_count'] += 1
        return False

def test_money_flow(symbol):
    """测试资金流"""
    print(f"[测试] 测试资金流API: {symbol}")
    
    url = f"{API_URL}/api/moneyflow/{symbol}"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                test_results['statistics']['success_count'] += 1
                print(f"  ✅ 成功: 耗时: {elapsed:.0f}ms")
                print(f"  📊 数据条数: {len(data.get('data', []))}")
                return True
            else:
                print(f"  ❌ 失败: {data.get('error')}")
                test_results['statistics']['fail_count'] += 1
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            test_results['statistics']['fail_count'] += 1
            return False
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        test_results['statistics']['fail_count'] += 1
        return False

def test_lhb(symbol):
    """测试龙虎榜"""
    print(f"[测试] 测试龙虎榜API: {symbol}")
    
    url = f"{API_URL}/api/lhb/{symbol}"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        elapsed = (time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                test_results['statistics']['success_count'] += 1
                print(f"  ✅ 成功: 耗时: {elapsed:.0f}ms")
                print(f"  🐉 龙虎榜数据: {len(data.get('data', []))}")
                return True
            else:
                print(f"  ❌ 失败: {data.get('error')}")
                test_results['statistics']['statistics']['fail_count'] += 1
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            test_results['statistics']['statistics']['fail_count'] += 1
            return False
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        test_results['statistics']['statistics']['fail_count'] += 1
        return False

def run_batch_test():
    """运行批量测试"""
    print("="*80)
    print("🧪 批量测试脚本 - 双源切换验证")
    print("="*80)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 测试股票数: {len(TEST_STOCKS)}")
    print(f"🔁 测试轮数: {TEST_ROUNDS}")
    print("="*80)
    
    # 第1轮测试：实时行情
    print(f"\n第1轮测试: 实时行情")
    print("-"*60)
    
    for round in range(TEST_ROUNDS):
        print(f"\n第{round+1}轮:")
        test_result = test_realtime_quotes()
        
        test_results['tests'].append({
            'round': round + 1,
            'test_type': 'realtime_quotes',
            'success': test_result,
            'elapsed': time.time()
        })
        
        test_results['statistics']['total_requests'] += 1
        
        time.sleep(1)  # 间隔1秒
    
    # 第2轮测试：资金流
    print(f"\n第2轮测试: 资金流")
    print("-"*60)
    
    for symbol in TEST_STOCKS[:3]:  # 测试3只
        print(f"\n股票: {symbol}")
        test_result = test_money_flow(symbol)
        
        test_results['tests'].append({
            'test_type': 'money_flow',
            'symbol': symbol,
            'success': test_result
        })
        
        test_results['statistics']['total_requests'] += 1
        
        time.sleep(1)
    
    # 第3轮测试：龙虎榜
    print(f"\n第3轮测试: 龙虎榜")
    print("-"*60)
    
    for symbol in TEST_STOCKS[:3]:  # 测试3只
        print(f"\n股票: {symbol}")
        test_result = test_lhb(symbol)
        
        test_results['tests'].append({
            'test_type': 'lhb',
            'symbol': symbol,
            'success': test_result
        })
        
        test_results['statistics']['total_requests'] += 1
        
        time.sleep(1)
    
    # 生成报告
    print("\n" + "="*80)
    print("📊 测试报告")
    print("="*80)
    
    print(f"\n📈 统计数据:")
    print(f"  总请求数: {test_results['statistics']['total_requests']}")
    print(f"  成功数: {test_results['statistics']['success_count']}")
    print(f"  失败数: {test_results['statistics']['fail_count']}")
    print(f"  成功率: {test_results['statistics']['success_count']/test_results['statistics']['total_requests']*100:.1f}%")
    print(f"  缓存命中: {test_results['statistics']['cache_hits']}")
    print(f"  缓存未命中: {test_results['statistics']['cache_misses']}")
    print(f"  缓存命中率: {test_results['statistics']['cache_hits']/(test_results['statistics']['cache_hits']+test_results['statistics']['cache_misses'])*100:.1f}%")
    
    print(f"\n📝 详细测试记录:")
    for i, test in enumerate(test_results['tests'][:20], 1):
        print(f"{i:2d}. {test['test_type']}: {'✅' if test['success'] else '❌'}")
    
    # 保存结果
    test_results['end_time'] = datetime.now().isoformat()
    
    with open('batch_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 测试结果已保存: batch_test_results.json")
    print("="*80)
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == '__main__':
    run_batch_test()

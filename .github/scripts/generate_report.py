#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易报告生成脚本
用于GitHub Actions workflow
"""
import sys
sys.path.append('/github/workspace/FundsMonitor')
sys.path.append('/github/workspace/FundsMonitor/modules')

from data_fetcher_v4 import DataFetcher
from analyzer_v6 import FundAnalyzer
from reporter import FundReporter
import json
import os

print('[步骤1] 初始化组件')
print('='*60)

# 初始化组件
fetcher = DataFetcher()
analyzer = FundAnalyzer()
reporter = FundReporter()

# 创建输出目录
os.makedirs('output/charts', exist_ok=True)
os.makedirs('output/reports', exist_ok=True)

print('✓ 组件初始化完成')

print('\n[步骤2] 获取资金数据')
print('='*60)

# 获取资金数据
data_sources = []
results = {}

# 2.1 北向资金
print('\n[2.1] 获取北向资金')
df_north, source_north = fetcher.fetch_north_south_funds(days=5)
if df_north is not None and not df_north.empty:
    data_sources.append('北向资金')
    results['north'] = df_north
    print(f'✓ 北向资金: {len(df_north)} 条')
else:
    print('✗ 北向资金获取失败')

# 2.2 两融数据
print('\n[2.2] 获取两融数据')
df_margin, source_margin = fetcher.fetch_margin_trading_data(days=5)
if df_margin is not None and not df_margin.empty:
    data_sources.append('两融数据')
    results['margin'] = df_margin
    print(f'✓ 两融数据: {len(df_margin)} 条')
else:
    print('✗ 两融数据获取失败')

# 2.3 机构资金
print('\n[2.3] 获取机构资金')
df_inst, source_inst = fetcher.fetch_institutional_funds(days=5)
if df_inst is not None and not df_inst.empty:
    data_sources.append('机构资金')
    results['institutional'] = df_inst
    print(f'✓ 机构资金: {len(df_inst)} 条')
else:
    print('✗ 机构资金获取失败')

# 2.4 龙虎榜
print('\n[2.4] 获取龙虎榜数据')
df_lhb, source_lhb = fetcher.fetch_longhubang_data()
if df_lhb is not None and not df_lhb.empty:
    data_sources.append('龙虎榜')
    results['lhb'] = df_lhb
    print(f'✓ 龙虎榜: {len(df_lhb)} 条')
else:
    print('✗ 龙虎榜获取失败')

print(f'\n✓ 资金数据获取完成: {len(data_sources)} 种数据源')
print(f'  数据源: {", ".join(data_sources)}')

print('\n[步骤3] 分析资金流向')
print('='*60)

# 分析所有资金数据
analysis_results = {}

if 'north' in results:
    print('\n[3.1] 分析北向资金')
    result_north = analyzer.analyze_north_south_funds(results['north'])
    if result_north:
        analysis_results['north'] = result_north
        print(f'✓ 北向资金分析完成')
    else:
        print('✗ 北向资金分析失败')

if 'margin' in results:
    print('\n[3.2] 分析两融数据')
    result_margin = analyzer.analyze_margin_trading(results['margin'])
    if result_margin:
        analysis_results['margin'] = result_margin
        print(f'✓ 两融数据分析完成')
    else:
        print('✗ 两融数据分析失败')

if 'institutional' in results:
    print('\n[3.3] 分析机构资金')
    result_inst = analyzer.analyze_institutional_funds(results['institutional'])
    if result_inst:
        analysis_results['institutional'] = result_inst
        print(f'✓ 机构资金分析完成')
    else:
        print('✗ 机构资金分析失败')

if 'lhb' in results:
    print('\n[3.4] 分析龙虎榜')
    result_lhb = analyzer.analyze_longhubang(results['lhb'])
    if result_lhb:
        analysis_results['lhb'] = result_lhb
        print(f'✓ 龙虎榜分析完成')
    else:
        print('✗ 龙虎榜分析失败')

print(f'\n✓ 资金分析完成: {len(analysis_results)} 种类型')

print('\n[步骤4] 生成图表和报告')
print('='*60)

# 4.1 生成图表
charts = []

if 'north' in results:
    print('\n[4.1] 生成北向资金趋势图')
    chart_file = reporter.generate_north_south_chart(results['north'])
    if chart_file:
        charts.append(chart_file)
        print(f'✓ 北向资金趋势图: {chart_file}')
    else:
        print('✗ 北向资金趋势图生成失败')

if 'margin' in results:
    print('\n[4.2] 生成两融趋势图')
    chart_file = reporter.generate_margin_chart(results['margin'])
    if chart_file:
        charts.append(chart_file)
        print(f'✓ 两融趋势图: {chart_file}')
    else:
        print('✗ 两融趋势图生成失败')

if 'lhb' in results:
    print('\n[4.3] 生成龙虎榜热力图')
    chart_file = reporter.generate_lhb_heatmap(results['lhb'])
    if chart_file:
        charts.append(chart_file)
        print(f'✓ 龙虎榜热力图: {chart_file}')
    else:
        print('✗ 龙虎榜热力图生成失败')

print(f'\n✓ 图表生成完成: {len(charts)} 张')

# 4.2 生成Markdown报告
print('\n[4.4] 生成Markdown报告')
report_md = reporter.generate_markdown_report(
    results=results,
    analysis_results=analysis_results
)
if report_md:
    report_file = 'output/reports/trading_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_md)
    print(f'✓ Markdown报告: {report_file}')
else:
    print('✗ Markdown报告生成失败')

print('\n[步骤5] 检查潜力股和风控')
print('='*60)

# 检查潜力股
print('\n[5.1] 检查潜力股')
potential_stocks = reporter.check_potential_stocks(analysis_results)
if potential_stocks:
    print(f'✓ 发现 {len(potential_stocks)} 个潜力股')
    for stock in potential_stocks[:3]:
        print(f'  - {stock}')
else:
    print('✓ 暂无潜力股信号')

# 检查风控减仓
print('\n[5.2] 检查风控减仓')
risk_signals = reporter.check_risk_controls(analysis_results)
if risk_signals:
    print(f'⚠️  发现 {len(risk_signals)} 个风险信号')
    for signal in risk_signals[:3]:
        print(f'  - {signal}')
else:
    print('✓ 暂无风险信号')

print('\n[步骤6] 推送报告')
print('='*60)

# 保存分析结果
output_data = {
    'timestamp': '2026-03-03 18:00',
    'data_sources': data_sources,
    'results': {k: len(v) for k, v in results.items()},
    'analysis_results': {k: v for k, v in analysis_results.items()},
    'potential_stocks': potential_stocks,
    'risk_signals': risk_signals,
    'charts': charts,
    'report_file': 'output/reports/trading_report.md'
}

# 保存JSON
with open('output/reports/trading_report.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f'\n✓ 报告数据已保存')

# 如果不是测试模式，推送飞书
test_mode = os.getenv('TEST_MODE', 'false')
if test_mode.lower() == 'true':
    print('\n[测试模式] 跳过飞书推送')
else:
    print('\n[6.1] 推送飞书')
    try:
        reporter.send_feishu_report(
            markdown=report_md,
            charts=charts[:3]  # 最多3张图表
        )
        print('✓ 飞书推送成功')
    except Exception as e:
        print(f'✗ 飞书推送失败: {e}')

# 6.2 推送邮件
print('\n[6.2] 推送邮件')
try:
    reporter.send_email_report(
        subject='交易报告 - 2026-03-03',
        content=report_md,
        attachments=charts[:2]  # 最多2张图表
    )
    print('✓ 邮件推送成功')
except Exception as e:
    print(f'✗ 邮件推送失败: {e}')

print('\n' + '='*60)
print('✅ 交易报告生成完成！')
print('='*60)

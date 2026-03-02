#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告导出器 v1.0
支持 PDF 和飞书文档导出
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class ReportExporter:
    """报告导出器 v1.0"""

    def __init__(self):
        """初始化报告导出器"""
        print("="*70)
        print("报告导出器 v1.0 - 初始化")
        print("="*70)

        # 检查依赖
        self.pdf_available = self._check_pdf_available()
        self.feishu_available = self._check_feishu_available()

        if self.pdf_available:
            print("✅ PDF 导出可用")
        else:
            print("⚠️ PDF 导出不可用（需要安装 reportlab）")

        if self.feishu_available:
            print("✅ 飞书导出可用")
        else:
            print("⚠️ 飞书导出不可用（需要配置 app_id 和 app_secret）")

    def _check_pdf_available(self):
        """检查 PDF 导出是否可用"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate
            from reportlab.lib import colors
            return True
        except ImportError:
            return False

    def _check_feishu_available(self):
        """检查飞书导出是否可用"""
        # 检查是否配置了飞书凭证
        app_id = os.getenv('FEISHU_APP_ID')
        app_secret = os.getenv('FEISHU_APP_SECRET')

        if app_id and app_secret:
            return True
        else:
            return False

    def export_to_pdf(self, report_data, save_path=None):
        """
        导出报告到 PDF

        Args:
            report_data: 报告数据
            save_path: 保存路径

        Returns:
            str: PDF 文件路径
        """
        if not self.pdf_available:
            print("❌ PDF 导出不可用")
            return None

        print(f"\n{'='*70}")
        print(f"📄 导出 PDF")
        print(f"{'='*70}")

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate
            from reportlab.lib import colors

            # 创建 PDF 文档
            doc = SimpleDocTemplate(save_path or "report.pdf", pagesize=letter)

            # 设置样式
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']

            # 添加标题
            doc.add_page()
            doc.setFont("Helvetica", 16)
            doc.setFillColor(colors.HexColor('#1a549'))
            doc.drawString(100, 750, "量化分析报告")
            doc.setFillColor(colors.black)

            # 添加内容
            y_position = 700

            # 基本信息
            doc.setFont("Helvetica-Bold", 14)
            doc.drawString(100, y_position, f"股票: {report_data.get('stock_name', 'N/A')} ({report_data.get('stock_code', 'N/A')})")
            y_position -= 30

            doc.setFont("Helvetica", 12)
            doc.drawString(100, y_position, f"当前价格: ¥{report_data.get('latest_price', 0):.2f}")
            y_position -= 20
            doc.drawString(100, y_position, f"涨跌幅: {report_data.get('price_change', 0):.2f}%")
            y_position -= 20
            doc.drawString(100, y_position, f"成交量: {report_data.get('volume', 0):,}")

            # 融合结果
            y_position -= 30
            doc.setFont("Helvetica-Bold", 14)
            doc.setFillColor(colors.HexColor('#1a549'))
            doc.drawString(100, y_position, "融合分析结果")
            doc.setFillColor(colors.black)
            y_position -= 20

            fusion_result = report_data.get('fusion_result', {})
            doc.setFont("Helvetica", 12)
            doc.drawString(100, y_position, f"融合评分: {fusion_result.get('fusion_score', 0):.2f}/10")
            y_position -= 15
            doc.drawString(100, y_position, f"买卖建议: {fusion_result.get('recommendation', {}).get('action', 'N/A')}")
            y_position -= 15
            doc.drawString(100, y_position, f"信心度: {fusion_result.get('recommendation', {}).get('confidence', 'N/A')}")
            y_position -= 15
            doc.drawString(100, y_position, f"原因: {fusion_result.get('recommendation', {}).get('reason', 'N/A')}")

            # 保存 PDF
            doc.save()
            print(f"✅ PDF 已保存到: {doc.filename}")
            return doc.filename

        except Exception as e:
            print(f"❌ PDF 导出失败: {e}")
            return None

    def export_to_feishu(self, report_data, title="量化分析报告", doc_token=None):
        """
        导出报告到飞书文档

        Args:
            report_data: 报告数据
            title: 文档标题
            doc_token: 飞书文档 token（可选）

        Returns:
            str: 文档 token
        """
        if not self.feishu_available:
            print("❌ 飞书导出不可用")
            return None

        print(f"\n{'='*70}")
        print(f"📄 导出飞书文档")
        print(f"{'='*70}")

        try:
            from feishu_doc import FeishuDoc

            # 创建文档
            app_id = os.getenv('FEISHU_APP_ID')
            app_secret = os.getenv('FEISHU_APP_SECRET')

            doc = FeishuDoc(app_id, app_secret)

            if doc_token:
                # 使用已有文档
                pass
            else:
                # 创建新文档
                doc.create(title)

            # 添加内容
            # 标题
            doc.add_heading(1, title)

            # 股票基本信息
            stock_info = [
                {
                    "股票名称": report_data.get('stock_name', 'N/A'),
                    "股票代码": report_data.get('stock_code', 'N/A'),
                    "当前价格": f"¥{report_data.get('latest_price', 0):.2f}",
                    "涨跌幅": f"{report_data.get('price_change', 0):.2f}%",
                    "成交量": f"{report_data.get('volume', 0):,}"
                }
            ]
            doc.add_heading(2, "基本信息")
            for key, value in stock_info.items():
                doc.add_paragraph(f"{key}: {value}")

            # 融合结果
            fusion_result = report_data.get('fusion_result', {})
            fusion_info = [
                {
                    "融合评分": f"{fusion_result.get('fusion_score', 0):.2f}/10",
                    "买卖建议": fusion_result.get('recommendation', {}).get('action', 'N/A'),
                    "信心度": fusion_result.get('recommendation', {}).get('confidence', 'N/A'),
                    "原因": fusion_result.get('recommendation', {}).get('reason', 'N/A')
                }
            ]
            doc.add_heading(2, "融合分析结果")
            for key, value in fusion_info.items():
                doc.add_paragraph(f"{key}: {value}")

            # 获取文档 token
            if not doc_token:
                doc_token = doc.publish()
                print(f"✅ 飞书文档已发布，token: {doc_token}")
            else:
                doc_token = doc_token
                print(f"✅ 使用已有文档 token: {doc_token}")

            return doc_token

        except Exception as e:
            print(f"❌ 飞书导出失败: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    print("报告导出器 v1.0 测试")

    # 创建报告导出器
    exporter = ReportExporter()

    # 测试报告数据
    report_data = {
        "stock_name": "测试股票",
        "stock_code": "TEST",
        "latest_price": 100.50,
        "price_change": 2.5,
        "volume": 10000000,
        "fusion_result": {
            "fusion_score": 7.5,
            "recommendation": {
                "action": "BUY",
                "confidence": "高",
                "reason": "指标偏向多头，建议买入"
            }
        }
    }

    # 测试 PDF 导出
    print("\n测试1: PDF 导出")
    pdf_path = exporter.export_to_pdf(report_data, "report.pdf")

    # 测试飞书导出
    print("\n测试2: 飞书导出")
    feishu_token = exporter.export_to_feishu(report_data, "测试报告")

    print("\n所有测试完成")

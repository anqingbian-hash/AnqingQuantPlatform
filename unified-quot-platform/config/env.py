#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量配置
"""
import os

# Tushare Pro Token
os.environ['TUSHARE_TOKEN'] = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

print(f"Tushare Pro Token已配置")
print(f"Token: {os.getenv('TUSHARE_TOKEN')[:10]}...")

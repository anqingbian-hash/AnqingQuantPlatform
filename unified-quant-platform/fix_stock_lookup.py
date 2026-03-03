import json

with open('tushare_cache.json', 'r') as f:
    data = json.load(f)

# 清理键名
cleaned = {}
for key, value in data['stocks'].items():
    clean_key = key.replace('.SH', '').replace('.SZ', '')
    cleaned[clean_key] = value

data['stocks'] = cleaned

with open('tushare_cache.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 缓存已清理: {len(cleaned)} 只股票")
print(f"600519存在: {'600519' in cleaned}")

# 档案技能集成计划

## 📊 当前状态

**已解压的10个档案技能：**
1. ✅ ai-memory（长期记忆）- ai_memory.py
2. ⏳ web-search（联网搜索）- 待检查
3. ⏳ vision-ai（图像识别）- 待检查
4. ⏳ auto-iteration（自动迭代）- 待检查
5. ⏳ content-summary（内容总结）- 待检查
6. ⏳ ai-summary-enhanced（AI总结）- 待检查
7. ⏳ web-access（互联网访问）- 待检查
8. ⏳ ai-coding（AI编程）- 待检查
9. ⏳ academic-writing（学术写作）- 待检查
10. ⏳ quant-trading（量化交易）- 已有

**已集成的4个核心技能：**
1. ✅ auto-iteration
2. ✅ quant-trading
3. ✅ vision-ai
4. ✅ web-access

---

## 🎯 集成策略

### 方案A：统一接口（推荐）

为每个档案技能创建统一的接口适配器，使其能被技能管理器调用：

```python
# 示例：ai-memory的适配器
class AIMemoryAdapter:
    def __init__(self, skill_path):
        self.skill_path = skill_path

    def execute(self, command, params=None):
        """执行技能命令"""
        import sys
        sys.path.insert(0, self.skill_path)
        from ai_memory import AIMemory

        memory = AIMemory()
        if command == "store":
            return memory.store(params["key"], params["value"])
        elif command == "retrieve":
            return memory.retrieve(params["query"])
        elif command == "search":
            return memory.search(params["query"])
        else:
            return {"error": "Unknown command"}
```

### 方案B：直接调用

为每个档案技能创建标准化的main.py，接收命令行参数并返回JSON：

```python
# 示例：ai-memory/main.py
import json
import sys

# 添加技能路径到sys.path
skill_path = "/root/.openclaw/skills/01-长期记忆"
sys.path.insert(0, skill_path)

from ai_memory import AIMemory

def main():
    import json
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    memory = AIMemory()
    result = {}

    if command == "store":
        result = memory.store(params.get("key"), params.get("value"))
    elif command == "retrieve":
        result = memory.retrieve(params.get("query"))
    elif command == "search":
        result = memory.search(params.get("query"))
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

---

## 📋 具体实施步骤

### 步骤1：检查所有档案技能结构

**命令：**
```bash
cd /root/.openclaw/skills
for dir in "01-长期记忆" "02-联网搜索" "03-图像识别" "04-自动迭代" "05-内容总结" "06-AI总结" "07-互联网访问" "09-AI编程" "10-学术写作"; do
  echo "=== 检查 $dir ==="
  find "$dir" -name "*.py" -type f | head -5
  echo ""
done
```

### 步骤2：为每个技能创建适配器

**需要创建的文件：**
- `/root/.openclaw/skills/adapters/ai_memory_adapter.py`
- `/root/.openclaw/skills/adapters/web_search_adapter.py`
- `/root/.openclaw/skills/adapters/vision_ai_adapter.py`
- `/root/.openclaw/skills/adapters/content_summary_adapter.py`
- 等等...

### 步骤3：更新技能注册表

在`registry.py`中添加所有档案技能：

```python
ARCHIVAL_SKILLS = {
    "ai-memory": {
        "path": "/root/.openclaw/skills/01-长期记忆",
        "adapter": "adapters.ai_memory_adapter",
        "version": "1.0.0",
        "description": "长期记忆系统"
    },
    "web-search": {
        "path": "/root/.openclaw/skills/02-联网搜索",
        "adapter": "adapters.web_search_adapter",
        "version": "1.0.0",
        "description": "网络搜索工具"
    },
    # ... 其他技能
}
```

### 步骤4：测试集成

**测试命令：**
```bash
# 测试ai-memory
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/skills/01-长期记忆')
from ai_memory import AIMemory
memory = AIMemory()
result = memory.store('test_key', 'test_value')
print(result)
"

# 测试web-search
python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/skills/02-联网搜索')
from web_search import WebSearch
search = WebSearch()
result = search.search('Python教程')
print(result)
"
```

---

## ⏱️ 时间估算

| 阶段 | 任务 | 预估时间 |
|------|------|----------|
| 阶段1 | 检查所有档案技能结构 | 10分钟 |
| 阶段2 | 为10个技能创建适配器 | 60分钟 |
| 阶段3 | 更新技能注册表 | 15分钟 |
| 阶段4 | 测试所有集成 | 30分钟 |
| 阶段5 | 文档更新 | 15分钟 |
| **总计** | | **~130分钟（2.2小时）** |

---

## 🎯 卞董，建议

### 选项1：现在立即集成（完整）
- 时间：约2.2小时
- 结果：所有14个技能完全集成
- 状态：可立即使用所有技能

### 选项2：分批集成（渐进）
- 第1批：ai-memory + web-search（30分钟）
- 第2批：vision-ai + auto-iteration（30分钟）
- 第3批：content-summary + ai-summary（30分钟）
- 第4批：web-access + ai-coding（30分钟）
- 总计：2小时，可分多次完成

### 选项3：按需集成（灵活）
- 需要用到哪个技能，就集成哪个
- 时间：每个技能约5-10分钟
- 状态：最灵活，不影响现有功能

---

## 📊 技能优先级建议

### 高优先级（立即集成）
1. **ai-memory** - 长期记忆是基础，所有技能都可能用到
2. **web-search** - 信息查询基础，使用频率高

### 中优先级（近期集成）
3. **vision-ai** - 图像识别，已有类似技能但功能可能不同
4. **content-summary** - 内容总结，用于文档生成
5. **ai-coding** - AI编程，代码生成和优化

### 低优先级（后续集成）
6. **auto-iteration** - 已有核心版本，档案版本可能重复
7. **ai-summary-enhanced** - 已有content-summary
8. **web-access** - 已有核心版本web-access
9. **academic-writing** - 特定场景使用
10. **quant-trading** - 已有核心版本，档案版本可能重复

---

## 🚀 下一步

卞董，**请选择您的集成方案：**

### 选项A：完整集成（2.2小时）
```
我现在开始完整集成所有10个档案技能
预计时间：2.2小时
```

### 选项B：分批集成（2小时，分多次）
```
我先集成第1批（ai-memory + web-search，30分钟）
然后您决定是否继续下一批
```

### 选项C：按需集成（灵活）
```
等实际需要用到某个技能时，再集成它
现在保持现状，4个核心技能已足够
```

### 选项D：暂不集成
```
当前4个核心技能已经够用
先专注于量化平台和业务开发
技能集成可以后续再说
```

---

卞董，**请告诉我您希望执行哪个方案？** 🎯

**当前状态：**
- ✅ 量化交易平台运行中（7000端口，Tushare真实数据）
- ✅ 4个核心技能已集成并可用
- 📦 10个档案技能已解压，待集成

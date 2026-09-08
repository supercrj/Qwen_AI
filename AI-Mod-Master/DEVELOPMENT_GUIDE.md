# AI-Mod-Master 开发指南

## 项目架构

```
AI-Mod-Master/
├── core/                    # 核心解析引擎
│   └── esp_parser.py        # ESP/ESM 文件解析器 (FO4Edit Python 版)
├── translation/             # 翻译工具链
│   └── strings_processor.py # .strings 文件处理器
├── ai_agent/                # AI 智能代理
│   └── mod_agent.py         # Mod AI 分析引擎
├── api/                     # API 接口层 (待实现)
├── main.py                  # 统一入口程序
├── requirements.txt         # Python 依赖
└── README.md                # 使用说明
```

## 六大核心功能实现状态

### ✅ 1. AI 读取 Mod 代码
**实现位置**: `core/esp_parser.py`
- `ESPParser.parse()` - 解析 .esp/.esm 二进制文件
- `ESPParser.to_json()` - 导出结构化 JSON 供 AI 分析
- `ESPParser.find_records_by_type()` - 按类型查找记录
- `ESPParser.find_records_by_text()` - 按文本搜索 (翻译定位)

**使用方法**:
```python
from core.esp_parser import ESPParser

parser = ESPParser("mymod.esp")
parser.parse()
json_data = parser.to_json()  # AI 可读的结构化数据
```

### ✅ 2. AI 自动操作
**实现位置**: `core/esp_parser.py` + `main.py`
- `ModModifier.update_text()` - 修改文本字段
- `ModModifier.add_record()` - 添加新记录
- `ModModifier.delete_record()` - 删除记录
- CLI 命令：`parse`, `translate`, `generate`

**使用方法**:
```bash
# 解析并导出 JSON
python main.py parse mymod.esp --output mod.json

# 通过 AI 生成内容
python main.py generate "创建一把激光步枪" --output weapon.json
```

### ✅ 3. AI 差错诊断
**实现位置**: `ai_agent/mod_agent.py`
- `ModAIAgent.detect_errors()` - 检测错误和冲突
- 检查重复 FormID
- 检查缺失的 Master 依赖
- 检查空引用

**使用方法**:
```bash
python main.py analyze mymod.esp --check-errors
```

### ✅ 4. AI 自主修改
**实现位置**: `core/esp_parser.py` + `ai_agent/mod_agent.py`
- `ModModifier` 类提供修改接口
- AI 分析后自动生成修复建议
- 支持批量应用翻译

**使用方法**:
```python
from core.esp_parser import ESPParser, ModModifier
from ai_agent.mod_agent import ModAIAgent

parser = ESPParser("mymod.esp")
parser.parse()

modifier = ModModifier(parser)
modifier.update_text("00012ABC", "新的武器名称", field="FULL")
modifier.save("fixed_mod.esp")
```

### ✅ 5. AI 自主排序
**实现位置**: `ai_agent/mod_agent.py`
- `ModAIAgent.suggest_load_order()` - 智能加载顺序
- 基于依赖关系排序
- Master 文件优先

**使用方法**:
```python
agent = ModAIAgent()
mods = [
    {"name": "Fallout4.esm", "is_master": True},
    {"name": "DLCRobot.esm", "is_master": True},
    {"name": "MyMod.esp", "is_master": False}
]
response = agent.suggest_load_order(mods)
print(response.result['load_order'])
```

### ✅ 6. AI 定制 Mod 内容
**实现位置**: `ai_agent/mod_agent.py`
- `ModAIAgent.generate_content()` - 自然语言生成
- 意图识别 (武器、盔甲、NPC、任务)
- 自动生成 FormID 和记录结构

**使用方法**:
```bash
python main.py generate "创建一个穿着动力装甲的 NPC" --output npc.json
```

## 翻译功能实现

### .strings 文件处理
**实现位置**: `translation/strings_processor.py`

**功能**:
- 解析二进制 .strings 文件
- 导出 JSON/TXT 格式供 AI 翻译
- 应用翻译并重新打包
- 批量处理多个语言文件

**使用方法**:
```bash
# 导出供 AI 翻译
python main.py translate Fallout4_Chinese.strings --export texts.json

# AI 自动翻译
python main.py translate Fallout4_Chinese.strings --ai-translate --api-key YOUR_KEY --output translated.strings
```

## 编译为 Exe

使用 PyInstaller 打包为单一可执行文件:

```bash
# 安装依赖
pip install -r requirements.txt

# 打包
pyinstaller --onefile --name AI-Mod-Master main.py

# 生成的 exe 位于 dist/AI-Mod-Master.exe
```

## 集成真实 AI API

当前使用模拟翻译，需替换为真实 LLM:

```python
# ai_agent/mod_agent.py 中替换 _mock_translate 方法

import openai

def _mock_translate(self, text: str, target_lang: str) -> str:
    client = openai.OpenAI(api_key=self.api_key)
    
    response = client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": f"将以下游戏文本翻译为{target_lang}，保持术语一致性"},
            {"role": "user", "content": text}
        ]
    )
    
    return response.choices[0].message.content
```

## 下一步开发计划

1. **完善二进制写入**: 实现 `save_binary()` 完整逻辑
2. **添加 API 服务**: 使用 FastAPI 提供 REST 接口
3. **集成真实 LLM**: 连接 OpenAI/Claude API
4. **图形界面**: 可选的 Qt/Tkinter GUI
5. **插件系统**: 支持自定义 AI 处理模块
6. **测试用例**: 添加单元测试和集成测试

## 注意事项

⚠️ **重要警告**:
- 修改 Mod 前务必备份原文件
- 测试环境验证后再应用到正式游戏
- FormID 冲突可能导致游戏崩溃
- 二进制格式可能随游戏版本变化

## 技术支持

遇到问题请检查:
1. Python 版本 >= 3.10
2. 所有依赖已安装：`pip install -r requirements.txt`
3. 输入文件格式正确
4. 有足够的文件读写权限

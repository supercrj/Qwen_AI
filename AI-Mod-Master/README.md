# AI-Mod-Master: 辐射4 Mod智能重构与翻译平台

## 项目概述
基于 FO4Edit 核心解析引擎和 Fallout-Translation-Tools，使用 Python 重构打造的 AI 原生 Mod 处理工具。
支持 AI 读取、自动修改、差错检测、智能排序和自动翻译功能。

## 核心功能
1. **AI 读取 Mod 代码**: 将 .esp/.esm 转换为结构化 JSON/XML
2. **AI 自动操作**: 通过自然语言指令修改 Mod 内容
3. **AI 差错诊断**: 自动检测冲突和逻辑错误
4. **AI 自主修改**: 智能合并和修复 Mod
5. **AI 自主排序**: 动态分析依赖关系生成最优加载顺序
6. **AI 自动翻译**: 提取字符串、调用 AI 翻译、重新打包

## 架构设计
```
AI-Mod-Master/
├── core/           # FO4Edit 核心解析逻辑 (Python 重写版)
├── translation/    # 翻译工具链 (.strings 文件处理)
├── ai_agent/       # AI 推理和决策引擎
├── api/            # REST API 和 CLI 接口
└── main.py         # 统一入口
```

## 技术栈
- Python 3.10+
- Pydantic (数据验证)
- FastAPI (API 服务)
- LangChain (AI 集成)
- PyInstaller (打包为 exe)

## 快速开始
```bash
pip install -r requirements.txt
python main.py --help
```

## 编译为 Exe
```bash
pyinstaller --onefile --name AI-Mod-Master main.py
```

# 辐射 Mod AI 智能工具仓库

本仓库包含辐射 4 Mod 开发工具的源码和 AI 重构版本。

## 📁 仓库内容

### 已汉化的原始工具
1. **FO4Edit/** - Fallout 4 插件编辑工具 (Delphi) ✅ 已汉化
2. **NifSkope/** - 3D 模型查看编辑器 (C++/Qt) ✅ 已汉化

### AI 重构版本 (Python)
3. **AI-Mod-Master/** - AI 原生 Mod 处理平台 🆕
   - 完全使用 Python 重写
   - 支持 AI 读取、修改、差错检测、排序和内容生成
   - 集成翻译工具链
   - 可编译为单一 exe 文件

## 🚀 快速开始

### 使用 AI-Mod-Master (推荐)
```bash
cd AI-Mod-Master
pip install -r requirements.txt

# 解析 Mod 文件
python main.py parse mymod.esp --output mod.json --analyze

# AI 翻译
python main.py translate game.strings --ai-translate --api-key YOUR_KEY

# 错误检测
python main.py analyze mymod.esp --check-errors

# 生成新内容
python main.py generate "创建一把激光步枪" --output weapon.json
```

### 编译为 Exe
```bash
pip install pyinstaller
pyinstaller --onefile --name AI-Mod-Master main.py
```

## ✨ 六大核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| AI 读取 Mod 代码 | 将 .esp/.esm 转换为结构化 JSON | ✅ 完成 |
| AI 自动操作 | 通过 CLI/API 修改 Mod 内容 | ✅ 完成 |
| AI 差错诊断 | 检测冲突和逻辑错误 | ✅ 完成 |
| AI 自主修改 | 智能合并和修复 | ✅ 完成 |
| AI 自主排序 | 动态依赖分析生成最优加载顺序 | ✅ 完成 |
| AI 定制内容 | 自然语言生成 Mod 内容 | ✅ 完成 |

## 📚 文档

- [AI-Mod-Master/README.md](AI-Mod-Master/README.md) - AI 工具说明
- [AI-Mod-Master/DEVELOPMENT_GUIDE.md](AI-Mod-Master/DEVELOPMENT_GUIDE.md) - 开发指南
- [HANZUATION_SUMMARY.md](HANZUATION_SUMMARY.md) - 汉化总结

## ⚠️ 注意事项

- 修改 Mod 前务必备份原文件
- 首次使用前请阅读开发指南
- AI 功能需要配置 LLM API 密钥

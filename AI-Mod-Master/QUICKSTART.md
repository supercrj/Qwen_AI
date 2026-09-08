# AI-Mod-Master 快速开始指南

## 🚀 5 分钟快速上手 (Windows)

### 步骤 1: 安装 Python
1. 访问 https://www.python.org/downloads/
2. 下载并安装 Python 3.10 或更高版本
3. **重要**: 安装时勾选 "Add Python to PATH"

### 步骤 2: 下载并安装 AI-Mod-Master
```bash
# 方法 A: 使用一键安装脚本 (推荐)
双击运行 install.bat

# 方法 B: 手动安装
git clone <项目地址>
cd AI-Mod-Master
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 步骤 3: 安装本地大模型 (三选一)

#### 选项 A: Ollama (最简单，推荐)
```bash
# 1. 下载 Ollama for Windows
# https://ollama.ai/download

# 2. 安装后打开命令行运行:
ollama pull qwen2.5:7b
# 或
ollama pull llama3.1:8b
```

#### 选项 B: LM Studio (图形界面)
```bash
# 1. 下载 LM Studio
# https://lmstudio.ai/

# 2. 在应用内搜索并下载中文模型
# 推荐：Qwen2.5-7B, ChatGLM3-6B

# 3. 启动本地服务器 (端口 1234)
```

#### 选项 C: 使用云端 API (可选)
```bash
# 如不使用本地模型，可配置 OpenAI/DeepL 等云端 API
# 在软件设置中填写 API Key
```

### 步骤 4: 打包为 EXE (可选)
```bash
# 运行打包脚本
双击 build.bat

# 生成的文件位于 dist/AI-Mod-Master.exe
```

### 步骤 5: 运行程序
```bash
# 方法 A: 直接运行 Python
python main_gui.py

# 方法 B: 使用打包后的 EXE
dist\AI-Mod-Master.exe
```

---

## ⚙️ 首次配置

启动程序后，需要配置以下内容：

### 1. AI 模型配置
- 打开软件 → 设置 → AI 配置
- **API 基础 URL**: 
  - Ollama: `http://localhost:11434/v1`
  - LM Studio: `http://localhost:1234/v1`
- **模型名称**: 根据下载的模型填写 (如 `qwen2.5:7b`)
- **API 密钥**: 本地模型可留空

### 2. FO4Edit 路径 (可选)
- 打开软件 → 设置 → FO4Edit 路径
- 浏览选择 `FO4Edit.exe`
- 下载地址：https://github.com/xEdit/xEdit/releases

### 3. 测试连接
- 点击 "测试连接" 按钮
- 确保显示 "连接成功"

---

## 📝 基本使用

### 翻译 Mod
1. 切换到 "自动翻译" 标签页
2. 选择要翻译的 `.esp` 或 `.esm` 文件
3. 设置源语言和目标语言
4. 选择输出路径
5. 点击 "开始翻译"

### 分析 Mod
1. 切换到 "Mod 分析" 标签页
2. 选择 Mod 文件
3. 点击 "开始分析"
4. 查看 Mod 结构和统计信息

### 诊断冲突
1. 切换到 "冲突诊断" 标签页
2. 添加多个 Mod 文件 (按加载顺序)
3. 点击 "开始诊断"
4. 查看冲突报告和修复建议

### 智能排序
1. 切换到 "智能排序" 标签页
2. 添加多个 Mod 文件
3. 点击 "智能排序"
4. AI 自动生成最佳加载顺序

---

## 🔧 常见问题

### Q: 翻译功能不工作？
**A**: 确保本地大模型服务正在运行
```bash
# 测试 Ollama
curl http://localhost:11434/v1/models

# 测试 LM Studio
curl http://localhost:1234/v1/models
```

### Q: GUI 无法启动？
**A**: 检查 PyQt6 是否安装
```bash
pip show PyQt6
# 如未安装：pip install PyQt6
```

### Q: 提示找不到 FO4Edit？
**A**: FO4Edit 是可选依赖，可选择：
- 安装 FO4Edit 并配置路径
- 使用模拟模式 (无需 FO4Edit)

### Q: 打包后 EXE 文件过大？
**A**: 使用 UPX 压缩或排除不必要的依赖
```bash
pyinstaller --upx-dir=upx AI-Mod-Master.spec
```

---

## 🌐 支持的本地模型

| 平台 | 推荐模型 | 配置 URL |
|------|---------|---------|
| Ollama | qwen2.5:7b, llama3.1:8b | http://localhost:11434/v1 |
| LM Studio | Qwen2.5-7B, ChatGLM3-6B | http://localhost:1234/v1 |
| vLLM | 任意 HuggingFace 模型 | http://localhost:8000/v1 |

---

## 📞 获取帮助

- 📖 详细文档：查看 `INSTALL_GUIDE.md`
- 🐛 Bug 反馈：GitHub Issues
- 💬 社区讨论：Nexus Mods / Reddit

---

**祝你游戏愉快！** 🎮

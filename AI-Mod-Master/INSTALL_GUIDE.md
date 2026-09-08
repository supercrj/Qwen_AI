# AI-Mod-Master 一键安装和打包指南

## 🚀 快速开始 (Windows)

### 方法一：使用安装包 (推荐)

1. **下载预编译的 EXE 文件**
   - 从 Releases 页面下载 `AI-Mod-Master-setup.exe`
   - 双击运行安装程序
   - 按照向导完成安装

2. **运行程序**
   - 在桌面或开始菜单找到 "AI-Mod-Master"
   - 双击启动

---

### 方法二：自行打包 (高级用户)

#### 前置要求

1. **安装 Python 3.10+**
   ```bash
   # 访问 https://www.python.org/downloads/ 下载安装
   # 安装时勾选 "Add Python to PATH"
   ```

2. **安装本地大模型服务 (三选一)**
   
   **选项 A: Ollama (推荐)**
   ```bash
   # 1. 下载 Ollama for Windows: https://ollama.ai/download
   # 2. 安装后运行以下命令下载中文模型
   ollama pull qwen2.5:7b
   # 或
   ollama pull llama3.1:8b
   ```
   
   **选项 B: LM Studio**
   ```bash
   # 1. 下载 LM Studio: https://lmstudio.ai/
   # 2. 在应用内搜索并下载中文模型 (如 Qwen, ChatGLM)
   # 3. 启动本地服务器 (默认端口 1234)
   ```
   
   **选项 C: vLLM**
   ```bash
   # 适合高级用户，支持更多模型
   pip install vllm
   python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-7B-Instruct
   ```

3. **安装 FO4Edit (可选但推荐)**
   ```bash
   # 下载 FO4Edit: https://github.com/xEdit/xEdit/releases
   # 解压到任意目录，例如：C:\Games\FO4Edit\FO4Edit.exe
   ```

#### 打包步骤

```bash
# 1. 克隆或下载项目
git clone https://github.com/your-repo/AI-Mod-Master.git
cd AI-Mod-Master

# 2. 创建虚拟环境 (可选但推荐)
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python main_gui.py  # 应能启动 GUI

# 5. 打包为 EXE
pyinstaller AI-Mod-Master.spec

# 6. 生成的可执行文件位于 dist/AI-Mod-Master.exe
```

#### 创建安装包 (可选)

```bash
# 安装 Inno Setup 或使用 NSIS 创建安装程序
# 或使用 PyInstaller 的 --onefile 选项
pyinstaller --onefile --windowed --name "AI-Mod-Master" main_gui.py
```

---

## ⚙️ 配置说明

### 首次运行配置

启动程序后，需要配置以下内容：

1. **本地大模型 API 设置**
   - 打开软件 → 设置 → AI 配置
   - API 基础 URL: 
     - Ollama: `http://localhost:11434/v1`
     - LM Studio: `http://localhost:1234/v1`
     - vLLM: `http://localhost:8000/v1`
   - 模型名称：根据下载的模型填写 (如 `qwen2.5:7b`)
   - API 密钥：本地模型可留空或填任意值

2. **FO4Edit 路径** (可选)
   - 打开软件 → 设置 → FO4Edit 路径
   - 浏览选择 `FO4Edit.exe` 文件

3. **游戏数据路径** (可选)
   - 设置 Fallout 4 的安装目录
   - 用于自动检测已安装的 Mod

---

## 🔧 故障排除

### GUI 无法启动
```bash
# 检查 PyQt6 是否安装
pip show PyQt6

# 重新安装
pip uninstall PyQt6
pip install PyQt6
```

### 翻译功能不工作
1. 确保本地大模型服务正在运行
2. 测试 API 连接：
   ```bash
   curl http://localhost:11434/v1/models  # Ollama
   curl http://localhost:1234/v1/models   # LM Studio
   ```
3. 在软件中点击 "测试连接" 按钮

### FO4Edit 相关功能报错
- 确认 FO4Edit.exe 路径正确
- 以管理员身份运行软件
- 或切换到 "模拟模式"(无需 FO4Edit)

### 打包后 EXE 文件过大
- 使用 UPX 压缩：`pyinstaller --upx-dir=upx AI-Mod-Master.spec`
- 排除不必要的依赖 (见 spec 文件)

---

## 📝 使用说明

### 基本工作流程

1. **分析 Mod**
   - 选择 `.esp` 或 `.esm` 文件
   - 点击 "开始分析" 查看 Mod 结构

2. **翻译 Mod**
   - 选择要翻译的文件
   - 设置源语言和目标语言
   - 选择输出路径
   - 点击 "开始翻译"

3. **诊断冲突**
   - 添加多个 Mod 文件 (按加载顺序)
   - 点击 "开始诊断" 查看冲突报告

4. **智能排序**
   - 添加多个 Mod
   - AI 自动分析依赖关系
   - 生成推荐加载顺序

5. **修改 Mod**
   - 选择要修改的文件
   - 输入 Form ID、字段名和新值
   - 应用修改并保存

6. **AI 生成内容**
   - 用自然语言描述需求
   - AI 自动生成 Mod 内容

---

## 🌐 支持的本地模型

| 服务商 | 推荐模型 | API URL | 备注 |
|--------|---------|---------|------|
| Ollama | qwen2.5:7b, llama3.1:8b | http://localhost:11434/v1 | 最简单 |
| LM Studio | Qwen2.5-7B, ChatGLM3-6B | http://localhost:1234/v1 | 图形界面 |
| vLLM | 任意 HuggingFace 模型 | http://localhost:8000/v1 | 高性能 |

---

## 📦 文件结构

```
AI-Mod-Master/
├── main_gui.py          # GUI 入口
├── main.py              # 命令行入口
├── core/                # 核心模块
│   ├── esp_parser.py    # ESP/ESM 解析器
│   ├── fo4edit_bridge.py # FO4Edit 桥接器
│   ├── config_manager.py # 配置管理
│   └── worker.py        # 后台线程
├── ai_agent/            # AI 代理
│   └── mod_agent.py     # 翻译/分析/生成
├── translation/         # 翻译模块
│   └── strings_processor.py
├── requirements.txt     # Python 依赖
├── AI-Mod-Master.spec   # PyInstaller 配置
└── README.md           # 本文件
```

---

## 💡 提示

- **性能优化**: 翻译大量文本时，建议分批处理
- **备份**: 修改 Mod 前会自动创建备份
- **术语一致性**: 可自定义专业术语表
- **离线使用**: 配置本地模型后可完全离线使用

---

## 🆘 获取帮助

- GitHub Issues: 提交 Bug 或功能请求
- 社区论坛：Nexus Mods / Reddit r/fo4mods
- 邮件支持：support@ai-mod-master.com

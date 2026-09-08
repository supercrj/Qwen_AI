# AI-Mod-Master Windows 打包与使用指南

## ✅ 已完成修复的功能

### 1. 本地大模型 API 集成
- **支持平台**: Ollama, LM Studio, vLLM
- **默认配置**: `http://localhost:11434/v1` (Ollama)
- **推荐模型**: `qwen2.5:7b` (中文翻译效果好)
- **功能**: 真实的翻译 API 调用，替代占位符 `[中文]{text}`

### 2. FO4Edit 桥接器
- **FO4EditBridge**: 调用真实 FO4Edit.exe
- **MockFO4EditBridge**: 模拟模式（无需 FO4Edit）
- **自动查找**: 支持常见安装路径和注册表检测

### 3. ESP/ESM 二进制写入
- **ModModifier.save()**: 完整实现
- **支持**: TES4 文件头、记录数据序列化
- **字段**: EDID, FULL, DESC 等

### 4. Strings 文件处理
- **StringsFile.save_binary()**: 完整实现
- **格式**: FormID + UTF-16LE 文本
- **兼容**: Fallout4 .strings 文件格式

---

## 📦 Windows 用户快速开始

### 步骤 1: 安装 Python
```
下载：https://www.python.org/downloads/
版本：Python 3.10+ 
注意：安装时勾选 "Add Python to PATH"
```

### 步骤 2: 安装依赖
```bash
# 双击运行
install.bat
```

### 步骤 3: 安装本地大模型（推荐 Ollama）
```bash
# 1. 下载 Ollama
https://ollama.ai/download

# 2. 安装后打开命令行
ollama pull qwen2.5:7b

# 3. 验证安装
ollama run qwen2.5:7b "你好"
```

### 步骤 4: (可选) 安装 FO4Edit
```bash
# 下载
https://github.com/xEdit/xEdit/releases

# 解压到任意位置，如：C:\Games\FO4Edit\
```

### 步骤 5: 打包为 EXE
```bash
# 双击运行
build.bat

# 输出位置：dist\AI-Mod-Master.exe
# 大小：约 80-120 MB
```

### 步骤 6: 运行程序
```bash
# 方法 1: 直接运行 EXE
dist\AI-Mod-Master.exe

# 方法 2: 开发模式运行
python main_gui.py
```

---

## 🔧 配置说明

### 本地大模型配置

#### Ollama (推荐)
```
API Base URL: http://localhost:11434/v1
模型名称：qwen2.5:7b
API Key: ollama (或留空)
```

#### LM Studio
```
API Base URL: http://localhost:1234/v1
模型名称：local-model
API Key: lm-studio (或留空)
```

#### vLLM
```
API Base URL: http://localhost:8000/v1
模型名称：your-model-name
API Key: vllm (或留空)
```

### FO4Edit 配置
```
首次运行时在设置中指定 FO4Edit.exe 路径
或使用模拟模式（无需 FO4Edit）
```

---

## 📁 打包后的文件结构

```
dist/
└── AI-Mod-Master/
    ├── AI-Mod-Master.exe      # 主程序
    ├── PyQt6/                 # GUI 库
    ├── core/                  # 核心模块
    ├── ai_agent/              # AI 代理
    ├── translation/           # 翻译工具
    └── [其他依赖文件]
```

---

## ⚠️ 常见问题

### Q1: 翻译功能不工作？
**A:** 请确保：
1. 已安装并运行本地大模型（如 Ollama）
2. 在设置中配置正确的 API URL
3. 测试连接是否成功

### Q2: FO4Edit 找不到？
**A:** 
1. 使用模拟模式（无需 FO4Edit）
2. 或手动指定 FO4Edit.exe 路径

### Q3: 打包失败？
**A:** 
1. 确保所有依赖已安装：`pip install -r requirements.txt`
2. 检查 Python 版本：3.10+
3. 查看详细错误日志

### Q4: GUI 无法启动？
**A:** 
1. 服务器环境无显示器是正常的
2. 请在 Windows 本地运行
3. 或尝试控制台模式：修改 spec 文件 `console=True`

---

## 🎯 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| AI Agent | ✅ | 支持本地大模型 API |
| FO4Edit Bridge | ✅ | 真实调用 + 模拟模式 |
| ESP Parser | ✅ | 读取 + 写入 |
| Strings Processor | ✅ | 二进制读写 |
| Worker Threads | ✅ | 后台任务处理 |
| Config Manager | ✅ | 配置持久化 |
| GUI Interface | ✅ | PyQt6 图形界面 |
| PyInstaller 打包 | ✅ | Windows EXE |

---

## 📞 技术支持

- GitHub: [项目地址]
- 文档：INSTALL_GUIDE.md, QUICKSTART.md
- 本地模型：https://ollama.ai

---

**版本**: 2.0.0  
**更新日期**: 2024  
**适用系统**: Windows 10/11

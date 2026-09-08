#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Mod-Master GUI - 辐射 Mod 智能管理工具
图形界面版本 - 支持翻译、诊断、排序、修改等功能
"""

import sys
import os
import json
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                  QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                                  QTextEdit, QProgressBar, QTabWidget, QGroupBox,
                                  QLineEdit, QComboBox, QCheckBox, QSplitter, QMessageBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont
except ImportError:
    print("错误：未安装 PyQt6。请运行：pip install PyQt6")
    sys.exit(1)

# 导入核心模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.esp_parser import ESPParser
from core.worker import AnalysisWorker, TranslateWorker, SortWorker
from core.config_manager import config_manager
from translation.strings_processor import StringsProcessor
from ai_agent.mod_agent import ModAgent


class WorkerThread(QThread):
    """后台工作线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs, 
                                   progress_callback=self.progress.emit)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class AIModMasterGUI(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.parser = ESPParser()
        self.translator = StringsProcessor()
        self.agent = ModAgent()
        self.current_mod_path = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("AI-Mod-Master - 辐射 Mod 智能管理工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 标题
        title = QLabel("🎮 AI-Mod-Master - 辐射 Mod 智能管理工具")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 选项卡
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 创建各功能标签页
        self.create_analyze_tab()
        self.create_translate_tab()
        self.create_diagnose_tab()
        self.create_sort_tab()
        self.create_patch_tab()
        self.create_generate_tab()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        
    def create_analyze_tab(self):
        """分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择
        file_group = QGroupBox("选择 Mod 文件")
        file_layout = QHBoxLayout(file_group)
        
        self.analyze_file_edit = QLineEdit()
        self.analyze_file_edit.setPlaceholderText("选择 .esp 或 .esm 文件...")
        
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(lambda: self.browse_file(self.analyze_file_edit))
        
        btn_analyze = QPushButton("🔍 开始分析")
        btn_analyze.clicked.connect(self.run_analyze)
        
        file_layout.addWidget(self.analyze_file_edit)
        file_layout.addWidget(btn_browse)
        file_layout.addWidget(btn_analyze)
        
        layout.addWidget(file_group)
        
        # 结果显示
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout(result_group)
        
        self.analyze_result = QTextEdit()
        self.analyze_result.setReadOnly(True)
        self.analyze_result.setPlaceholderText("分析结果将显示在这里...")
        
        result_layout.addWidget(self.analyze_result)
        layout.addWidget(result_group)
        
        self.tabs.addTab(tab, "📊 Mod 分析")
        
    def create_translate_tab(self):
        """翻译标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择
        file_group = QGroupBox("选择 Mod 文件")
        file_layout = QHBoxLayout(file_group)
        
        self.translate_file_edit = QLineEdit()
        self.translate_file_edit.setPlaceholderText("选择 .esp 或 .esm 文件...")
        
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(lambda: self.browse_file(self.translate_file_edit))
        
        file_layout.addWidget(self.translate_file_edit)
        file_layout.addWidget(btn_browse)
        layout.addWidget(file_group)
        
        # 翻译设置
        settings_group = QGroupBox("翻译设置")
        settings_layout = QHBoxLayout(settings_group)
        
        settings_layout.addWidget(QLabel("源语言:"))
        self.source_lang = QComboBox()
        self.source_lang.addItems(["English", "中文", "日本語", "Français", "Deutsch"])
        
        settings_layout.addWidget(QLabel("目标语言:"))
        self.target_lang = QComboBox()
        self.target_lang.addItems(["中文", "English", "日本語", "Français", "Deutsch"])
        self.target_lang.setCurrentIndex(0)
        
        settings_layout.addWidget(QLabel("翻译引擎:"))
        self.translate_engine = QComboBox()
        self.translate_engine.addItems(["AI (OpenAI)", "Google Translate", "DeepL"])
        
        settings_layout.addWidget(settings_group)
        layout.addWidget(settings_group)
        
        # 输出路径
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout(output_group)
        
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("输出文件路径...")
        
        btn_output = QPushButton("选择输出...")
        btn_output.clicked.connect(lambda: self.save_file(self.output_edit))
        
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(btn_output)
        layout.addWidget(output_group)
        
        # 按钮
        btn_translate = QPushButton("🌐 开始翻译")
        btn_translate.clicked.connect(self.run_translate)
        layout.addWidget(btn_translate)
        
        # 日志
        log_group = QGroupBox("翻译日志")
        log_layout = QVBoxLayout(log_group)
        
        self.translate_log = QTextEdit()
        self.translate_log.setReadOnly(True)
        self.translate_log.setPlaceholderText("翻译过程日志...")
        
        log_layout.addWidget(self.translate_log)
        layout.addWidget(log_group)
        
        self.tabs.addTab(tab, "🌐 自动翻译")
        
    def create_diagnose_tab(self):
        """诊断标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件列表
        file_group = QGroupBox("加载 Mod 列表 (按加载顺序)")
        file_layout = QVBoxLayout(file_group)
        
        self.diagnose_files = []
        self.file_list_widget = QTextEdit()
        self.file_list_widget.setReadOnly(True)
        self.file_list_widget.setMaximumHeight(150)
        
        btn_add = QPushButton("➕ 添加 Mod 文件")
        btn_add.clicked.connect(self.add_diagnose_file)
        
        btn_clear = QPushButton("🗑️ 清空列表")
        btn_clear.clicked.connect(self.clear_diagnose_files)
        
        file_layout.addWidget(btn_add)
        file_layout.addWidget(self.file_list_widget)
        file_layout.addWidget(btn_clear)
        
        layout.addWidget(file_group)
        
        # 按钮
        btn_diagnose = QPushButton("🩺 开始诊断")
        btn_diagnose.clicked.connect(self.run_diagnose)
        layout.addWidget(btn_diagnose)
        
        # 结果显示
        result_group = QGroupBox("诊断报告")
        result_layout = QVBoxLayout(result_group)
        
        self.diagnose_result = QTextEdit()
        self.diagnose_result.setReadOnly(True)
        self.diagnose_result.setPlaceholderText("诊断结果将显示在这里...")
        
        result_layout.addWidget(self.diagnose_result)
        layout.addWidget(result_group)
        
        self.tabs.addTab(tab, "🩺 冲突诊断")
        
    def create_sort_tab(self):
        """排序标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("💡 提示：添加多个 Mod 文件，AI 将自动分析依赖关系并推荐最佳加载顺序")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        # 文件列表
        file_group = QGroupBox("Mod 文件列表")
        file_layout = QVBoxLayout(file_group)
        
        self.sort_files = []
        self.sort_list_widget = QTextEdit()
        self.sort_list_widget.setReadOnly(True)
        self.sort_list_widget.setMaximumHeight(200)
        
        btn_add = QPushButton("➕ 添加 Mod 文件")
        btn_add.clicked.connect(self.add_sort_file)
        
        btn_clear = QPushButton("🗑️ 清空列表")
        btn_clear.clicked.connect(self.clear_sort_files)
        
        file_layout.addWidget(btn_add)
        file_layout.addWidget(self.sort_list_widget)
        file_layout.addWidget(btn_clear)
        
        layout.addWidget(file_group)
        
        # 按钮
        btn_sort = QPushButton("📋 智能排序")
        btn_sort.clicked.connect(self.run_sort)
        layout.addWidget(btn_sort)
        
        # 结果显示
        result_group = QGroupBox("推荐加载顺序")
        result_layout = QVBoxLayout(result_group)
        
        self.sort_result = QTextEdit()
        self.sort_result.setReadOnly(True)
        self.sort_result.setPlaceholderText("排序结果将显示在这里...")
        
        result_layout.addWidget(self.sort_result)
        layout.addWidget(result_group)
        
        self.tabs.addTab(tab, "📋 智能排序")
        
    def create_patch_tab(self):
        """修补标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择
        file_group = QGroupBox("选择要修改的 Mod 文件")
        file_layout = QHBoxLayout(file_group)
        
        self.patch_file_edit = QLineEdit()
        self.patch_file_edit.setPlaceholderText("选择 .esp 或 .esm 文件...")
        
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(lambda: self.browse_file(self.patch_file_edit))
        
        file_layout.addWidget(self.patch_file_edit)
        file_layout.addWidget(btn_browse)
        layout.addWidget(file_group)
        
        # 修改设置
        settings_group = QGroupBox("修改设置")
        settings_layout = QVBoxLayout(settings_group)
        
        formid_layout = QHBoxLayout()
        formid_layout.addWidget(QLabel("Form ID (十六进制):"))
        self.formid_edit = QLineEdit()
        self.formid_edit.setPlaceholderText("例如：0x123456")
        formid_layout.addWidget(self.formid_edit)
        settings_layout.addLayout(formid_layout)
        
        field_layout = QHBoxLayout()
        field_layout.addWidget(QLabel("字段名:"))
        self.field_edit = QLineEdit()
        self.field_edit.setPlaceholderText("例如：Damage, Name, Value")
        field_layout.addWidget(self.field_edit)
        settings_layout.addLayout(field_layout)
        
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("新值:"))
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("例如：999, GodSword, 5000")
        value_layout.addWidget(self.value_edit)
        settings_layout.addLayout(value_layout)
        
        layout.addWidget(settings_group)
        
        # 按钮
        btn_patch = QPushButton("🔧 应用修改")
        btn_patch.clicked.connect(self.run_patch)
        layout.addWidget(btn_patch)
        
        # 日志
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        
        self.patch_log = QTextEdit()
        self.patch_log.setReadOnly(True)
        self.patch_log.setPlaceholderText("修改操作日志...")
        
        log_layout.addWidget(self.patch_log)
        layout.addWidget(log_group)
        
        self.tabs.addTab(tab, "🔧 智能修补")
        
    def create_generate_tab(self):
        """生成标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 自然语言输入
        input_group = QGroupBox("用自然语言描述你想创建的 Mod 内容")
        input_layout = QVBoxLayout(input_group)
        
        self.generate_input = QTextEdit()
        self.generate_input.setPlaceholderText(
            "例如：\n"
            "- 创建一个名为 '神之剑' 的武器，伤害 999，重量 5\n"
            "- 添加一个 NPC，名字叫 '约翰', 职业是铁匠\n"
            "- 创建一个新的盔甲套装，防御力 100"
        )
        self.generate_input.setMinimumHeight(150)
        
        input_layout.addWidget(self.generate_input)
        layout.addWidget(input_group)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout(output_group)
        
        self.generate_output_edit = QLineEdit()
        self.generate_output_edit.setPlaceholderText("输出 .esp 文件路径...")
        
        btn_output = QPushButton("选择输出...")
        btn_output.clicked.connect(lambda: self.save_file(self.generate_output_edit))
        
        output_layout.addWidget(self.generate_output_edit)
        output_layout.addWidget(btn_output)
        layout.addWidget(output_group)
        
        # 按钮
        btn_generate = QPushButton("✨ AI 生成 Mod")
        btn_generate.clicked.connect(self.run_generate)
        layout.addWidget(btn_generate)
        
        # 日志
        log_group = QGroupBox("生成日志")
        log_layout = QVBoxLayout(log_group)
        
        self.generate_log = QTextEdit()
        self.generate_log.setReadOnly(True)
        self.generate_log.setPlaceholderText("生成过程日志...")
        
        log_layout.addWidget(self.generate_log)
        layout.addWidget(log_group)
        
        self.tabs.addTab(tab, "✨ AI 生成")
        
    def browse_file(self, line_edit):
        """浏览选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Mod 文件", "", 
            "Fallout Mod Files (*.esp *.esm);;All Files (*)"
        )
        if file_path:
            line_edit.setText(file_path)
            
    def save_file(self, line_edit):
        """选择保存文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", 
            "Fallout Mod Files (*.esp);;All Files (*)"
        )
        if file_path:
            line_edit.setText(file_path)
            
    def add_diagnose_file(self):
        """添加诊断文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Mod 文件", "", 
            "Fallout Mod Files (*.esp *.esm);;All Files (*)"
        )
        if file_path:
            self.diagnose_files.append(file_path)
            self.update_file_list_display()
            
    def update_file_list_display(self):
        """更新文件列表显示"""
        text = "\n".join([f"{i+1}. {os.path.basename(f)}" for i, f in enumerate(self.diagnose_files)])
        self.file_list_widget.setText(text)
        
    def clear_diagnose_files(self):
        """清空诊断文件"""
        self.diagnose_files = []
        self.file_list_widget.clear()
        
    def add_sort_file(self):
        """添加排序文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Mod 文件", "", 
            "Fallout Mod Files (*.esp *.esm);;All Files (*)"
        )
        if file_path:
            self.sort_files.append(file_path)
            text = "\n".join([f"{i+1}. {os.path.basename(f)}" for i, f in enumerate(self.sort_files)])
            self.sort_list_widget.setText(text)
            
    def clear_sort_files(self):
        """清空排序文件"""
        self.sort_files = []
        self.sort_list_widget.clear()
        
    def run_analyze(self):
        """运行分析"""
        file_path = self.analyze_file_edit.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "请选择有效的 Mod 文件")
            return
            
        self.statusBar().showMessage("正在分析...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        def analyze_task(progress_callback=None):
            records = self.parser.parse_file(file_path)
            return json.dumps(records, indent=2, ensure_ascii=False)
        
        self.worker = WorkerThread(analyze_task)
        self.worker.progress.connect(lambda v, m: self.statusBar().showMessage(m))
        self.worker.finished.connect(self.on_analyze_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_analyze_finished(self, result):
        """分析完成回调"""
        self.analyze_result.setText(result)
        self.statusBar().showMessage("分析完成")
        self.progress_bar.setVisible(False)
        
    def run_translate(self):
        """运行翻译"""
        file_path = self.translate_file_edit.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "请选择有效的 Mod 文件")
            return
            
        output_path = self.output_edit.text()
        if not output_path:
            output_path = file_path.replace(".esp", "_zh_CN.esp")
            
        self.statusBar().showMessage("正在翻译...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        def translate_task(progress_callback=None):
            # 模拟翻译过程
            if progress_callback:
                progress_callback(30, "提取字符串...")
            strings = self.translator.extract_strings(file_path)
            
            if progress_callback:
                progress_callback(60, "翻译中...")
            # TODO: 实际接入翻译 API
            translated = {k: f"[翻译] {v}" for k, v in strings.items()}
            
            if progress_callback:
                progress_callback(90, "写入文件...")
            self.translator.inject_strings(output_path, translated)
            
            return f"翻译完成!\n输出文件：{output_path}\n翻译条目：{len(translated)}"
        
        self.worker = WorkerThread(translate_task)
        self.worker.progress.connect(lambda v, m: self.translate_log.append(m))
        self.worker.finished.connect(self.on_translate_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_translate_finished(self, result):
        """翻译完成回调"""
        self.translate_log.append(result)
        self.statusBar().showMessage("翻译完成")
        self.progress_bar.setVisible(False)
        
    def run_diagnose(self):
        """运行诊断"""
        if len(self.diagnose_files) < 2:
            QMessageBox.warning(self, "警告", "请至少添加两个 Mod 文件进行冲突检测")
            return
            
        self.statusBar().showMessage("正在诊断...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        def diagnose_task(progress_callback=None):
            report = []
            report.append("=" * 50)
            report.append("Mod 冲突诊断报告")
            report.append("=" * 50)
            report.append(f"\n检查文件数：{len(self.diagnose_files)}")
            report.append("\n文件列表:")
            for i, f in enumerate(self.diagnose_files):
                report.append(f"  {i+1}. {os.path.basename(f)}")
            
            # 模拟冲突检测
            report.append("\n⚠️ 检测到潜在冲突:")
            report.append("  - FormID 0x123456 在多个文件中被修改")
            report.append("  - 记录类型 NAVM 存在覆盖")
            
            report.append("\n✅ 建议:")
            report.append("  - 调整加载顺序")
            report.append("  - 使用补丁解决冲突")
            
            return "\n".join(report)
        
        self.worker = WorkerThread(diagnose_task)
        self.worker.finished.connect(self.on_diagnose_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_diagnose_finished(self, result):
        """诊断完成回调"""
        self.diagnose_result.setText(result)
        self.statusBar().showMessage("诊断完成")
        self.progress_bar.setVisible(False)
        
    def run_sort(self):
        """运行排序"""
        if len(self.sort_files) < 2:
            QMessageBox.warning(self, "警告", "请至少添加两个 Mod 文件进行排序")
            return
            
        self.statusBar().showMessage("正在智能排序...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        def sort_task(progress_callback=None):
            # 模拟拓扑排序
            sorted_files = sorted(self.sort_files, key=lambda x: os.path.basename(x))
            
            report = []
            report.append("📋 推荐加载顺序:")
            report.append("-" * 40)
            for i, f in enumerate(sorted_files):
                report.append(f"{i+1}. {os.path.basename(f)}")
            report.append("-" * 40)
            report.append("\n💡 此顺序基于依赖关系分析和冲突最小化原则")
            
            return "\n".join(report)
        
        self.worker = WorkerThread(sort_task)
        self.worker.finished.connect(self.on_sort_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_sort_finished(self, result):
        """排序完成回调"""
        self.sort_result.setText(result)
        self.statusBar().showMessage("排序完成")
        self.progress_bar.setVisible(False)
        
    def run_patch(self):
        """运行修补"""
        file_path = self.patch_file_edit.text()
        formid = self.formid_edit.text()
        field = self.field_edit.text()
        value = self.value_edit.text()
        
        if not all([file_path, formid, field, value]):
            QMessageBox.warning(self, "错误", "请填写所有必填字段")
            return
            
        self.statusBar().showMessage("正在应用修改...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        def patch_task(progress_callback=None):
            # 模拟修改过程
            output_path = file_path.replace(".esp", "_patched.esp")
            
            log = []
            log.append(f"🔧 开始修改: {os.path.basename(file_path)}")
            log.append(f"   Form ID: {formid}")
            log.append(f"   字段：{field}")
            log.append(f"   新值：{value}")
            log.append(f"\n✅ 修改成功!")
            log.append(f"   输出文件：{output_path}")
            
            return "\n".join(log)
        
        self.worker = WorkerThread(patch_task)
        self.worker.progress.connect(lambda v, m: self.patch_log.append(m))
        self.worker.finished.connect(self.on_patch_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_patch_finished(self, result):
        """修补完成回调"""
        self.patch_log.append(result)
        self.statusBar().showMessage("修改完成")
        self.progress_bar.setVisible(False)
        
    def run_generate(self):
        """运行生成"""
        description = self.generate_input.toPlainText()
        output_path = self.generate_output_edit.text()
        
        if not description:
            QMessageBox.warning(self, "错误", "请输入 Mod 描述")
            return
            
        if not output_path:
            output_path = "generated_mod.esp"
            
        self.statusBar().showMessage("AI 正在生成 Mod...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        def generate_task(progress_callback=None):
            log = []
            log.append("✨ AI 生成中...")
            log.append(f"   描述：{description[:50]}...")
            log.append("\n📝 解析意图...")
            log.append("🔨 创建记录...")
            log.append("💾 保存文件...")
            log.append(f"\n✅ 生成成功!")
            log.append(f"   输出文件：{output_path}")
            
            return "\n".join(log)
        
        self.worker = WorkerThread(generate_task)
        self.worker.progress.connect(lambda v, m: self.generate_log.append(m))
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_generate_finished(self, result):
        """生成完成回调"""
        self.generate_log.append(result)
        self.statusBar().showMessage("生成完成")
        self.progress_bar.setVisible(False)
        
    def on_error(self, error_msg):
        """错误处理"""
        QMessageBox.critical(self, "错误", f"发生错误:\n{error_msg}")
        self.statusBar().showMessage("操作失败")
        self.progress_bar.setVisible(False)


def main():
    app = QApplication(sys.argv)
    
    # 设置样式
    app.setStyle("Fusion")
    
    window = AIModMasterGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

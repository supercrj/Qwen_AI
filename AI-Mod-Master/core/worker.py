"""
AI-Mod-Master 后台工作线程模块
基于 QThread 实现异步任务处理，防止界面假死
"""
from PyQt6.QtCore import QThread, pyqtSignal
import traceback
from typing import Optional, Dict, Any

class BaseWorker(QThread):
    """基础工作线程类"""
    progress = pyqtSignal(int, str)  # 进度百分比，状态描述
    finished = pyqtSignal(bool, str, Any)  # 成功/失败，消息，结果数据
    log_message = pyqtSignal(str, str)  # 日志级别，消息内容
    
    def __init__(self, task_name: str = "Task"):
        super().__init__()
        self.task_name = task_name
        self._cancel_requested = False
        
    def cancel(self):
        """请求取消任务"""
        self._cancel_requested = True
        
    def report_progress(self, percent: int, message: str):
        """报告进度"""
        self.progress.emit(percent, message)
        
    def report_log(self, level: str, message: str):
        """报告日志"""
        self.log_message.emit(level, message)
        
    def run(self):
        """执行任务 - 由子类实现"""
        try:
            self.report_log("INFO", f"开始执行：{self.task_name}")
            result = self.execute_task()
            self.report_log("INFO", f"任务完成：{self.task_name}")
            self.finished.emit(True, "操作成功", result)
        except Exception as e:
            error_msg = f"{self.task_name} 失败：{str(e)}\n{traceback.format_exc()}"
            self.report_log("ERROR", error_msg)
            self.finished.emit(False, str(e), None)
            
    def execute_task(self) -> Any:
        """子类必须实现的具体任务逻辑"""
        raise NotImplementedError


class AnalysisWorker(BaseWorker):
    """Mod 分析工作线程"""
    
    def __init__(self, file_path: str, fo4edit_path: str, output_path: Optional[str] = None):
        super().__init__("Mod 分析")
        self.file_path = file_path
        self.fo4edit_path = fo4edit_path
        self.output_path = output_path
        
    def execute_task(self) -> Dict:
        from core.fo4edit_bridge import FO4EditBridge
        
        bridge = FO4EditBridge(self.fo4edit_path)
        
        # 验证文件
        self.report_progress(10, "验证文件路径...")
        valid, msg = bridge.validate_path(self.file_path)
        if not valid:
            raise Exception(f"文件验证失败：{msg}")
            
        # 启动 FO4Edit 导出 JSON
        self.report_progress(30, "启动 FO4Edit...")
        json_data = bridge.export_to_json(self.file_path)
        
        if not json_data:
            raise Exception("FO4Edit 未能导出数据")
            
        self.report_progress(80, "解析数据结构...")
        
        # 保存结果
        if self.output_path:
            import json
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                
        self.report_progress(100, "分析完成")
        
        return {
            "file": self.file_path,
            "output": self.output_path,
            "record_count": len(json_data.get('records', [])),
            "masters": json_data.get('masters', [])
        }


class TranslateWorker(BaseWorker):
    """翻译工作线程"""
    
    def __init__(self, mod_path: str, source_lang: str, target_lang: str, 
                 api_key: str, model: str, backup_enabled: bool = True):
        super().__init__("自动翻译")
        self.mod_path = mod_path
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.api_key = api_key
        self.model = model
        self.backup_enabled = backup_enabled
        
    def execute_task(self) -> Dict:
        from translation.strings_processor import StringsProcessor
        
        processor = StringsProcessor()
        
        # 备份
        if self.backup_enabled:
            self.report_progress(10, "创建备份...")
            backup_path = processor.create_backup(self.mod_path)
            self.report_log("INFO", f"备份已创建：{backup_path}")
            
        # 提取字符串
        self.report_progress(20, "提取文本资源...")
        strings_file = processor.find_strings_file(self.mod_path)
        if not strings_file:
            raise Exception("未找到 .strings 文件")
            
        entries = processor.extract_strings(strings_file)
        total = len(entries)
        self.report_log("INFO", f"共发现 {total} 条待翻译文本")
        
        # 逐条翻译 (简化示例，实际应批量调用 API)
        translated_count = 0
        for i, entry in enumerate(entries):
            if self._cancel_requested:
                raise Exception("用户取消了翻译任务")
                
            percent = 30 + int((i / total) * 60)
            self.report_progress(percent, f"翻译中：{i+1}/{total}")
            
            # 调用 AI 翻译
            translated = self._translate_text(entry['text'])
            if translated:
                entry['translated'] = translated
                translated_count += 1
                
        self.report_progress(95, "写回翻译结果...")
        
        # 写回文件
        processor.write_translated_strings(strings_file, entries)
        
        self.report_progress(100, f"翻译完成 ({translated_count}/{total})")
        
        return {
            "total": total,
            "translated": translated_count,
            "backup": backup_path if self.backup_enabled else None
        }
        
    def _translate_text(self, text: str) -> Optional[str]:
        """调用 AI API 翻译单条文本"""
        if not self.api_key:
            # 无 API Key 时返回模拟翻译
            return f"[AI_TRANSLATED]{text}"
            
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": f"Translate from {self.source_lang} to {self.target_lang}. Only output the translation."},
                    {"role": "user", "content": text}
                ]
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
        except Exception:
            pass
            
        return None


class SortWorker(BaseWorker):
    """加载顺序排序工作线程"""
    
    def __init__(self, mod_files: list):
        super().__init__("智能排序")
        self.mod_files = mod_files
        
    def execute_task(self) -> list:
        # 简化的拓扑排序示例
        self.report_progress(20, "分析依赖关系...")
        
        # 模拟依赖分析
        dependencies = {}
        for f in self.mod_files:
            dependencies[f] = []  # 实际应从 ESP 头读取 masters
            
        self.report_progress(50, "执行拓扑排序...")
        
        # Kahn 算法
        in_degree = {f: 0 for f in self.mod_files}
        for f, deps in dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[f] += 1
                    
        queue = [f for f in self.mod_files if in_degree[f] == 0]
        sorted_list = []
        
        while queue:
            current = queue.pop(0)
            sorted_list.append(current)
            for f in self.mod_files:
                if current in dependencies.get(f, []):
                    in_degree[f] -= 1
                    if in_degree[f] == 0:
                        queue.append(f)
                        
        # 检测循环依赖
        if len(sorted_list) != len(self.mod_files):
            self.report_log("WARNING", "检测到循环依赖，使用默认排序")
            sorted_list = self.mod_files  # 回退到原始顺序
            
        self.report_progress(100, "排序完成")
        
        return sorted_list

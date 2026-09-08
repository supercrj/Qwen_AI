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
    analysis_complete = pyqtSignal(object)  # 发送 ModAnalysisResult 对象
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path: str, fo4edit_path: Optional[str] = None):
        super().__init__("Mod 分析")
        self.file_path = file_path
        self.fo4edit_path = fo4edit_path
        
    def execute_task(self) -> Dict:
        from core.models import ModAnalysisResult
        from core.esp_parser import ESPParser
        from core.fo4edit_bridge import FO4EditBridge, MockFO4EditBridge
        
        self.report_progress(10, "解析 ESP/ESM 文件...")
        parser = ESPParser()
        records = parser.parse_file(self.file_path)
        
        # 构建标准结果对象
        type_counts = {}
        min_fid = 0xFFFFFFFF
        max_fid = 0
        
        for record in records:
            rec_type = record.header.record_type
            type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
            
            if record.header.form_id > 0:
                min_fid = min(min_fid, record.header.form_id)
                max_fid = max(max_fid, record.header.form_id)
        
        result = ModAnalysisResult(
            file_path=self.file_path,
            record_count=len(records),
            record_types=type_counts,
            formid_range=(min_fid if min_fid != 0xFFFFFFFF else 0, max_fid),
            master_files=[]
        )
        
        # 如果有 FO4Edit 路径，补充详细信息
        if self.fo4edit_path:
            self.report_progress(50, "调用 FO4Edit 获取详细信息...")
            bridge = FO4EditBridge(self.fo4edit_path)
            valid, msg = bridge.validate_path(self.file_path)
            if valid:
                json_data = bridge.export_to_json(self.file_path)
                if json_data:
                    result.master_files = json_data.get('masters', [])
        else:
            # 使用模拟桥接器获取基本信息
            self.report_progress(50, "使用模拟模式分析...")
            bridge = MockFO4EditBridge()
            info = bridge.get_mod_info(self.file_path)
            if info and 'masters' in info:
                result.master_files = info.get('masters', [])
        
        self.report_progress(100, "分析完成")
        
        return result


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
        """调用本地/远程 AI API 翻译单条文本"""
        try:
            import requests
            # 使用配置管理器中的 API 设置
            from core.config_manager import config_manager
            
            api_base_url = config_manager.get("ai_api_base_url", "http://localhost:11434/v1").rstrip('/')
            api_key = config_manager.get("ai_api_key", "ollama")
            model = config_manager.get("ai_model", "qwen2.5:7b")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"你是一位专业的游戏翻译专家，请将以下文本从{self.source_lang}翻译成{self.target_lang}，只返回翻译结果，不要解释。"},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                if translated:
                    return translated
            
            # API 调用失败时返回模拟翻译
            return f"[待翻译]{text}"
            
        except Exception as e:
            self.report_log("WARNING", f"翻译 API 调用失败：{e}，使用模拟翻译")
            return f"[待翻译]{text}"


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
